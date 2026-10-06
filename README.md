# Euro Inflation Monitor

A compact Streamlit relative-value dashboard using reproducible mock euro-area linker and EUR HICPxT swap data.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app creates its data in memory, so no data download or API key is required.

## Included

- France, Germany and Italy inflation-linked bonds
- EUR HICP ex-tobacco zero-coupon swaps
- Bond breakeven, IOTA and forward inflation
- Three-month excess carry
- Real DV01 and inflation IE01 per €1m face value
- Country-selectable EU and UK historical panels at 2Y, 5Y and 10Y
- Sortable relative-value table and CSV export

All values are synthetic and intended for demonstration only.
