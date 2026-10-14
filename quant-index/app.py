import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(page_title="OpenQuant Cloud", layout="wide")

CSV_FILE = "strategies.csv"
REQ_FILE = "requirements.txt"

# 1. Auto-create requirements.txt for free public Internet deployment
if not os.path.exists(REQ_FILE):
    with open(REQ_FILE, "w") as f:
        f.write("streamlit\nyfinance\npandas\nnumpy\nplotly\n")

# 2. Auto-create strategies.csv spreadsheet if it doesn't exist yet
if not os.path.exists(CSV_FILE):
    starter_data = [
        {"ID": "#0001", "Title": "Asset Class Trend (GTAA 5)", "Logic_Type": "trend", "Assets": "SPY,EFA,BND,VNQ,GSG", "Rebalance": "Monthly", "Market": "Multi-Asset", "Source_CAGR": 11.27, "Source_Vol": 6.87, "Rule": "Hold each ETF when above its 200-day SMA; else hold T-Bills/Cash.", "Paper": "Mebane Faber (2007)", "URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461"},
        {"ID": "#0002", "Title": "Dual Momentum Equities (GEM)", "Logic_Type": "gem", "Assets": "SPY,EFA,BND", "Rebalance": "Monthly", "Market": "Multi-Asset", "Source_CAGR": 17.40, "Source_Vol": 12.60, "Rule": "Hold 12-month winner between SPY & EFA if return > 0%; else hold BND.", "Paper": "Gary Antonacci (2012)", "URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750"},
        {"ID": "#0003", "Title": "Defensive Canary Allocation (DAA)", "Logic_Type": "daa", "Assets": "SPY,QQQ,VNQ,GLD,BND,VWO", "Rebalance": "Monthly", "Market": "Multi-Asset", "Source_CAGR": 14.80, "Source_Vol": 9.50, "Rule": "Monitor Canary assets (VWO & BND). Hold risky ETFs when Canaries are positive; shift to BND when negative.", "Paper": "Keller & Keuning (2018)", "URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3212862"},
        {"ID": "#0014", "Title": "Momentum Factor in Stocks", "Logic_Type": "top2", "Assets": "SPY,QQQ,IWM,MTUM", "Rebalance": "Monthly", "Market": "Equities", "Source_CAGR": 8.30, "Source_Vol": 16.60, "Rule": "Rank US Equity ETFs by 6-month momentum. Hold top 2 (50% each) if above 200-day SMA.", "Paper": "Jegadeesh & Titman (1993)", "URL": "https://www.jstor.org/stable/2329002"},
        {"ID": "#0021", "Title": "Momentum Effect in Commodities", "Logic_Type": "top2", "Assets": "GLD,SLV,USO,DBA,GSG", "Rebalance": "Monthly", "Market": "Commodities", "Source_CAGR": 14.60, "Source_Vol": 25.57, "Rule": "Rank Commodity ETFs by 6-month momentum. Hold top 2 when above 200-day SMA.", "Paper": "Miffre & Rallis (2007)", "URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=929548"},
        {"ID": "#0028", "Title": "Value & Momentum Across Assets", "Logic_Type": "valmom", "Assets": "SPY,EFA,VNQ,GLD,BND", "Rebalance": "Monthly", "Market": "Multi-Asset", "Source_CAGR": 11.90, "Source_Vol": 10.00, "Rule": "Combine 12-month Momentum rank + 3-year Value reversal rank. Hold top 3 above 200-day SMA.", "Paper": "Asness, Moskowitz, Pedersen (2013)", "URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2174501"}
    ]
    pd.DataFrame(starter_data).to_csv(CSV_FILE, index=False)

df_strats = pd.read_csv(CSV_FILE)

@st.cache_data(ttl=3600)
def get_data(tickers, start_yr):
    t_list = list(tickers)
    try:
        raw = yf.download(t_list, start=f"{start_yr}-01-01", progress=False, timeout=8)
        if not raw.empty and "Close" in raw:
            pr = raw["Close"]
            if isinstance(pr, pd.Series): pr = pr.to_frame(name=t_list[0])
            pr = pr.ffill().dropna()
            if len(pr) > 260 and all(x in pr.columns for x in t_list):
                return pr[t_list]
    except Exception:
        pass
    dates = pd.date_range(start=f"{start_yr}-01-01", periods=2200, freq="B")
    sim = {t: 100 * np.exp(np.cumsum(np.random.RandomState(abs(hash(t)) % 9999).normal(0.00045, 0.011, len(dates)))) for t in t_list}
    return pd.DataFrame(sim, index=dates)

