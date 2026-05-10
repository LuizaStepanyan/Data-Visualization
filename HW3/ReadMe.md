# Jordan Cars Market 2026 — Dashboard

A 3-page interactive Dash dashboard for the Jordan Cars Market 2026 dataset.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:8050 in your browser.

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Pricing Overview | `/` | Price distributions, Jordan vs USA, median/mean toggle, percentiles |
| Fuel & Brands | `/fuel-brands` | Fuel transition area chart, brand bar & bubble chart |
| Geography | `/geography` | Choropleth map, city listings & price bars, box plots |

## Instructor Feedback Addressed

- **Log scale for bubble size** — Geography page has a Linear/Log toggle for map bubbles; Fuel & Brands bubble chart uses `log1p` scaling by default.
- **Hover on polygons, no purple dots** — The choropleth uses `go.Choropleth` with `customdata` hover so tooltips appear directly on governorate polygons. The scatter layer is for city-level detail and uses neutral styling.
- **Simplified Brand × Year chart** — Added a multi-select brand filter so users can focus on one or a few brands instead of seeing all at once. Dropdown also controls which brands appear.
- **Single color for bar charts** — Brand bar chart uses a single blue gradient colorscale, not a multi-color palette.
- **Amman vs Oman label fix** — City bar chart pulls directly from the `City` column (cleaned `str.split(",").str[0].str.strip()`), avoiding the label artifact.
- **Median + Mean comparison** — All pages expose a stat toggle (median / mean). The box plot on Geography shows both (box line = median, dot = mean via `boxmean=True`).

## Dataset

- Jordan: [alzyood95/jordan-cars-market-2026](https://www.kaggle.com/datasets/alzyood95/jordan-cars-market-2026) (auto-downloaded via `kagglehub`)
- USA reference data used in Assignment 2 is not included in the dashboard to keep load times fast; the pricing page focuses on Jordan with stat annotations.