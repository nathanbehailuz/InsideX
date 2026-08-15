"""
Modal deployment for OpenSignal: FastAPI web + scrape/train jobs on a shared Volume.

Deploy:
  modal deploy modal_app.py

One-off jobs (after deploy, or via `modal run`):
  modal run modal_app.py::scrape_update
  modal run modal_app.py::train_model

Then set ALLOWED_HOSTS to your Vercel origin(s), e.g.:
  modal secret create insidex-cors ALLOWED_HOSTS=https://your-app.vercel.app
  # and attach secret=modal.Secret.from_name("insidex-cors") on the web function
"""

from __future__ import annotations

import os
from pathlib import Path

import modal

APP_NAME = "insidex"
DATA_DIR = "/data"
DB_PATH = f"{DATA_DIR}/insider_trading.db"
ML_DIR = f"{DATA_DIR}/ml"
APP_ROOT = "/app"

# Paths relative to this file (repo root)
_REPO_ROOT = Path(__file__).resolve().parent

volume = modal.Volume.from_name("insidex-data", create_if_missing=True)

# Local sources are added last (Modal requirement). PYTHONPATH=/app so
# `backend.app.*`, `database`, and `scrape` imports resolve.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgomp1")  # xgboost / sklearn runtime
    .pip_install_from_requirements(str(_REPO_ROOT / "requirements.txt"))
    .env(
        {
            "PYTHONPATH": APP_ROOT,
            "DATABASE_PATH": DB_PATH,
            "ML_ARTIFACTS_DIR": ML_DIR,
            "ML_MODEL_PATH": f"{ML_DIR}/model.joblib",
            "ML_FEATURES_PATH": f"{ML_DIR}/features.yaml",
            # Override after Vercel deploy; regex covers *.vercel.app previews.
            # Avoid backslashes — Modal image .env unescaping rejects \. sequences.
            "ALLOWED_HOSTS": "http://localhost:3000,http://127.0.0.1:3000",
            "ALLOWED_ORIGIN_REGEX": "https://.*[.]vercel[.]app",
        }
    )
    .add_local_dir(
        str(_REPO_ROOT),
        remote_path=APP_ROOT,
        ignore=[
            "**/frontend/**",
            "**/.git/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.venv/**",
            "**/venv/**",
            "**/.next/**",
            "**/logs/**",
            "**/*.db",
            "**/.cursor/**",
        ],
    )
)

app = modal.App(APP_NAME, image=image)

_volume_mount = {DATA_DIR: volume}


def _ensure_data_dirs() -> None:
    Path(ML_DIR).mkdir(parents=True, exist_ok=True)
    Path(f"{DATA_DIR}/logs").mkdir(parents=True, exist_ok=True)


@app.function(
    volumes=_volume_mount,
    timeout=60 * 30,
    memory=2048,
)
@modal.concurrent(max_inputs=20)
@modal.asgi_app()
def api():
    """Serve the FastAPI app; SQLite + ML artifacts live on the Volume."""
    _ensure_data_dirs()
    # Settings are read at import from env set on the image
    from backend.app.main import app as fastapi_app

    return fastapi_app


@app.function(
    volumes=_volume_mount,
    timeout=60 * 60 * 6,
    memory=4096,
    schedule=modal.Cron("0 6 * * *"),  # daily 06:00 UTC
)
def scrape_update():
    """Incremental scrape (`scrape.py --s_type update`) into the Volume DB."""
    _ensure_data_dirs()
    os.environ["DATABASE_PATH"] = DB_PATH
    # scrape.py writes ./logs — keep them on the Volume
    os.chdir(DATA_DIR)

    import scrape as scrape_mod

    scrape_mod.DB_PATH = DB_PATH
    scrape_mod.scraper("update")
    volume.commit()
    return {"status": "ok", "database": DB_PATH}


@app.function(
    volumes=_volume_mount,
    timeout=60 * 60 * 2,
    memory=8192,
    schedule=modal.Cron("0 8 * * 0"),  # weekly Sunday 08:00 UTC
)
def train_model():
    """Train signal model and write joblib artifacts under /data/ml."""
    import numpy as np

    from backend.app.ml.train import MLTrainer

    _ensure_data_dirs()
    if not Path(DB_PATH).exists():
        return {"status": "skipped", "reason": f"missing database at {DB_PATH}"}

    np.random.seed(42)
    trainer = MLTrainer(db_path=DB_PATH, artifacts_dir=ML_DIR)
    df = trainer.load_data()
    if len(df) < 100:
        return {"status": "skipped", "reason": f"too few rows ({len(df)})"}

    X, y = trainer.prepare_features_and_labels(df, horizon_days=20, threshold_pct=5.0)
    if X.empty or len(y.unique()) < 2:
        return {"status": "skipped", "reason": "insufficient labeled data"}

    X_train, X_test, y_train, y_test = trainer.split_data(X, y, random_state=42)
    trainer.train_model(X_train, y_train, model_type="random_forest")
    metrics = trainer.evaluate_model(X_test, y_test)
    trainer.save_model()
    volume.commit()
    return {"status": "ok", "metrics": metrics, "artifacts_dir": ML_DIR}


@app.local_entrypoint()
def main(action: str = "scrape"):
    """
    Local CLI helper:
      modal run modal_app.py --action scrape
      modal run modal_app.py --action train
    """
    if action == "scrape":
        print(scrape_update.remote())
    elif action == "train":
        print(train_model.remote())
    else:
        raise SystemExit(f"Unknown action {action!r}; use scrape or train")
