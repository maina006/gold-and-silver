from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data"
IBJA_FILE = DATA / "ibja_daily.csv"
FX_FILE = DATA / "usd_inr.csv"
INTL_FILE = DATA / "international_daily.csv"

st.set_page_config(page_title="India Bullion Tracker", page_icon="📈", layout="wide")

st.title("India Gold & Silver Tracker")
st.caption("Indian benchmark prices • Official-source records • INR and international comparison")

st.info(
    "Data policy: this dashboard does not scrape price aggregators or MCX. "
    "Only enter figures obtained directly from sources whose terms permit your use. "
    "A blank or stale dataset is shown as such; prices are never fabricated."
)

def load_csv(path, required):
    if not path.exists():
        return pd.DataFrame(columns=required)
    try:
        df = pd.read_csv(path)
        for col in required:
            if col not in df.columns:
                st.error(f"{path.name} is missing required column: {col}")
                return pd.DataFrame(columns=required)
        return df
    except Exception as exc:
        st.error(f"Could not read {path.name}: {exc}")
        return pd.DataFrame(columns=required)

ibja_cols = [
    "date", "session", "gold_999_inr_10g", "gold_916_inr_10g",
    "gold_750_inr_10g", "silver_999_inr_kg", "source_name", "source_url"
]
fx_cols = ["date", "usd_inr", "source_name", "source_url"]
intl_cols = [
    "date", "gold_usd_per_troy_oz", "silver_usd_per_troy_oz",
    "source_name", "source_url"
]

ibja = load_csv(IBJA_FILE, ibja_cols)
fx = load_csv(FX_FILE, fx_cols)
intl = load_csv(INTL_FILE, intl_cols)

def clean_dates(df):
    if not df.empty:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date")
    return df

ibja, fx, intl = map(clean_dates, (ibja, fx, intl))

def latest_value(df, col):
    if df.empty or col not in df:
        return None
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    return None if s.empty else float(s.iloc[-1])

latest_date = None if ibja.empty else ibja["date"].max().date().isoformat()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest IBJA record", latest_date or "No data")
g = latest_value(ibja, "gold_999_inr_10g")
s = latest_value(ibja, "silver_999_inr_kg")
c2.metric("Gold 999 (₹ / 10g)", "—" if g is None else f"₹{g:,.0f}")
c3.metric("Silver 999 (₹ / kg)", "—" if s is None else f"₹{s:,.0f}")
c4.metric("USD/INR reference", "—" if latest_value(fx, "usd_inr") is None else f"₹{latest_value(fx, 'usd_inr'):,.4f}")

st.subheader("Indian benchmark history")
if ibja.empty:
    st.warning("No IBJA records yet. Add dated rows to data/ibja_daily.csv in your GitHub repository.")
else:
    metric = st.selectbox(
        "Choose benchmark",
        ["gold_999_inr_10g", "gold_916_inr_10g", "gold_750_inr_10g", "silver_999_inr_kg"],
        format_func=lambda x: {
            "gold_999_inr_10g": "Gold 999 — ₹ / 10g",
            "gold_916_inr_10g": "Gold 916 — ₹ / 10g",
            "gold_750_inr_10g": "Gold 750 — ₹ / 10g",
            "silver_999_inr_kg": "Silver 999 — ₹ / kg",
        }[x],
    )
    plot_df = ibja.copy()
    plot_df[metric] = pd.to_numeric(plot_df[metric], errors="coerce")
    plot_df = plot_df.dropna(subset=[metric])
    if not plot_df.empty:
        fig = px.line(plot_df, x="date", y=metric, markers=True, title="IBJA benchmark price history")
        fig.update_layout(xaxis_title="Date", yaxis_title="INR", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No numeric values are available for this benchmark.")

st.subheader("International benchmark converted to INR")
st.caption("Calculated only when an international price and FBIL USD/INR rate exist for the same date. No forward-fill or interpolation.")
if not intl.empty and not fx.empty:
    merged = intl.merge(fx[["date", "usd_inr"]], on="date", how="inner")
    for col in ["gold_usd_per_troy_oz", "silver_usd_per_troy_oz", "usd_inr"]:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")
    merged = merged.dropna(subset=["gold_usd_per_troy_oz", "silver_usd_per_troy_oz", "usd_inr"])
    if not merged.empty:
        merged["gold_inr_per_gram"] = merged["gold_usd_per_troy_oz"] * merged["usd_inr"] / 31.1034768
        merged["silver_inr_per_kg"] = merged["silver_usd_per_troy_oz"] * merged["usd_inr"] / 31.1034768 * 1000
        metal = st.radio("International metal", ["Gold (₹ / gram)", "Silver (₹ / kg)"], horizontal=True)
        y = "gold_inr_per_gram" if metal.startswith("Gold") else "silver_inr_per_kg"
        f2 = px.line(merged, x="date", y=y, markers=True, title=f"International benchmark converted to INR — {metal}")
        f2.update_layout(xaxis_title="Date", yaxis_title="INR", hovermode="x unified")
        st.plotly_chart(f2, use_container_width=True)
        st.dataframe(merged[["date", "usd_inr", "gold_inr_per_gram", "silver_inr_per_kg"]].tail(20), use_container_width=True)
    else:
        st.warning("No matching dates between international prices and USD/INR data.")
else:
    st.warning("International comparison needs both international_daily.csv and usd_inr.csv.")

with st.expander("Data sources, units and methodology"):
    st.markdown("""
    - **Indian prices:** enter IBJA figures directly from an authorised IBJA publication or API, with attribution and source URL.
    - **International prices:** enter LBMA/IBA figures only if your licence or written permission permits the intended use. Do not use this feature with unlicensed benchmark data.
    - **FX:** enter FBIL USD/INR reference rates from an authorised publication.
    - Gold conversion: USD/troy oz × USD/INR ÷ 31.1034768 = INR/gram.
    - Silver conversion: USD/troy oz × USD/INR ÷ 31.1034768 × 1,000 = INR/kg.
    - Converted international prices are indicative benchmark conversions, not Indian retail prices. They exclude import duty, GST, freight, local premiums and differences in benchmark timing/specification.
    - No MCX data is used. No third-party aggregator is queried.
    """)

st.subheader("Data freshness")
def freshness(df, label):
    if df.empty:
        st.write(f"**{label}:** No records")
    else:
        dt = df["date"].max().date()
        st.write(f"**{label}:** Latest record {dt.isoformat()}")

freshness(ibja, "IBJA")
freshness(intl, "International benchmark")
freshness(fx, "FBIL USD/INR")

st.caption("This is an informational benchmark tracker, not investment advice or a live trading terminal.")
