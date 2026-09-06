
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="蔥明錢 Lite",
    page_icon="🧅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Lightweight CSS
# -----------------------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background:#08111a;
    color:#eef5f9;
}
[data-testid="stHeader"], [data-testid="stToolbar"] {display:none;}
.block-container {
    padding:.45rem .55rem .8rem .55rem;
    max-width:100%;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background:#0d1822;
    border:1px solid #223442;
    border-radius:12px;
}
.stButton button {
    min-height:42px;
    border-radius:9px;
    font-weight:800;
    border:1px solid #2a4152;
    background:#10202c;
    color:#f2f7fb;
}
[data-testid="stDataFrame"] {
    border:1px solid #223442;
    border-radius:9px;
}
.brand {
    font-size:28px;
    font-weight:900;
    padding:2px 4px 8px 4px;
}
.sub {
    color:#73889a;
    font-size:13px;
    margin-left:8px;
}
.cardgrid {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:8px;
}
.card {
    background:#111f2a;
    border:1px solid #223544;
    border-radius:9px;
    padding:9px 10px;
    min-height:56px;
}
.card .k {font-size:12px;color:#8094a4;}
.card .v {font-size:20px;font-weight:850;margin-top:3px;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Demo OHLC (cached once)
# -----------------------------
@st.cache_data(show_spinner=False)
def make_data(n=320, seed=12):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0007, 0.012, n)
    close = 450 * np.cumprod(1 + r)
    close = close / close[-1] * 525

    open_ = np.r_[close[0], close[:-1] * (1 + rng.normal(0, .0025, n-1))]
    high = np.maximum(open_, close) * (1 + rng.uniform(.002, .011, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(.002, .011, n))
    dates = pd.date_range("2023-01-02", periods=n, freq="B")
    return pd.DataFrame({
        "Date": dates,
        "Open": open_,
        "High": high,
        "Low": low,
        "Close": close
    })

df = make_data()

# -----------------------------
# State
# -----------------------------
if "i" not in st.session_state:
    st.session_state.i = 90
    st.session_state.pos = 0
    st.session_state.entry = None
    st.session_state.entry_time = None
    st.session_state.qty = 1
    st.session_state.trades = []

def now():
    return df.iloc[st.session_state.i]

def open_position(side, reasons):
    if st.session_state.pos != 0:
        close_position("Reverse", reasons)
    r = now()
    st.session_state.pos = side
    st.session_state.entry = float(r.Close)
    st.session_state.entry_time = r.Date

def close_position(exit_type="Manual", reasons=None):
    if st.session_state.pos == 0:
        return
    r = now()
    px = float(r.Close)
    pnl_pct = ((px - st.session_state.entry) / st.session_state.entry) * st.session_state.pos * 100
    pnl_cash = pnl_pct / 100 * st.session_state.entry * st.session_state.qty

    st.session_state.trades.append({
        "#": len(st.session_state.trades) + 1,
        "時間": st.session_state.entry_time.strftime("%m-%d"),
        "方向": "多" if st.session_state.pos == 1 else "空",
        "進場": round(st.session_state.entry, 2),
        "出場": round(px, 2),
        "數量": st.session_state.qty,
        "損益": round(pnl_cash, 0),
        "R": round(pnl_pct / 3.0, 2),
        "理由": "、".join(reasons or [])
    })
    st.session_state.pos = 0
    st.session_state.entry = None
    st.session_state.entry_time = None

# -----------------------------
# Header
# -----------------------------
st.markdown(
    '<div class="brand">🧅 蔥明錢 <span class="sub">Lite｜交易訓練模式</span></div>',
    unsafe_allow_html=True
)

left, right = st.columns([2.55, 7.45], gap="small")

# -----------------------------
# LEFT PANEL
# -----------------------------
with left:
    with st.container(border=True):
        a,b,c = st.columns([1,1,2])
        if a.button("▶", use_container_width=True):
            st.session_state.i = min(len(df)-1, st.session_state.i + 1)
            st.rerun()
        if b.button("⏩", use_container_width=True):
            st.session_state.i = min(len(df)-1, st.session_state.i + 5)
            st.rerun()
        speed = c.selectbox(
            "速度", ["1x","2x","4x"],
            label_visibility="collapsed"
        )

        st.markdown("### 交易操作")

        reasons = st.multiselect(
            "交易理由",
            ["趨勢","回撤","突破","支撐","壓力","均線","RSI","OB","BOS","Liquidity Sweep","其他"],
            placeholder="選擇交易理由"
        )

        buy, sell = st.columns(2)
        if buy.button("⬆\n買入 BUY\n做多", use_container_width=True):
            open_position(1, reasons)
            st.rerun()
        if sell.button("⬇\n賣出 SELL\n放空", use_container_width=True):
            open_position(-1, reasons)
            st.rerun()

        c1,c2,c3 = st.columns(3)
        if c1.button("✕ 平倉", use_container_width=True):
            close_position("Manual", reasons)
            st.rerun()
        c2.button("＋ 加碼", use_container_width=True)
        c3.button("－ 減碼", use_container_width=True)

        q1,q2 = st.columns(2)
        order_type = q1.selectbox("委託", ["市價","限價"])
        qty = q2.number_input("數量", min_value=1, value=st.session_state.qty, step=1)
        st.session_state.qty = int(qty)

        sl1, tp1 = st.columns(2)
        sl1.number_input("SL %（選填）", min_value=0.0, step=.1)
        tp1.number_input("TP %（選填）", min_value=0.0, step=.1)

        status = "FLAT" if st.session_state.pos == 0 else ("LONG" if st.session_state.pos == 1 else "SHORT")
        px = float(now().Close)
        if st.session_state.pos != 0:
            unreal = ((px - st.session_state.entry) / st.session_state.entry) * st.session_state.pos * 100
            st.caption(f"部位：{status} ｜ 未實現：{unreal:+.2f}%")
        else:
            st.caption("部位：FLAT")

# -----------------------------
# MAIN CHART
# -----------------------------
with right:
    with st.container(border=True):
        r = now()
        h1,h2,h3 = st.columns([2.1,1.2,4.7])
        h1.markdown("### 2330 台積電")
        h2.markdown(f"**{r.Date.date()}**")
        h3.markdown(
            f"開 {r.Open:.0f}　高 {r.High:.0f}　低 {r.Low:.0f}　收 **{r.Close:.0f}**"
        )

        # Render only most recent bars -> much faster
        window = 120
        start = max(0, st.session_state.i - window + 1)
        vis = df.iloc[start:st.session_state.i+1]

        fig = go.Figure(go.Candlestick(
            x=vis.Date,
            open=vis.Open,
            high=vis.High,
            low=vis.Low,
            close=vis.Close
        ))
        fig.update_layout(
            height=500,
            margin=dict(l=3,r=3,t=2,b=2),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_rangeslider_visible=False,
            showlegend=False,
            font=dict(color="#aebdca", size=11),
            xaxis=dict(gridcolor="#172a37", nticks=7),
            yaxis=dict(gridcolor="#172a37", side="right"),
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "staticPlot": False
            }
        )

# -----------------------------
# LOWER SECTION
# -----------------------------
tcol, scol = st.columns([6.5,3.5], gap="small")

with tcol:
    with st.container(border=True):
        st.markdown("### 交易筆記")
        trades = pd.DataFrame(st.session_state.trades)
        if trades.empty:
            st.caption("尚無已完成交易。完成第一筆平倉後會自動出現在這裡。")
        else:
            st.dataframe(
                trades.iloc[::-1],
                use_container_width=True,
                hide_index=True,
                height=205
            )

with scol:
    with st.container(border=True):
        st.markdown("### 交易統計")
        trades = pd.DataFrame(st.session_state.trades)

        if trades.empty:
            total = 0
            wr = 0
            count = 0
            avg_r = 0
            best = 0
            worst = 0
        else:
            total = float(trades["損益"].sum())
            wr = float((trades["損益"] > 0).mean() * 100)
            count = len(trades)
            avg_r = float(trades["R"].mean())
            best = float(trades["損益"].max())
            worst = float(trades["損益"].min())

        cards = f"""
        <div class="cardgrid">
          <div class="card"><div class="k">總損益</div><div class="v">{total:+,.0f}</div></div>
          <div class="card"><div class="k">勝率</div><div class="v">{wr:.0f}%</div></div>
          <div class="card"><div class="k">交易次數</div><div class="v">{count}</div></div>
          <div class="card"><div class="k">平均 R</div><div class="v">{avg_r:.2f}</div></div>
          <div class="card"><div class="k">最大獲利</div><div class="v">{best:+,.0f}</div></div>
          <div class="card"><div class="k">最大虧損</div><div class="v">{worst:+,.0f}</div></div>
        </div>
        """
        st.markdown(cards, unsafe_allow_html=True)
