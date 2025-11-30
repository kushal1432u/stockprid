import streamlit as st
import numpy as np
import yfinance as yf
import pandas as pd
import datetime

# --- HELPER: GENERATE MINI GRAPH ---
def make_sparkline(data_list, color="#ffffff", width=80, height=30):
    if len(data_list) < 2:
        return ""
    min_val = min(data_list)
    max_val = max(data_list)
    range_val = max_val - min_val if max_val != min_val else 1
    points = []
    for i, val in enumerate(data_list):
        x = (i / (len(data_list) - 1)) * width
        y = height - ((val - min_val) / range_val) * height
        points.append(f"{x},{y}")
    polyline_points = " ".join(points)
    return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity: 0.8;"><polyline points="{polyline_points}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# --- HELPER: FETCH LIVE DATA ---
@st.cache_data(ttl=60)
def fetch_overview_data(tickers):
    try:
        data = yf.download(tickers, period="5d", interval="5m", group_by='ticker', progress=False)
        return data
    except Exception:
        return None

def render_home():
    st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🚀 AI Stock Prediction Spaces</h1>", unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Live Prices", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

    STOCKS = [
        {"ticker": "AAPL", "name": "Apple Intelligence", "desc": "Consumer Electronics", "gradient": "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)", "logo": "https://logo.clearbit.com/apple.com"},
        {"ticker": "TSLA", "name": "Tesla Autopilot", "desc": "EV & Robotics", "gradient": "linear-gradient(135deg, #dc2626 0%, #991b1b 100%)", "logo": "https://logo.clearbit.com/tesla.com"},
        {"ticker": "NVDA", "name": "NVIDIA AI", "desc": "Semiconductors & GPUs", "gradient": "linear-gradient(135deg, #059669 0%, #047857 100%)", "logo": "https://logo.clearbit.com/nvidia.com"},
        {"ticker": "GOOGL", "name": "Alphabet DeepMind", "desc": "Search & AI", "gradient": "linear-gradient(135deg, #d97706 0%, #b45309 100%)", "logo": "https://logo.clearbit.com/google.com"},
        {"ticker": "MSFT", "name": "Microsoft Azure", "desc": "Cloud & Enterprise", "gradient": "linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)", "logo": "https://logo.clearbit.com/microsoft.com"},
        {"ticker": "AMZN", "name": "Amazon AWS", "desc": "E-Commerce", "gradient": "linear-gradient(135deg, #db2777 0%, #be185d 100%)", "logo": "https://logo.clearbit.com/amazon.com"},
        {"ticker": "META", "name": "Meta Llama", "desc": "Social & Metaverse", "gradient": "linear-gradient(135deg, #0891b2 0%, #0e7490 100%)", "logo": "https://logo.clearbit.com/meta.com"},
        {"ticker": "NFLX", "name": "Netflix Stream", "desc": "Entertainment", "gradient": "linear-gradient(135deg, #ca8a04 0%, #a16207 100%)", "logo": "https://logo.clearbit.com/netflix.com"},
        {"ticker": "BTC-USD", "name": "Bitcoin Core", "desc": "Cryptocurrency", "gradient": "linear-gradient(135deg, #ea580c 0%, #c2410c 100%)", "logo": "https://logo.clearbit.com/bitcoin.org"},
        {"ticker": "RELIANCE.NS", "name": "Reliance Ind", "desc": "Conglomerate", "gradient": "linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)", "logo": "https://logo.clearbit.com/ril.com"},
        {"ticker": "TCS.NS", "name": "Tata CS", "desc": "IT Services", "gradient": "linear-gradient(135deg, #0d9488 0%, #0f766e 100%)", "logo": "https://logo.clearbit.com/tcs.com"},
        {"ticker": "HDFCBANK.NS", "name": "HDFC Bank", "desc": "Finance & Banking", "gradient": "linear-gradient(135deg, #be123c 0%, #9f1239 100%)", "logo": "https://logo.clearbit.com/hdfcbank.com"},
    ]

    ticker_list = [s['ticker'] for s in STOCKS]
    with st.spinner("Connecting to Live Market Data (5m Interval)..."):
        market_data = fetch_overview_data(ticker_list)

    cols = st.columns(4)
    
    for i, stock in enumerate(STOCKS):
        ticker = stock['ticker']
        col = cols[i % 4]
        
        # Default values
        current_price = "Loading..."
        pct_change = 0.0
        sparkline_svg = ""
        last_update_str = ""
        
        # Logic to fetch real data
        if market_data is not None and not market_data.empty:
            try:
                if len(ticker_list) > 1:
                    stock_hist = market_data[ticker]['Close']
                else:
                    stock_hist = market_data['Close']
                
                stock_hist = stock_hist.dropna()
                if not stock_hist.empty:
                    last_price = stock_hist.iloc[-1]
                    prev_price = stock_hist.iloc[-2]
                    pct_change = ((last_price - prev_price) / prev_price) * 100
                    current_price = f"${last_price:.2f}"
                    sparkline_svg = make_sparkline(stock_hist.tolist()[-50:])
                    last_time = stock_hist.index[-1]
                    last_update_str = last_time.strftime("%H:%M")
            except Exception:
                pass

        if current_price == "Loading...":
             current_price = "---"

        # --- DETERMINE STATUS COLOR & BORDER ---
        if pct_change < -0.05: # DOWN
            arrow = "▼"
            text_color_class = "text-red"
            border_class = "border-red"
        elif pct_change > 0.05: # UP
            arrow = "▲"
            text_color_class = "text-green"
            border_class = "border-green"
        else: # STATIC (Between -0.05 and 0.05)
            arrow = "●"
            text_color_class = "text-yellow"
            border_class = "border-yellow"

        # Construct HTML string (New Wrapper Structure)
        html_code = f"""
        <div class="stock-card-wrapper {border_class}">
            <div class="stock-card-inner" style="background: {stock['gradient']};">
                <div class="card-header">
                    <span class="status-badge">● Live {last_update_str}</span>
                    <span class="heart-icon">🤍 {np.random.randint(50, 500)}</span>
                </div>
                <div class="card-content">
                    <div class="stock-icon">
                        <img src="{stock['logo']}" alt="logo">
                    </div>
                    <div class="stock-info">
                        <div class="stock-ticker">{stock['ticker']}</div>
                        <div class="stock-name">{stock['name']}</div>
                    </div>
                </div>
                <div class="price-section">
                    <div class="price-info">
                        <div class="current-price">{current_price}</div>
                        <div class="price-change {text_color_class}">{arrow} {abs(pct_change):.2f}%</div>
                    </div>
                    <div class="mini-chart">
                        {sparkline_svg}
                    </div>
                </div>
                <div class="card-footer">
                    <span class="author">🤖 LSTM Model</span>
                </div>
            </div>
        </div>
        """

        with col:
            st.markdown(html_code, unsafe_allow_html=True)
            if st.button(f"Analyze {stock['ticker']}", key=f"btn_{stock['ticker']}", use_container_width=True):
                st.session_state.selected_stock = stock['ticker']
                st.rerun()

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #6b7280;'>Or search for a specific ticker</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        custom_input = st.text_input("Search Ticker", placeholder="e.g. SHOP, UBER, ZOMATO.NS", label_visibility="collapsed")
        if st.button("Search Custom Ticker", use_container_width=True):
            if custom_input:
                st.session_state.selected_stock = custom_input.upper()
                st.rerun()