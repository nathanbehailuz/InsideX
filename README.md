# InsideX - Insider Trading Signal Platform

## Overview

InsideX is an AI-powered platform that analyzes SEC insider trading filings to generate actionable trading signals. The platform combines real-time data processing with machine learning to identify potentially profitable insider trading patterns.

**Key Features:**
- 🧠 **AI-Powered Signals**: Machine learning models trained on historical insider trading data
- 📊 **Real-time Analytics**: Live tracking of SEC Form 4 filings and insider activity
- 📈 **Performance Tracking**: Historical success rates and insider performance metrics
- 🎯 **Smart Rankings**: Confidence-based signal scoring with detailed explanations
- 📱 **Modern Web Interface**: Responsive React/Next.js frontend with professional UI

## Architecture

This is a full-stack application with three main components:

1. **Backend API** (FastAPI + SQLite)
2. **ML Pipeline** (scikit-learn + feature engineering)
3. **Frontend Web App** (Next.js + TypeScript + Tailwind CSS)

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- npm or yarn

### 1. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Endpoints**: http://localhost:8000/api/v1/
- **Interactive Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz

### 2. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

The frontend will be available at:
- **Web Application**: http://localhost:3000

### 3. Data Collection (Optional)

To populate the database with insider trading data:

```bash
# Run the scraper to collect SEC data
python scrape.py --s_type all
```

### 4. ML Model Training (Optional)

To train the machine learning model:

```bash
cd backend
python -m app.ml.train --model_type random_forest --horizon_days 20 --threshold_pct 5.0
```

## API Documentation

### Core Endpoints

#### Trades
- `GET /api/v1/trades` - Get trades with filtering and pagination
- `GET /api/v1/trades/stats` - Database statistics

#### Companies & Insiders
- `GET /api/v1/companies/{ticker}` - Company information and recent activity
- `GET /api/v1/insiders/{name}` - Insider profile and trading history

#### AI Signals
- `GET /api/v1/signals/top` - Top-ranked trading signals
- `POST /api/v1/signals/score` - Score specific tickers or filings
- `GET /api/v1/signals/model-info` - ML model information

### Example API Usage

```bash
# Get top signals
curl "http://localhost:8000/api/v1/signals/top?window_days=30&limit=10"

# Get recent trades for Apple
curl "http://localhost:8000/api/v1/trades?ticker=AAPL&limit=20"

# Get company information
curl "http://localhost:8000/api/v1/companies/AAPL"
```

## Web Interface

### Pages

1. **Landing Page** (`/`)
   - Marketing page with feature overview
   - Call-to-action buttons to dashboard

2. **Dashboard** (`/dashboard`)
   - Key performance indicators (KPIs)
   - Database statistics
   - Top trading signals
   - Recent activity overview

3. **Signals** (`/signals`)
   - AI-generated trading signals
   - Filtering by confidence and time window
   - Detailed explanations for each signal

### Navigation
- **Dashboard**: Overview and KPIs
- **Signals**: AI-powered trading signals
- **Companies**: Company profiles and activity (planned)
- **Insiders**: Insider profiles and performance (planned)
- **Trades**: Raw trade data with filtering (planned)

## Machine Learning Pipeline

### Feature Engineering

The ML pipeline extracts 25+ features from insider trading data:

**Basic Features:**
- Trade value and log-transformed value
- Ownership change ratios
- Buy/sell indicators

**Categorical Features:**
- Trade flags (Disposition, Multiple, Acquisition, Stock-based)
- Insider roles (CEO, CFO, Director, 10% Owner)

**Temporal Features:**
- Filing delays
- Day of week, month, quarter patterns

**Aggregate Features:**
- Insider historical performance
- Company trading patterns
- Success rates and activity levels

**Market Context:**
- Price momentum indicators
- Volatility proxies

### Model Training

```bash
# Train with custom parameters
python -m app.ml.train \
  --model_type random_forest \
  --horizon_days 20 \
  --threshold_pct 5.0 \
  --seed 42

# Evaluate model performance
python -m app.ml.evaluate --artifact app/ml/artifacts/model.joblib
```

### Signal Generation

The system generates signals using:
1. **ML Predictions**: When a trained model is available
2. **Heuristic Fallback**: Rule-based scoring for reliability
3. **Confidence Scoring**: High/Medium/Low confidence levels
4. **Explanations**: Human-readable reasons for each signal

## Directory Structure

```
InsideX/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # REST API routes
│   │   ├── core/              # Configuration
│   │   ├── models/            # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── ml/                # ML pipeline
│   │       ├── features.py    # Feature engineering
│   │       ├── train.py       # Model training
│   │       └── artifacts/     # Model artifacts
│   └── requirements.txt
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # Pages (App Router)
│   │   ├── components/       # UI components
│   │   └── lib/              # Utilities & API client
│   ├── package.json
│   └── tailwind.config.js
├── database.py               # Database interface
├── scrape.py                 # Data collection
├── analyze.py                # Data analysis
└── README.md
```

## Configuration

### Backend Configuration

Environment variables can be set in `.env`:
```bash
DATABASE_PATH=../../insider_trading.db
ML_MODEL_PATH=app/ml/artifacts/model.joblib
```

### Frontend Configuration

Set API URL in `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Development

### Backend Development
```bash
cd backend
source ../venv/bin/activate
python -m uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build
npm start

# Backend (use production ASGI server)
pip install gunicorn
gunicorn -k uvicorn.workers.UvicornWorker app.main:app
```

## Data Sources

- **SEC EDGAR Database**: Insider trading filings (Form 4)
- **OpenInsider.com**: Aggregated insider trading data
- **Historical Price Data**: For performance calculations (future integration)

## Deployment

### Docker Support (Future)
```dockerfile
# Example Dockerfile structure
FROM python:3.13
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment Options
- **Vercel**: Frontend deployment
- **Railway/Render**: Backend API deployment
- **AWS/GCP/Azure**: Full infrastructure deployment

## Monitoring & Observability

- Health checks at `/healthz`
- Request/response logging in development
- Model performance tracking
- API usage analytics (future)

## Legal & Compliance

⚠️ **Important Disclaimer**: This platform is for educational and research purposes only. 

- All data is sourced from public SEC filings
- Not financial advice or investment recommendations
- Users should conduct their own research
- Comply with all applicable securities laws
- Past performance doesn't guarantee future results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please ensure compliance with all applicable laws and regulations when using insider trading data.

## Support

For questions or issues:
- Check the API documentation at `/docs`
- Review the implementation summary in `IMPLEMENTATION_SUMMARY.md`
- Open an issue on the repository

---

**Built with ❤️ for educational purposes** | **Not investment advice** | **Use responsibly**