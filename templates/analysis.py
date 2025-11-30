import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

def render_analysis():
    ticker = st.session_state.selected_stock
    
    # Header with Back Button
    c1, c2 = st.columns([1, 10])
    with c1:
        if st.button("← Back"):
            st.session_state.selected_stock = None
            st.rerun()
    with c2:
        st.title(f"{ticker} Forecast Analysis")

    # --- DATA LOADING ---
    try:
        with st.spinner(f"Fetching data and company profile for {ticker}..."):
            start_date = pd.to_datetime('2015-01-01')
            end_date = pd.to_datetime('today')
            
            # 1. Download Price History
            df = yf.download(ticker, start=start_date, end=end_date)
            
            # 2. Create Ticker Object for Holders Data
            stock_info = yf.Ticker(ticker)
            
            if len(df) == 0:
                st.error("No data found. Please check the ticker symbol.")
                return
                
    except Exception as e:
        st.error(f"Error: {e}")
        return

    # --- DISPLAY METRICS ---
    # Inject CSS to force White Text for Metrics AND Title
    st.markdown("""
        <style>
        /* Force the Page Title (h1) to be white */
        h1 {
            color: #ffffff !important;
        }
        /* Force the Metric Label (e.g. "Current Price") to be light gray */
        [data-testid="stMetricLabel"] {
            color: #e2e8f0 !important;
        }
        /* Force the Metric Value (e.g. "$150.00") to be white */
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    
    if isinstance(current_price, pd.Series): current_price = current_price.item()
    if isinstance(prev_price, pd.Series): prev_price = prev_price.item()
        
    delta = current_price - prev_price
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Price", f"${current_price:.2f}", f"{delta:.2f}")
    
    high_val = df['High'].iloc[-1]
    low_val = df['Low'].iloc[-1]
    m2.metric("High (Today)", f"${high_val.item():.2f}" if hasattr(high_val, 'item') else f"${high_val:.2f}")
    m3.metric("Low (Today)", f"${low_val.item():.2f}" if hasattr(low_val, 'item') else f"${low_val:.2f}")

    st.markdown("---")

    # --- RAW DATA EXPANDER ---
    with st.expander("📊 View Raw Data (Last 5 Days)"):
        st.dataframe(df.tail(), use_container_width=True)

    # --- TABS FOR ANALYSIS ---
    # Added "🏢 Company Info" tab
    tab1, tab2, tab3 = st.tabs(["📈 Technical Charts", "🧠 LSTM Prediction", "🏢 Company Info"])

    with tab1:
        st.subheader("Price History & Moving Averages")
        ma100 = df.Close.rolling(100).mean()
        ma200 = df.Close.rolling(200).mean()

        fig = plt.figure(figsize=(12, 6))
        plt.plot(df.Close, label='Price', alpha=0.5)
        plt.plot(ma100, 'r', label='MA100')
        plt.plot(ma200, 'g', label='MA200')
        plt.legend()
        plt.grid(True, alpha=0.3)
        st.pyplot(fig)

    with tab2:
        st.subheader("Neural Network Prediction")
        
        # --- PREPROCESSING ---
        data_training = pd.DataFrame(df['Close'][0:int(len(df)*0.70)])
        data_testing = pd.DataFrame(df['Close'][int(len(df)*0.70):])

        scaler = MinMaxScaler(feature_range=(0,1))
        data_training_array = scaler.fit_transform(data_training)

        # TRAIN MODEL ON THE FLY
        if st.button("Start LSTM Training"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            x_train, y_train = [], []
            for i in range(100, len(data_training_array)):
                x_train.append(data_training_array[i-100:i])
                y_train.append(data_training_array[i, 0])
            
            x_train, y_train = np.array(x_train), np.array(y_train)

            # Build Model
            model = Sequential()
            model.add(LSTM(units=50, activation='relu', return_sequences=True, input_shape=(x_train.shape[1], 1)))
            model.add(Dropout(0.2))
            model.add(LSTM(units=60, activation='relu', return_sequences=True))
            model.add(Dropout(0.3))
            model.add(LSTM(units=80, activation='relu', return_sequences=True))
            model.add(Dropout(0.4))
            model.add(LSTM(units=120, activation='relu'))
            model.add(Dropout(0.5))
            model.add(Dense(units=1))

            model.compile(optimizer='adam', loss='mean_squared_error')

            # Training Simulation
            epochs = 5
            for i in range(epochs):
                status_text.text(f"Training Model... (Epoch {i+1}/{epochs})")
                model.fit(x_train, y_train, epochs=1, batch_size=32, verbose=0)
                progress_bar.progress(int((i+1)/epochs * 100))
            
            status_text.text("Training Complete!")

            # --- PREDICT ---
            past_100_days = data_training.tail(100)
            final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
            input_data = scaler.transform(final_df)

            x_test, y_test = [], []
            for i in range(100, input_data.shape[0]):
                x_test.append(input_data[i-100: i])
                y_test.append(input_data[i, 0])

            x_test, y_test = np.array(x_test), np.array(y_test)
            y_predicted = model.predict(x_test)

            scale_factor = 1 / scaler.scale_[0]
            y_predicted = y_predicted * scale_factor
            y_test = y_test * scale_factor

            # Plot
            fig2 = plt.figure(figsize=(12,6))
            plt.plot(y_test, 'b', label = 'Original Price')
            plt.plot(y_predicted, 'r', label = 'Predicted Price')
            plt.xlabel('Time')
            plt.ylabel('Price')
            plt.legend()
            st.pyplot(fig2)
        else:
            st.info("Click 'Start LSTM Training' to train a new model for this stock.")

    # --- NEW SECTION: HOLDERS ---
    with tab3:
        st.subheader("👥 Shareholder Structure")
        
        # UI: Dropdown to select the type of data view
        holder_view = st.selectbox(
            "Select Data View",
            [
                "Institutional Holders (Current)", 
                "Mutual Fund Holders (Current)", 
                "Recent Insider Selling (Past Activity)", 
                "Holder Profit/Loss Analysis (Current Holders)",
                "Insider Sales: Opportunity Analysis (If Held)"
            ]
        )
        
        try:
            # OPTION 1: INSTITUTIONAL HOLDERS (CURRENT)
            if holder_view == "Institutional Holders (Current)":
                inst = stock_info.institutional_holders
                if inst is not None and not inst.empty:
                    st.markdown("#### Top Institutional Holders")
                    st.dataframe(inst, use_container_width=True)
                else:
                    st.info("Institutional holder data not available.")

            # OPTION 2: MUTUAL FUND HOLDERS
            elif holder_view == "Mutual Fund Holders (Current)":
                mf = stock_info.mutualfund_holders
                if mf is not None and not mf.empty:
                    st.markdown("#### Top Mutual Fund Holders")
                    st.dataframe(mf, use_container_width=True)
                else:
                    st.info("Mutual Fund holder data not available.")

            # OPTION 3: RECENT INSIDER SELLING (PAST HOLDERS)
            elif holder_view == "Recent Insider Selling (Past Activity)":
                st.markdown("#### 🏃 Recent Insider Sales")
                st.caption("This list shows insiders (executives/directors) who have recently sold shares.")
                
                insider_tx = stock_info.insider_transactions
                if insider_tx is not None and not insider_tx.empty:
                    st.dataframe(insider_tx, use_container_width=True)
                else:
                    st.info("No recent insider transaction data available.")

            # OPTION 4: P&L for CURRENT Holders
            elif holder_view == "Holder Profit/Loss Analysis (Current Holders)":
                st.markdown("##### 📉 P&L Analysis for Current Holders")
                st.caption("Estimates if current institutions are winning or losing based on reporting date.")
                
                inst = stock_info.institutional_holders
                if inst is not None and not inst.empty:
                    analysis_data = []
                    for index, row in inst.iterrows():
                        try:
                            holder_name = row.get('Holder', 'Unknown')
                            report_date = row.get('Date Reported')
                            if report_date:
                                if not isinstance(report_date, pd.Timestamp):
                                    report_date = pd.to_datetime(report_date)
                                if report_date >= df.index[0]:
                                    idx = df.index.get_indexer([report_date], method='nearest')[0]
                                    entry_price = df.iloc[idx]['Close']
                                    if isinstance(entry_price, pd.Series): entry_price = entry_price.item()
                                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                                    status = "🟢 PROFIT" if pnl_pct > 0 else "🔴 LOSS"
                                    analysis_data.append({
                                        "Holder": holder_name,
                                        "Date Reported": report_date.strftime('%Y-%m-%d'),
                                        "Est. Entry Price": f"${entry_price:.2f}",
                                        "Current Price": f"${current_price:.2f}",
                                        "P&L (%)": f"{pnl_pct:.2f}%",
                                        "Status": status
                                    })
                        except Exception:
                            continue
                    
                    if analysis_data:
                        st.dataframe(pd.DataFrame(analysis_data), use_container_width=True)
                    else:
                        st.warning("Could not calculate P&L.")
                else:
                    st.info("No data available.")

            # OPTION 5: P&L for PAST Holders (Insider Sales)
            elif holder_view == "Insider Sales: Opportunity Analysis (If Held)":
                st.markdown("##### 🔮 Hypothetical Analysis: What if they hadn't sold?")
                st.caption("We analyze recent insider SALES. If the stock is higher now than when they sold, they 'missed out' (Opportunity Loss). If lower, they 'avoided loss' (Smart Move).")
                
                insider_tx = stock_info.insider_transactions
                
                if insider_tx is not None and not insider_tx.empty:
                    sales_data = []
                    
                    # Columns usually: ['Start Date', 'Shares', 'Text', 'Value', 'Insider', 'Position'] or similar
                    # We iterate and check for "Sale" context
                    for index, row in insider_tx.iterrows():
                        try:
                            # Try to identify sales based on text description or negative shares (if represented that way)
                            tx_text = str(row.get('Text', '')).lower()
                            
                            # Heuristic: Check if it mentions "Sale" or looking at row structure
                            if 'sale' in tx_text:
                                insider_name = row.get('Insider', 'Unknown')
                                tx_date = row.get('Start Date')
                                
                                if tx_date:
                                    if not isinstance(tx_date, pd.Timestamp):
                                        tx_date = pd.to_datetime(tx_date)
                                    
                                    # Find price on Transaction Date
                                    if tx_date >= df.index[0]:
                                        idx = df.index.get_indexer([tx_date], method='nearest')[0]
                                        sale_price = df.iloc[idx]['Close']
                                        if isinstance(sale_price, pd.Series): sale_price = sale_price.item()
                                        
                                        # Logic:
                                        # If Current > Sale Price: They sold too early (Missed Gain) -> Red
                                        # If Current < Sale Price: They sold at top (Avoided Loss) -> Green
                                        
                                        diff = current_price - sale_price
                                        diff_pct = (diff / sale_price) * 100
                                        
                                        if diff > 0:
                                            outcome = "🔴 Missed Gain" # Stock went up after they sold
                                            meaning = f"Sold at ${sale_price:.2f}, now ${current_price:.2f}"
                                        else:
                                            outcome = "🟢 Avoided Loss" # Stock went down after they sold
                                            meaning = f"Sold at ${sale_price:.2f}, now ${current_price:.2f}"

                                        sales_data.append({
                                            "Insider": insider_name,
                                            "Date Sold": tx_date.strftime('%Y-%m-%d'),
                                            "Sale Price": f"${sale_price:.2f}",
                                            "Current Price": f"${current_price:.2f}",
                                            "Hypothetical Diff": f"{diff_pct:.2f}%",
                                            "Outcome": outcome
                                        })
                        except Exception:
                            continue

                    if sales_data:
                        st.dataframe(pd.DataFrame(sales_data), use_container_width=True)
                    else:
                        st.info("No recent 'Sale' transactions found to analyze.")
                else:
                    st.info("No insider transaction data available.")

        except Exception as e:
            st.warning(f"Unable to fetch holder information: {e}")