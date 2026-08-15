# OpenSignal — Design Brief for Mockups

Use this as the product and IA brief for UI mockups. Live reference: https://insidex-steel.vercel.app

---

## Product

**Name:** OpenSignal  
**Logo mark:** `OS` monogram in a rounded square  
**One-liner:** An AI platform that analyzes financial disclosures and transactions from influential decision-makers—including government officials and corporate executives—to identify market signals.

**What it does:** Surfaces ranked market signals from public filings and trades made by executives and other influential people. Users browse signals, companies, people, and raw trades in one app.

**Audience:** Retail investors, researchers, and analysts who want a clear read on “who’s buying/selling what, and how strong the signal is.”

**Tone:** Professional, calm, data-forward. Confident but not hypey. Not a casino trading app; not a dense Bloomberg terminal.

---

## Global chrome (every app page)

- Top nav with brand (OS + “OpenSignal”) left
- Links: **Dashboard · Signals · Companies · People · Trades**
- Active link clearly indicated
- Content width ~max 7xl, comfortable padding
- Light theme preferred for mockups (white / soft gray canvas)

---

## Screens to mock

### 1. Landing (`/`)

**Job:** Instant brand + positioning; one primary CTA into the product.

**Hierarchy (first viewport):**
1. Brand: OpenSignal (hero-level)
2. Positioning sentence (the one-liner above)
3. Primary CTA: “View Signals Dashboard”
4. Secondary CTA: “Explore Market Signals”

**Below fold (optional):** three feature blocks — Disclosure Tracking · AI-Powered Signals · Smart Rankings

**Avoid on first viewport:** stats grids, tables, schedules, promo chips.

---

### 2. Dashboard (`/dashboard`)

**Job:** At-a-glance health of the market + top signals.

**Layout:**
- Page title: Dashboard  
- Subcopy: overview of recent activity and top signals
- **4 metric cards** in a row (desktop): e.g. trades (7d), trades (30d), buy/sell mix, avg signal score
- **Top Signals** list/table (ticker, score/confidence, reasons, trade value)
- **Database / coverage** summary (total records, companies, people, date range)

---

### 3. Signals (`/signals`)

**Job:** Browse AI-ranked trading signals.

**Layout:**
- Title: Trading Signals  
- Subcopy: AI-ranked by confidence and potential
- **Filters bar:** time window (e.g. 7 / 30 / 90 days), confidence (All / High / Medium / Low)
- **Results:** ranked cards or table rows showing:
  - Ticker
  - Score / confidence badge (high / medium / low)
  - Short reason chips or bullets
  - Optional: person name, trade date, trade value
- Empty state: “No signals found” with nudge to adjust filters

---

### 4. Companies (`/companies`)

**Job:** Find a ticker and see its recent insider activity.

**Layout:**
- Title: Companies  
- Search: ticker input + search
- **List:** most active companies (ticker, name, recent trades, last trade date)
- **Detail (when ticker selected):** company header + summary stats + recent trades table  
  - Link out to Trades filtered by ticker

---

### 5. People (`/insiders` — labeled “People” in nav)

**Job:** Profiles of decision-makers (executives / filers), not “celebrity gossip.”

**Layout:**
- Title: People  
- Subcopy: Influential decision-makers ranked by disclosure and trading activity
- **Filters:** name search + sort (Most active / Performance / Most recent)
- **List table:** name, trades, companies, avg value, 30d activity, last trade, success
- **Profile panel (when person selected):** name, trade counts, bought/sold, avg value, recent trades table

---

### 6. Trades (`/trades`)

**Job:** Raw searchable ledger of filings/transactions.

**Layout:**
- Title: Trades (or “Market Trades”)
- **3 summary stats** on top (e.g. total records, companies, people)
- **Filter form:** ticker, person name, trade type (buy/sell), date range, min value
- **Paginated table:** date, ticker, person, title/role, type badge, qty, value, performance if available
- Purchase = positive/green badge; Sale = negative/red badge

---

## Data language (use consistently)

| Concept | UI word |
|--------|---------|
| Product | OpenSignal |
| Ranked insights | Signals |
| Issuers | Companies |
| Decision-makers / filers | People |
| Individual filings | Trades |
| Confidence | High / Medium / Low |
| Trade direction | Purchase / Sale (or Buy / Sell) |

Avoid calling the product “InsideX.” Prefer “People” over “Insiders” in user-facing chrome.

---

## Visual direction (for Stitch)

- **Brand first** on the landing page; product name should dominate the first viewport
- Clean light UI; blue as primary accent (current live site uses a strong blue CTA)
- Tables and filters are core patterns — design those carefully
- Badges for confidence and buy/sell should be scannable
- Desktop-first mockups OK; also show one mobile nav / stacked filters variant if possible
- Prefer expressive typography over default Inter/Roboto stacks if Stitch allows font choice
- Soft atmospheric background on landing only; app pages can be quieter (gray canvas + white panels)

---

## Sample content (for realistic mockups)

**Signals row examples:**
- PFE · High · “Large purchase · Director-level” · $2.4M  
- INTC · Medium · “Cluster buying · 30d activity” · $890K  

**People examples:**
- Horizon Kinetics Asset Management LLC  
- Corporate CEOs / CFOs / Directors as individual names  

**Disclaimer (footer-friendly):** Data from public financial disclosures. Not investment advice.

---

## Mockup priority order

1. Landing  
2. Signals  
3. Dashboard  
4. People  
5. Companies  
6. Trades  

Deliver desktop frames for all six; add mobile for Landing + Signals if time-boxed.
