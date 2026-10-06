from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Euro Inflation Monitor", page_icon="€", layout="wide")

INK = "#172033"
MUTED = "#657188"
BLUE = "#2855d9"
GRID = "#e8ebf1"

st.markdown(
    f"""
    <style>
    .stApp {{ background:#fff; color:{INK}; }}
    .block-container {{ max-width:1480px; padding-top:1.7rem; padding-bottom:2rem; }}
    [data-testid="stSidebar"] {{ background:#f6f7f9; border-right:1px solid #e3e6eb; }}
    [data-testid="stSidebar"] * {{ color:{INK}; }}
    [data-testid="stMetric"] {{ background:#fff; border:1px solid #e1e5eb; border-radius:10px; padding:14px 16px; }}
    [data-testid="stMetricLabel"] {{ color:{MUTED}; }}
    [data-testid="stMetricValue"] {{ color:{INK}; font-weight:650; }}
    [data-testid="stDataFrame"] {{ border:1px solid #e0e4ea; border-radius:8px; overflow:hidden; }}
    h1,h2,h3 {{ color:{INK}; letter-spacing:-.025em; }}
    .kicker {{ color:{BLUE}; font-size:.76rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }}
    .subtitle {{ color:{MUTED}; margin-top:-.55rem; }}
    .section-title {{ font-size:1.05rem; font-weight:650; color:{INK}; margin:1.15rem 0 .12rem; }}
    .section-note {{ color:{MUTED}; font-size:.83rem; margin-bottom:.55rem; }}
    .detail-card {{ background:#f7f8fa; border:1px solid #e1e5eb; border-radius:10px; padding:16px 18px; min-height:126px; }}
    .detail-label {{ color:{MUTED}; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; }}
    .detail-value {{ color:{INK}; font-size:1.45rem; font-weight:650; margin:.16rem 0; }}
    .detail-note {{ color:{MUTED}; font-size:.82rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

SWAP_TENORS = np.array([1, 2, 3, 5, 7, 10, 15, 20, 30], dtype=float)
SWAP_RATES = np.array([1.72, 1.78, 1.84, 1.94, 2.02, 2.09, 2.16, 2.20, 2.24])


def interp_curve(years):
    return np.interp(years, SWAP_TENORS, SWAP_RATES)


def forward_rate(start, end, z_start, z_end):
    return (((1 + z_end / 100) ** end / (1 + z_start / 100) ** start) ** (1 / (end - start)) - 1) * 100


@st.cache_data
def make_euro_linkers(seed=42):
    rng = np.random.default_rng(seed)
    today = pd.Timestamp(date.today())
    issuers = [
        ("France", "OAT€i", 12, 2.80, 1.16, 0.02),
        ("Germany", "DBR€i", 8, 2.63, 1.11, -0.04),
        ("Italy", "BTP€i", 10, 3.48, 1.19, 0.14),
    ]
    rows = []
    for country, family, count, nominal_base, ratio_base, basis in issuers:
        maturities = np.linspace(2.0, 28.0, count) + rng.normal(0, 0.55, count)
        for years in maturities:
            years = float(np.clip(years, 1.1, 29.5))
            maturity = today + pd.to_timedelta(int(years * 365.25), unit="D")
            swap = float(interp_curve(years))
            nominal_yield = nominal_base + 0.028 * years + 0.12 * np.exp(-years / 3) + rng.normal(0, 0.035)
            iota = basis + rng.normal(0, 0.055)
            breakeven = swap - iota
            real_yield = nominal_yield - breakeven
            coupon = float(rng.choice([0.10, 0.25, 0.50, 0.70, 1.00, 1.50, 1.80]))
            duration = years * (0.88 + rng.normal(0, 0.012))
            real_price = 100 + (coupon - real_yield) * duration + rng.normal(0, 0.55)
            index_ratio = ratio_base + rng.uniform(0.00, 0.28)
            indexed_dirty = (real_price + coupon * rng.uniform(0.05, 0.90)) * index_ratio
            outstanding = rng.uniform(5.0, 34.0)
            real_dv01 = indexed_dirty / 100 * 1_000_000 * duration * 0.0001
            inflation_ie01 = indexed_dirty / 100 * 1_000_000 * years * 0.0001
            z_t1 = float(interp_curve(min(years + 1, 30)))
            one_year_forward = float(
                forward_rate(np.array([years]), np.array([years + 1]), np.array([swap]), np.array([z_t1]))[0]
            )
            rows.append(
                {
                    "Bond": f"{country[:2].upper()} {coupon:.2f} {maturity:%b-%y}",
                    "Country": country,
                    "Family": family,
                    "Maturity": maturity,
                    "Years": years,
                    "Nominal Yield": nominal_yield,
                    "Real Yield": real_yield,
                    "Bond Breakeven": breakeven,
                    "ZC Swap": swap,
                    "IOTA": iota * 100,
                    "1Y Forward Inflation": one_year_forward,
                    "3M Excess Carry": (one_year_forward - breakeven) * 25,
                    "Real DV01": real_dv01,
                    "Inflation IE01": inflation_ie01,
                    "Outstanding": outstanding,
                }
            )
    return pd.DataFrame(rows).sort_values(["Country", "Maturity"]).reset_index(drop=True)


@st.cache_data
def make_swap_table():
    tenors = SWAP_TENORS.astype(int)
    starts = np.maximum(tenors - 1, 0.01).astype(float)
    forwards = forward_rate(starts, tenors.astype(float), interp_curve(starts), SWAP_RATES)
    return pd.DataFrame(
        {
            "Tenor": [f"{x}Y" for x in tenors],
            "ZC HICPxT": SWAP_RATES,
            "1Y Forward": forwards,
            "1D": [-1.4, -1.1, -0.8, -0.3, 0.1, 0.5, 0.8, 1.0, 1.2],
            "1W": [-4.2, -3.5, -2.9, -1.7, -0.8, 0.2, 1.1, 1.6, 2.2],
        }
    )


@st.cache_data
def make_history(seed=17):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=105, freq="W-FRI")
    euro_swap_base = {2: 1.78, 5: 1.94, 10: 2.09}
    uk_rpi_swap_base = {2: 3.02, 5: 3.18, 10: 3.31}
    country_iota = {
        "France": 0.02,
        "Germany": -0.04,
        "Italy": 0.14,
        "Spain": 0.09,
        "United Kingdom": -0.10,
    }
    common = np.zeros(len(dates))
    rows = []

    for index in range(1, len(dates)):
        common[index] = 0.965 * common[index - 1] + rng.normal(0, 0.035)

    for tenor in [2, 5, 10]:
        tenor_noise = np.zeros(len(dates))
        for index in range(1, len(dates)):
            tenor_noise[index] = 0.90 * tenor_noise[index - 1] + rng.normal(0, 0.014 + 0.001 * tenor)

        for country, basis in country_iota.items():
            swap_base = uk_rpi_swap_base[tenor] if country == "United Kingdom" else euro_swap_base[tenor]
            swap_series = swap_base + common + tenor_noise
            iota_series = np.zeros(len(dates))
            iota_series[0] = basis
            for index in range(1, len(dates)):
                iota_series[index] = basis + 0.91 * (iota_series[index - 1] - basis) + rng.normal(0, 0.009 + 0.0008 * tenor)
            linker_series = swap_series - iota_series
            for dt, swap_rate, linker_rate in zip(dates, swap_series, linker_series):
                rows.append(
                    {"Date": dt, "Country": country, "Tenor": tenor, "Swap": swap_rate, "Linker": linker_rate}
                )
    return pd.DataFrame(rows)


bonds = make_euro_linkers()
swaps = make_swap_table()
history = make_history()

filtered = bonds[
    bonds["Country"].isin(countries)
    & bonds["Years"].between(*maturity_range)
    & (bonds["Outstanding"] >= min_outstanding)
].copy()

st.markdown('<div class="kicker">EUR inflation-linked markets</div>', unsafe_allow_html=True)
st.title("Euro linker economics")
st.markdown(
    '<div class="subtitle">Bond breakevens, HICPxT swaps, IOTA and carry in one compact screen</div>',
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No bonds match the current filters.")
    st.stop()

weights = filtered["Outstanding"]
avg_real = np.average(filtered["Real Yield"], weights=weights)
avg_be = np.average(filtered["Bond Breakeven"], weights=weights)
avg_swap = np.average(filtered["ZC Swap"], weights=weights)
avg_iota = np.average(filtered["IOTA"], weights=weights)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Weighted real yield", f"{avg_real:.2f}%")
m2.metric("Bond breakeven", f"{avg_be:.2f}%")
m3.metric("HICPxT swap", f"{avg_swap:.2f}%")
m4.metric("IOTA", f"{avg_iota:+.1f} bp")

st.markdown('<div class="section-title">Historical swap inflation versus linkers</div>', unsafe_allow_html=True)
history_country = st.selectbox(
    "Country",
    ["France", "Germany", "Italy", "Spain", "United Kingdom"],
    key="history_country",
)
index_name = "UK RPI" if history_country == "United Kingdom" else "EUR HICPxT"
st.markdown(
    f'<div class="section-note">{index_name} inflation · solid = swap · dotted = linker breakeven</div>',
    unsafe_allow_html=True,
)

tenor_colours = {2: "#2855d9", 5: "#16877a", 10: "#b8404c"}
chart_columns = st.columns(3)

for chart_column, tenor in zip(chart_columns, [2, 5, 10]):
    series = history[(history["Country"] == history_country) & (history["Tenor"] == tenor)]
    figure = go.Figure()
    colour = tenor_colours[tenor]
    figure.add_trace(
        go.Scatter(
            x=series["Date"],
            y=series["Swap"],
            mode="lines",
            name="Swap",
            line=dict(color=colour, width=2.0),
            hovertemplate=f"{tenor}Y swap<br>%{{x|%d %b %Y}}<br>%{{y:.2f}}%<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=series["Date"],
            y=series["Linker"],
            mode="lines",
            name="Linker",
            line=dict(color=colour, width=1.6, dash="dot"),
            hovertemplate=f"{tenor}Y linker<br>%{{x|%d %b %Y}}<br>%{{y:.2f}}%<extra></extra>",
        )
    )
    figure.update_layout(
        title=dict(text=f"{tenor}Y · {history_country}", x=0.02, font=dict(size=14, color=INK)),
        height=285,
        margin=dict(l=8, r=8, t=38, b=8),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color=MUTED, family="Arial, sans-serif", size=10),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#ffffff", font_color=INK, bordercolor="#d9dee7"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
    )
    figure.update_xaxes(gridcolor=GRID, zeroline=False, tickformat="%b\n%Y", nticks=5)
    figure.update_yaxes(gridcolor=GRID, zeroline=False, ticksuffix="%", tickformat=".1f")
    chart_column.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

st.markdown('<div class="section-title">Bond economics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-note">Select a bond for its cash, derivative and risk measures. Sensitivities are per €1m face value.</div>',
    unsafe_allow_html=True,
)
selected_name = st.selectbox("Bond", filtered["Bond"].tolist(), label_visibility="collapsed")
selected = filtered.loc[filtered["Bond"] == selected_name].iloc[0]

columns = st.columns(5)
cards = [
    ("IOTA", f'{selected["IOTA"]:+.1f} bp', "Swap minus bond breakeven"),
    ("3M excess carry", f'{selected["3M Excess Carry"]:+.1f} bp', "Forward inflation minus breakeven"),
    ("1Y forward inflation", f'{selected["1Y Forward Inflation"]:.2f}%', "Implied from the ZC curve"),
    ("Real DV01", f'€{selected["Real DV01"]:,.0f}', "1 bp real-yield move"),
    ("Inflation IE01", f'€{selected["Inflation IE01"]:,.0f}', "1 bp inflation-curve move"),
]
for column, (label, value, note) in zip(columns, cards):
    column.markdown(
        f'<div class="detail-card"><div class="detail-label">{label}</div><div class="detail-value">{value}</div><div class="detail-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-title">Relative-value screen</div>', unsafe_allow_html=True)
table = filtered[
    [
        "Bond", "Country", "Maturity", "Real Yield", "Nominal Yield", "Bond Breakeven",
        "ZC Swap", "IOTA", "1Y Forward Inflation", "3M Excess Carry", "Real DV01", "Inflation IE01",
    ]
].sort_values("IOTA", ascending=False)

st.dataframe(
    table,
    hide_index=True,
    use_container_width=True,
    height=405,
    column_config={
        "Maturity": st.column_config.DateColumn(format="DD MMM YYYY"),
        "Real Yield": st.column_config.NumberColumn("Real yld", format="%.2f%%"),
        "Nominal Yield": st.column_config.NumberColumn("Nominal yld", format="%.2f%%"),
        "Bond Breakeven": st.column_config.NumberColumn("Bond BE", format="%.2f%%"),
        "ZC Swap": st.column_config.NumberColumn("ZC swap", format="%.2f%%"),
        "IOTA": st.column_config.NumberColumn(format="%+.1f bp"),
        "1Y Forward Inflation": st.column_config.NumberColumn("1Y fwd", format="%.2f%%"),
        "3M Excess Carry": st.column_config.NumberColumn("3M carry", format="%+.1f bp"),
        "Real DV01": st.column_config.NumberColumn(format="€%.0f"),
        "Inflation IE01": st.column_config.NumberColumn("Infl. IE01", format="€%.0f"),
    },
)

st.markdown('<div class="section-title">EUR HICPxT swap curve</div>', unsafe_allow_html=True)
swap_col, download_col = st.columns([4, 1])
with swap_col:
    st.dataframe(
        swaps,
        hide_index=True,
        use_container_width=True,
        height=355,
        column_config={
            "ZC HICPxT": st.column_config.NumberColumn(format="%.2f%%"),
            "1Y Forward": st.column_config.NumberColumn(format="%.2f%%"),
            "1D": st.column_config.NumberColumn(format="%+.1f bp"),
            "1W": st.column_config.NumberColumn(format="%+.1f bp"),
        },
    )
with download_col:
    st.download_button(
        "Download economics as CSV",
        table.to_csv(index=False).encode("utf-8"),
        file_name="euro_linker_economics_mock.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption("Synthetic EUR sovereign linker and HICPxT swap data · For demonstration only")
