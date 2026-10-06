from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


st.set_page_config(page_title="Inflation PM Monitor", page_icon="€", layout="wide")

INK = "#172033"
MUTED = "#657188"
BLUE = "#2855d9"
TEAL = "#16877a"
RED = "#b8404c"
GRID = "#e8ebf1"
AS_OF = pd.Timestamp("2026-10-06 16:30:00", tz="Europe/London")
SNAPSHOT_ID = "DEMO-20261006-1630"
TENORS = np.array([1, 2, 3, 5, 7, 10, 15, 20, 30], dtype=float)

st.markdown(
    f"""
    <style>
    .stApp {{ background:#fff; color:{INK}; }}
    .block-container {{ max-width:1500px; padding-top:1.35rem; padding-bottom:2rem; }}
    [data-testid="stMetric"] {{ background:#fff; border:1px solid #e1e5eb; border-radius:10px; padding:13px 15px; }}
    [data-testid="stMetricLabel"] {{ color:{MUTED}; }}
    [data-testid="stMetricValue"] {{ color:{INK}; font-weight:650; }}
    [data-testid="stDataFrame"] {{ border:1px solid #e0e4ea; border-radius:8px; overflow:hidden; }}
    h1,h2,h3 {{ color:{INK}; letter-spacing:-.025em; }}
    .kicker {{ color:{BLUE}; font-size:.74rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }}
    .subtitle {{ color:{MUTED}; margin-top:-.55rem; }}
    .status {{ background:#f4f7ff; border:1px solid #d9e2ff; border-radius:8px; padding:9px 12px; color:#42506a; font-size:.78rem; margin:.85rem 0 .25rem; }}
    .demo-pill {{ display:inline-block; background:#e7edff; color:{BLUE}; border-radius:999px; padding:2px 8px; font-weight:700; margin-right:8px; }}
    .section-title {{ font-size:1.05rem; font-weight:650; color:{INK}; margin:1.15rem 0 .12rem; }}
    .section-note {{ color:{MUTED}; font-size:.82rem; margin-bottom:.55rem; }}
    .detail-card {{ background:#f7f8fa; border:1px solid #e1e5eb; border-radius:10px; padding:15px 16px; min-height:120px; }}
    .detail-label {{ color:{MUTED}; font-size:.73rem; text-transform:uppercase; letter-spacing:.07em; }}
    .detail-value {{ color:{INK}; font-size:1.36rem; font-weight:650; margin:.16rem 0; }}
    .detail-note {{ color:{MUTED}; font-size:.79rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)


EUR_SWAP = np.array([1.72, 1.78, 1.84, 1.94, 2.02, 2.09, 2.16, 2.20, 2.24])
UK_SWAP = np.array([3.05, 3.08, 3.11, 3.18, 3.24, 3.31, 3.37, 3.42, 3.47])

MARKETS = {
    "France": {
        "currency": "EUR", "symbol": "€", "index": "EUR HICPxT", "swap": EUR_SWAP,
        "nominal": np.array([2.30, 2.38, 2.46, 2.62, 2.73, 2.88, 3.05, 3.18, 3.28]),
        "real": np.array([0.58, 0.60, 0.63, 0.70, 0.74, 0.79, 0.90, 0.98, 1.04]),
    },
    "Germany": {
        "currency": "EUR", "symbol": "€", "index": "EUR HICPxT", "swap": EUR_SWAP,
        "nominal": np.array([2.18, 2.26, 2.35, 2.50, 2.61, 2.76, 2.92, 3.04, 3.14]),
        "real": np.array([0.49, 0.51, 0.55, 0.60, 0.62, 0.65, 0.74, 0.81, 0.85]),
    },
    "Italy": {
        "currency": "EUR", "symbol": "€", "index": "EUR HICPxT", "swap": EUR_SWAP,
        "nominal": np.array([3.15, 3.25, 3.36, 3.55, 3.70, 3.92, 4.18, 4.38, 4.55]),
        "real": np.array([1.38, 1.43, 1.50, 1.64, 1.75, 1.88, 2.08, 2.23, 2.35]),
    },
    "Spain": {
        "currency": "EUR", "symbol": "€", "index": "EUR HICPxT", "swap": EUR_SWAP,
        "nominal": np.array([2.72, 2.82, 2.92, 3.10, 3.22, 3.39, 3.61, 3.76, 3.89]),
        "real": np.array([0.96, 1.02, 1.08, 1.18, 1.25, 1.34, 1.48, 1.57, 1.64]),
    },
    "United Kingdom": {
        "currency": "GBP", "symbol": "£", "index": "UK RPI", "swap": UK_SWAP,
        "nominal": np.array([3.75, 3.82, 3.88, 4.02, 4.12, 4.28, 4.42, 4.52, 4.60]),
        "real": np.array([0.74, 0.77, 0.80, 0.86, 0.90, 0.97, 1.05, 1.11, 1.15]),
    },
}

# country, code, coupon, maturity, BE residual (bp), position (m), benchmark raw weight, index ratio
BOND_SPECS = [
    ("France", "FR-DEMO-28", 0.10, "2028-03-01", -1.5, 18, 4.0, 1.18),
    ("France", "FR-DEMO-30", 0.40, "2030-07-25", 1.0, 24, 5.0, 1.22),
    ("France", "FR-DEMO-32", 0.10, "2032-03-01", -2.0, 21, 4.5, 1.19),
    ("France", "FR-DEMO-36", 0.60, "2036-07-25", 2.5, 29, 5.5, 1.27),
    ("France", "FR-DEMO-40", 0.50, "2040-03-01", 0.0, 20, 4.0, 1.25),
    ("France", "FR-DEMO-48", 0.75, "2048-07-25", -3.0, 15, 3.0, 1.31),
    ("Germany", "DE-DEMO-28", 0.10, "2028-04-15", 1.0, 16, 4.0, 1.15),
    ("Germany", "DE-DEMO-30", 0.50, "2030-04-15", -1.0, 22, 5.5, 1.20),
    ("Germany", "DE-DEMO-33", 0.10, "2033-04-15", 2.0, 19, 4.5, 1.17),
    ("Germany", "DE-DEMO-46", 0.10, "2046-04-15", -2.5, 13, 3.0, 1.24),
    ("Italy", "IT-DEMO-28", 1.30, "2028-09-15", -2.0, 25, 5.0, 1.24),
    ("Italy", "IT-DEMO-30", 0.40, "2030-05-15", 2.5, 20, 4.0, 1.20),
    ("Italy", "IT-DEMO-33", 0.10, "2033-05-15", -1.0, 28, 5.5, 1.18),
    ("Italy", "IT-DEMO-36", 0.50, "2036-05-15", 3.5, 24, 4.5, 1.26),
    ("Italy", "IT-DEMO-41", 0.65, "2041-05-15", 1.0, 18, 3.5, 1.29),
    ("Italy", "IT-DEMO-51", 0.15, "2051-05-15", -3.5, 12, 2.5, 1.21),
    ("Spain", "ES-DEMO-28", 0.15, "2028-11-30", 1.5, 18, 4.0, 1.16),
    ("Spain", "ES-DEMO-30", 0.70, "2030-11-30", -1.0, 23, 5.0, 1.23),
    ("Spain", "ES-DEMO-33", 0.15, "2033-11-30", 2.0, 20, 4.5, 1.19),
    ("Spain", "ES-DEMO-37", 0.65, "2037-11-30", -2.5, 17, 3.5, 1.27),
    ("Spain", "ES-DEMO-49", 1.00, "2049-11-30", 3.0, 11, 2.5, 1.34),
    ("United Kingdom", "UK-DEMO-29", 0.13, "2029-03-22", -3.0, 22, 4.5, 1.31),
    ("United Kingdom", "UK-DEMO-31", 0.13, "2031-08-10", 2.0, 27, 5.0, 1.35),
    ("United Kingdom", "UK-DEMO-36", 0.13, "2036-03-22", -1.5, 25, 5.0, 1.39),
    ("United Kingdom", "UK-DEMO-42", 0.13, "2042-03-22", 3.0, 19, 4.0, 1.43),
    ("United Kingdom", "UK-DEMO-50", 0.13, "2050-03-22", 0.5, 14, 3.0, 1.47),
    ("United Kingdom", "UK-DEMO-62", 0.13, "2062-03-22", -2.0, 9, 2.0, 1.52),
]


def curve_value(values, years):
    return float(np.interp(years, TENORS, values))


def one_year_forward(start, curve):
    if start <= 1:
        return curve_value(curve, 1)
    if start >= 30:
        return curve_value(curve, 30)
    end = min(start + 1, 30)
    start = min(start, 30)
    z_start = curve_value(curve, start) / 100
    z_end = curve_value(curve, end) / 100
    return (((1 + z_end) ** end / (1 + z_start) ** start) ** (1 / (end - start)) - 1) * 100


def cashflows(coupon, years, frequency):
    count = max(1, int(np.ceil(years * frequency)))
    times = np.arange(1, count + 1, dtype=float) / frequency
    times[-1] = years
    flows = np.full(count, coupon / frequency)
    flows[-1] += 100
    return times, flows


def real_price(coupon, real_yield, years, frequency):
    times, flows = cashflows(coupon, years, frequency)
    discount = (1 + real_yield / 100 / frequency) ** (frequency * times)
    return float(np.sum(flows / discount))


def bond_pricing(coupon, real_yield, years, frequency):
    price = real_price(coupon, real_yield, years, frequency)
    price_down = real_price(coupon, real_yield - 0.01, years, frequency)
    price_up = real_price(coupon, real_yield + 0.01, years, frequency)
    modified_duration = (price_down - price_up) / 2 / price / 0.0001
    return price, modified_duration


@st.cache_data
def make_history(seed=17):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=AS_OF.tz_localize(None).normalize(), periods=522)
    rows = []
    swap_paths = {}

    for index_group, swap_curve in [("EUR HICPxT", EUR_SWAP), ("UK RPI", UK_SWAP)]:
        macro = np.zeros(len(dates))
        for day in range(1, len(dates)):
            macro[day] = 0.992 * macro[day - 1] + rng.normal(0, 0.010)
        for tenor, current_swap in zip(TENORS.astype(int), swap_curve):
            local = np.zeros(len(dates))
            for day in range(1, len(dates)):
                local[day] = 0.975 * local[day - 1] + rng.normal(0, 0.003 + tenor * 0.00015)
            path = macro + local
            path -= path[-1]
            swap_paths[(index_group, tenor)] = current_swap + path

    for country, market in MARKETS.items():
        for tenor in TENORS.astype(int):
            swap_series = swap_paths[(market["index"], tenor)]
            target_be = curve_value(market["nominal"], tenor) - curve_value(market["real"], tenor)
            target_iota_bp = (curve_value(market["swap"], tenor) - target_be) * 100
            basis_noise = np.zeros(len(dates))
            for day in range(1, len(dates)):
                basis_noise[day] = 0.982 * basis_noise[day - 1] + rng.normal(0, 0.42 + tenor * 0.015)
            basis_noise -= basis_noise[-1]
            iota_bp = target_iota_bp + basis_noise
            linker = swap_series - iota_bp / 100
            rows.extend(
                {
                    "Date": dt,
                    "Country": country,
                    "Tenor": tenor,
                    "Swap": swap_rate,
                    "Linker": linker_rate,
                    "IOTA": basis,
                }
                for dt, swap_rate, linker_rate, basis in zip(dates, swap_series, linker, iota_bp)
            )
    return pd.DataFrame(rows)


def iota_statistics(history, country, tenor, current_iota):
    series = history[(history["Country"] == country) & (history["Tenor"] == tenor)]["IOTA"]
    lookback = series.tail(252)
    volatility = float(lookback.std(ddof=0))
    z_score = 0.0 if volatility == 0 else (current_iota - float(lookback.mean())) / volatility
    percentile = float((lookback <= current_iota).mean() * 100)
    return z_score, percentile


@st.cache_data
def make_bond_snapshot(history):
    rows = []
    for country, code, coupon, maturity_text, be_residual, position, _benchmark_raw, index_ratio in BOND_SPECS:
        market = MARKETS[country]
        maturity = pd.Timestamp(maturity_text)
        years = (maturity - AS_OF.tz_localize(None)).days / 365.25
        if years <= 0:
            continue
        frequency = 2 if country == "United Kingdom" else 1
        nominal_yield = curve_value(market["nominal"], years)
        fitted_real_yield = curve_value(market["real"], years)
        real_yield = fitted_real_yield - be_residual / 100
        bond_be = nominal_yield - real_yield
        swap_rate = curve_value(market["swap"], years)
        iota_bp = (swap_rate - bond_be) * 100
        clean_price, duration = bond_pricing(coupon, real_yield, years, frequency)
        accrued_real = coupon / frequency * 0.35
        dirty_price = (clean_price + accrued_real) * index_ratio
        nearest_tenor = int(TENORS[np.argmin(np.abs(TENORS - min(years, 30)))])
        iota_z, iota_percentile = iota_statistics(history, country, nearest_tenor, iota_bp)
        rolled_years = max(0.25, years - 0.25)
        rolled_real_yield = curve_value(market["real"], rolled_years) - be_residual / 100
        roll_bp = (real_yield - rolled_real_yield) * duration * 100
        coupon_accrual_bp = coupon * 25
        inflation_accrual_bp = ((1 + one_year_forward(years, market["swap"]) / 100) ** 0.25 - 1) * 10_000
        gross_carry_roll = coupon_accrual_bp + inflation_accrual_bp + roll_bp
        bid_ask = min(11.0, 1.5 + 0.12 * years + (1.7 if country == "Italy" else 0.8))
        signal = "Cash cheap" if iota_z >= 0.75 else "Cash rich" if iota_z <= -0.75 else "Neutral"
        rows.append(
            {
                "Bond": f"{coupon:.2f}% {maturity:%b-%y}",
                "ID": code,
                "Country": country,
                "Currency": market["currency"],
                "Index": market["index"],
                "Maturity": maturity,
                "Years": years,
                "Position": position,
                "Index Ratio": index_ratio,
                "Clean Price": clean_price,
                "Dirty Price": dirty_price,
                "Nominal Yield": nominal_yield,
                "Real Yield": real_yield,
                "Bond Breakeven": bond_be,
                "ZC Swap": swap_rate,
                "IOTA": iota_bp,
                "IOTA Z": iota_z,
                "IOTA Percentile": iota_percentile,
                "3M Gross Carry/Roll": gross_carry_roll,
                "Real Duration": duration,
                "Bid/Ask": bid_ask,
                "Signal": signal,
            }
        )
    return pd.DataFrame(rows)


def make_swap_table(history, country):
    market = MARKETS[country]
    rows = []
    for tenor, rate in zip(TENORS.astype(int), market["swap"]):
        series = history[(history["Country"] == country) & (history["Tenor"] == tenor)]["Swap"]
        if tenor == 1:
            forward = rate
        else:
            z_start = curve_value(market["swap"], tenor - 1) / 100
            z_end = rate / 100
            forward = ((1 + z_end) ** tenor / (1 + z_start) ** (tenor - 1) - 1) * 100
        rows.append(
            {
                "Tenor": f"{tenor}Y",
                "ZC Swap": rate,
                "1D": (float(series.iloc[-1]) - float(series.iloc[-2])) * 100,
                "1W": (float(series.iloc[-1]) - float(series.iloc[-6])) * 100,
                "1Y Fwd Ending": forward,
            }
        )
    return pd.DataFrame(rows)


history = make_history()
bonds = make_bond_snapshot(history)

header_left, header_right = st.columns([0.76, 0.24], vertical_alignment="bottom")
with header_right:
    selected_country = st.selectbox("Market", list(MARKETS), index=0, key="market_selector")

market = MARKETS[selected_country]
country_bonds = bonds[bonds["Country"] == selected_country].copy()
symbol = market["symbol"]

with header_left:
    st.markdown('<div class="kicker">Inflation portfolio · relative value</div>', unsafe_allow_html=True)
    st.title(f"{selected_country} {market['index']} linker monitor")
    st.markdown(
        '<div class="subtitle">Cash-versus-swaps history, portfolio exposure and security-level economics</div>',
        unsafe_allow_html=True,
    )

ten_year = history[(history["Country"] == selected_country) & (history["Tenor"] == 10)]
swap_10 = float(ten_year["Swap"].iloc[-1])
be_10 = float(ten_year["Linker"].iloc[-1])
iota_10 = float(ten_year["IOTA"].iloc[-1])
swap_day = (swap_10 - float(ten_year["Swap"].iloc[-2])) * 100
be_day = (be_10 - float(ten_year["Linker"].iloc[-2])) * 100
iota_day = iota_10 - float(ten_year["IOTA"].iloc[-2])
iota_z, _ = iota_statistics(history, selected_country, 10, iota_10)
carry_value_k = (
    country_bonds["Position"] * 1_000_000 * country_bonds["3M Gross Carry/Roll"] / 10_000
).sum() / 1_000

m1, m2, m3, m4 = st.columns(4)
m1.metric("10Y swap", f"{swap_10:.2f}%", f"{swap_day:+.1f} bp 1D")
m2.metric("10Y linker BE", f"{be_10:.2f}%", f"{be_day:+.1f} bp 1D")
m3.metric("10Y IOTA", f"{iota_10:+.1f} bp", f"{iota_z:+.1f} z · {iota_day:+.1f} bp 1D")
m4.metric("3M gross carry/roll", f"{symbol}{carry_value_k:,.0f}k", "before funding")

st.markdown('<div class="section-title">Historical cash versus swaps</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-note">Upper panel: inflation levels. Lower panel: IOTA in basis points with a zero reference.</div>',
    unsafe_allow_html=True,
)

chart_tenors = [2, 5, 10]
chart_history = history[(history["Country"] == selected_country) & history["Tenor"].isin(chart_tenors)]
level_min = min(chart_history["Swap"].min(), chart_history["Linker"].min()) - 0.06
level_max = max(chart_history["Swap"].max(), chart_history["Linker"].max()) + 0.06
iota_limit = max(6.0, float(chart_history["IOTA"].abs().max()) * 1.15)

for column, tenor in zip(st.columns(3), chart_tenors):
    series = chart_history[chart_history["Tenor"] == tenor]
    current_iota = float(series["IOTA"].iloc[-1])
    z_score, percentile = iota_statistics(history, selected_country, tenor, current_iota)
    figure = make_subplots(
        rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.04
    )
    figure.add_trace(
        go.Scatter(
            x=series["Date"], y=series["Swap"], name="Swap", mode="lines",
            line=dict(color=BLUE, width=2.0),
            hovertemplate="%{x|%d %b %Y}<br>Swap %{y:.2f}%<extra></extra>",
        ), row=1, col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=series["Date"], y=series["Linker"], name="Linker BE", mode="lines",
            line=dict(color=INK, width=1.6, dash="dot"),
            hovertemplate="%{x|%d %b %Y}<br>Linker BE %{y:.2f}%<extra></extra>",
        ), row=1, col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=series["Date"], y=series["IOTA"], name="IOTA", mode="lines",
            line=dict(color=RED, width=1.5), fill="tozeroy", fillcolor="rgba(184,64,76,.08)",
            hovertemplate="%{x|%d %b %Y}<br>IOTA %{y:+.1f} bp<extra></extra>",
        ), row=2, col=1,
    )
    figure.add_hline(y=0, line_width=1, line_color="#aeb6c4", row=2, col=1)
    figure.update_layout(
        title=dict(
            text=f"{tenor}Y · IOTA {current_iota:+.1f} bp · z {z_score:+.1f} · pctl {percentile:.0f}",
            x=0.02, font=dict(size=13, color=INK),
        ),
        height=330, margin=dict(l=58, r=10, t=42, b=26),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font=dict(color=MUTED, family="Arial, sans-serif", size=10),
        showlegend=tenor == 2,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#ffffff", font_color=INK, bordercolor="#d9dee7"),
    )
    figure.update_xaxes(gridcolor=GRID, zeroline=False, tickformat="%b\n%Y", nticks=5, row=2, col=1)
    figure.update_yaxes(
        title_text="Rate",
        title_standoff=5,
        automargin=True,
        gridcolor=GRID,
        range=[level_min, level_max],
        ticksuffix="%",
        tickformat=".1f",
        row=1,
        col=1,
    )
    figure.update_yaxes(
        title_text="IOTA",
        title_standoff=5,
        automargin=True,
        gridcolor=GRID,
        range=[-iota_limit, iota_limit],
        ticksuffix=" bp",
        tickformat="+.0f",
        row=2,
        col=1,
    )
    column.plotly_chart(
        figure,
        width="stretch",
        theme=None,
        key=f"history_{selected_country.lower().replace(' ', '_')}_{tenor}",
        config={"displayModeBar": False},
    )


@st.fragment
def render_relative_value(data):
    st.markdown('<div class="section-title">Relative-value screen</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Synthetic sleeve positions. Positive IOTA means swap inflation is above the cash breakeven.</div>',
        unsafe_allow_html=True,
    )
    table = data[
        [
            "Bond", "Maturity", "Position", "Real Yield", "Bond Breakeven", "ZC Swap",
            "IOTA", "IOTA Z", "3M Gross Carry/Roll", "Bid/Ask", "Signal",
        ]
    ].sort_values(["IOTA Z", "IOTA"], ascending=False)
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        height=min(420, 38 * (len(table) + 1)),
        column_config={
            "Maturity": st.column_config.DateColumn(format="DD MMM YYYY"),
            "Position": st.column_config.NumberColumn(f"Position ({market['currency']}m)", format="%.0f"),
            "Real Yield": st.column_config.NumberColumn("Real yld", format="%.2f%%"),
            "Bond Breakeven": st.column_config.NumberColumn("Bond BE", format="%.2f%%"),
            "ZC Swap": st.column_config.NumberColumn("ZC swap", format="%.2f%%"),
            "IOTA": st.column_config.NumberColumn(format="%+.1f bp"),
            "IOTA Z": st.column_config.NumberColumn(format="%+.1f"),
            "3M Gross Carry/Roll": st.column_config.NumberColumn("3M gross C/R", format="%+.1f bp"),
            "Bid/Ask": st.column_config.NumberColumn(format="%.1f bp"),
        },
    )

    st.markdown('<div class="section-title">Selected security</div>', unsafe_allow_html=True)
    selected_id = st.selectbox(
        "Bond",
        data["ID"].tolist(),
        format_func=lambda item: data.loc[data["ID"] == item, "Bond"].iloc[0],
        key=f"bond_selector_{selected_country.lower().replace(' ', '_')}",
    )
    selected = data.loc[data["ID"] == selected_id].iloc[0]
    st.caption(
        f"{selected['ID']} · {selected['Currency']} · {selected['Index']} · "
        f"index ratio {selected['Index Ratio']:.4f} · dirty price {selected['Dirty Price']:.2f}"
    )
    cards = [
        ("IOTA", f'{selected["IOTA"]:+.1f} bp', selected["Signal"]),
        ("IOTA history", f'{selected["IOTA Z"]:+.1f} z', f'{selected["IOTA Percentile"]:.0f}th percentile'),
        ("3M gross carry/roll", f'{selected["3M Gross Carry/Roll"]:+.1f} bp', "before funding and costs"),
    ]
    for card, (label, value, note) in zip(st.columns(3), cards):
        card.markdown(
            f'<div class="detail-card"><div class="detail-label">{label}</div>'
            f'<div class="detail-value">{value}</div><div class="detail-note">{note}</div></div>',
            unsafe_allow_html=True,
        )

    export = table.copy()
    export.insert(0, "Snapshot", SNAPSHOT_ID)
    export.insert(1, "As Of", AS_OF.isoformat())
    export.insert(2, "Data Status", "SYNTHETIC DEMO")
    st.download_button(
        "Download selected sleeve",
        export.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_country.lower().replace(' ', '_')}_linker_demo.csv",
        mime="text/csv",
    )


render_relative_value(country_bonds)

st.markdown(f'<div class="section-title">{market["index"]} swap curve</div>', unsafe_allow_html=True)
swap_table = make_swap_table(history, selected_country)
st.dataframe(
    swap_table,
    hide_index=True,
    width="stretch",
    height=355,
    column_config={
        "ZC Swap": st.column_config.NumberColumn(format="%.2f%%"),
        "1D": st.column_config.NumberColumn(format="%+.1f bp"),
        "1W": st.column_config.NumberColumn(format="%+.1f bp"),
        "1Y Fwd Ending": st.column_config.NumberColumn(format="%.2f%%"),
    },
)