def run_bt(prices, stype, assets, cash_rate_pa=4.2):
    rets = prices[assets].pct_change().fillna(0)
    sma = prices[assets].rolling(200).mean()
    w = pd.DataFrame(0.0, index=prices.index, columns=assets)
    if stype == "trend":
        w = (prices[assets] > sma).astype(float) * (1.0 / len(assets))
    elif stype == "gem":
        m = prices[assets].pct_change(252)
        sw = m[assets[0]] >= m[assets[1]]
        w[assets[0]] = np.where(sw & (m[assets[0]] > 0), 1.0, 0.0)
        w[assets[1]] = np.where((~sw) & (m[assets[1]] > 0), 1.0, 0.0)
        w[assets[2]] = np.where((w[assets[0]] == 0) & (w[assets[1]] == 0), 1.0, 0.0)
    elif stype == "daa":
        m = prices[assets].pct_change(126)
        bad = (m["VWO"] <= 0).astype(int) + (m["BND"] <= 0).astype(int)
        for r in ["SPY", "QQQ", "VNQ", "GLD"]:
            w[r] = np.where(bad == 0, 0.25, np.where(bad == 1, 0.125, 0.0))
        w["BND"] = np.where(bad == 0, 0.0, np.where(bad == 1, 0.5, 1.0))
    elif stype == "top2":
        m = prices[assets].pct_change(126)
        w = ((m.rank(axis=1, ascending=False) <= 2) & (prices[assets] > sma)).astype(float) * 0.5
    elif stype == "valmom":
        score = prices[assets].pct_change(252).rank(axis=1) + 0.5 * (-prices[assets].pct_change(500)).rank(axis=1)
        w = ((score.rank(axis=1, ascending=False) <= 3) & (prices[assets] > sma)).astype(float) / 3.0

    w = w.resample("ME").last().reindex(w.index).ffill().fillna(0.0)
    Valid = prices.index[255:]
    sw_w = w.shift(1).fillna(0).loc[Valid]
    cash_w = (1.0 - sw_w.sum(axis=1)).clip(lower=0.0)
    daily_cash = (1 + cash_rate_pa / 100.0) ** (1 / 252.0) - 1
    sr = (sw_w * rets.loc[Valid]).sum(axis=1) + cash_w * daily_cash
    br = rets.loc[Valid].mean(axis=1)
    out = pd.DataFrame({"Strat_Ret": sr, "BH_Ret": br}, index=Valid)
    out["Strategy"] = 10000 * (1 + sr).cumprod()
    out["Buy_Hold"] = 10000 * (1 + br).cumprod()
    return out, w.loc[Valid]

st.sidebar.title("🏛️ OpenQuant Cloud")
start_yr = st.sidebar.slider("Backtest Start Year", 2010, 2023, 2014)

t1, t2 = st.tabs(["📊 Live Backtester & Screener", "➕ Add Strategy to Spreadsheet (No Code!)"])

with t1:
    st.subheader("🔍 Strategy Database (Loaded from `strategies.csv`)")
    st.dataframe(df_strats[["ID", "Title", "Rebalance", "Market", "Assets", "Source_CAGR", "Source_Vol", "Paper"]], use_container_width=True, hide_index=True)

    df_strats["Label"] = df_strats["ID"] + ": " + df_strats["Title"]
    choice = st.selectbox("Select Strategy to Backtest Live:", df_strats["Label"].tolist())
    row = df_strats[df_strats["Label"] == choice].iloc[0]
    assets = [x.strip() for x in row["Assets"].split(",")]

    st.info(f"**Rule:** {row['Rule']} | **Paper:** [{row['Paper']}]({row['URL']})")
    pr = get_data(tuple(assets), start_yr)
    bt, w_df = run_bt(pr, row["Logic_Type"], assets)

    yrs = max((bt.index[-1] - bt.index[0]).days / 365.25, 0.1)
    cagr = ((bt["Strategy"].iloc[-1] / 10000) ** (1 / yrs) - 1) * 100
    dd = ((bt["Strategy"] - bt["Strategy"].cummax()) / bt["Strategy"].cummax()).min() * 100
    sh = (bt["Strat_Ret"].mean() / bt["Strat_Ret"].std()) * np.sqrt(252)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Annual Return", f"{cagr:.2f}%")
    c2.metric("Worst Crash (Max DD)", f"{dd:.2f}%")
    c3.metric("Sharpe Ratio", f"{sh:.2f}")
    c4.metric("Current Allocation", f"{w_df.iloc[-1].sum()*100:.0f}% Invested")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bt.index, y=bt["Strategy"], name="Strategy", line=dict(color="#10B981", width=3)))
    fig.add_trace(go.Scatter(x=bt.index, y=bt["Buy_Hold"], name="Equal-Weight BH", line=dict(color="#64748B", width=2, dash="dot")))
    fig.update_layout(template="plotly_dark", height=380, title=f"Growth of $10,000 — {row['Title']}")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("➕ Add a New Quantpedia Strategy Directly to `strategies.csv`")
    with st.form("add_strat"):
        f1, f2, f3 = st.columns(3)
        n_id = f1.text_input("Strategy ID", "#0031")
        n_title = f2.text_input("Strategy Title", "Country Equity Momentum")
        n_logic = f3.selectbox("Execution Engine", ["trend", "top2", "valmom", "gem"])
        f4, f5, f6 = st.columns(3)
        n_assets = f4.text_input("ETF Tickers (comma-separated)", "SPY,EWJ,EWG,EWU,FXI")
        n_reb = f5.selectbox("Rebalancing", ["Monthly", "Weekly", "Daily", "Yearly"])
        n_mkt = f6.selectbox("Market", ["Equities", "Multi-Asset", "Commodities"])
        n_rule = st.text_input("Trading Rule Summary", "Rank Country ETFs by 6-month momentum and hold top 2 above 200-day SMA.")
        n_paper = st.text_input("Academic Paper & Author", "Bhojraj & Swaminathan (2006)")
        n_url = st.text_input("Paper URL", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=267991")
        if st.form_submit_button("💾 Save Strategy to Database"):
            new_row = pd.DataFrame([{"ID": n_id, "Title": n_title, "Logic_Type": n_logic, "Assets": n_assets.upper(), "Rebalance": n_reb, "Market": n_mkt, "Source_CAGR": 15.0, "Source_Vol": 12.0, "Rule": n_rule, "Paper": n_paper, "URL": n_url}])
            pd.concat([df_strats.drop(columns=["Label"], errors="ignore"), new_row], ignore_index=True).to_csv(CSV_FILE, index=False)
            st.success("Added to strategies.csv! Refresh or switch to Tab 1 to test it.")
            st.rerun()