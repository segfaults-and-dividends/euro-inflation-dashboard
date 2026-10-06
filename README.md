# Inflation PM Monitor

A compact Streamlit relative-value dashboard using reproducible synthetic EU and UK linker and inflation-swap data.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app creates its data in memory, so no data download or API key is required.

## Included

- France, Germany, Italy, Spain and United Kingdom inflation-linked bond sleeves
- EUR HICPxT and UK RPI zero-coupon swap curves
- Three consistent historical panels at 2Y, 5Y and 10Y for the selected market
- Bond breakeven, IOTA, IOTA history, explicit one-year forwards and three-month gross carry/roll
- Security-level position, breakeven, IOTA and carry/roll comparisons
- Sortable relative-value table and snapshot-labelled CSV export

The market selector scopes the entire page. Every value is synthetic, generated in memory from one reproducible snapshot, and intended for demonstration only.
