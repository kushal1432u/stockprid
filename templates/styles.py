import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* General App Styling */
        .stApp {
            background-color: #0b0f19;
        }

        /* --- ANIMATED BORDER WRAPPER --- */
        /* This container holds the spinning border and the card */
        .stock-card-wrapper {
            position: relative;
            border-radius: 14px;
            padding: 2px; /* This determines border width */
            overflow: hidden;
            margin-bottom: 10px;
            height: 200px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease-in-out;
        }

        .stock-card-wrapper:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px -3px rgba(0, 0, 0, 0.4);
        }

        /* The Spinning Animation Layer */
        .stock-card-wrapper::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            z-index: 0;
            animation: spin 3s linear infinite;
        }

        /* BORDER COLORS (Conic Gradients) */
        .border-green::before {
            background: conic-gradient(transparent 270deg, #4ade80, transparent);
        }
        .border-red::before {
            background: conic-gradient(transparent 270deg, #ef4444, transparent);
        }
        .border-yellow::before {
            background: conic-gradient(transparent 270deg, #eab308, transparent);
        }

        /* THE ACTUAL CARD CONTENT (Sits on top of the spinner) */
        .stock-card-inner {
            position: relative;
            z-index: 1;
            border-radius: 12px; /* Slightly smaller than wrapper */
            height: 100%;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            color: white;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* --- EXISTING CARD CONTENT STYLES --- */
        .card-header {
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            font-weight: 600;
            opacity: 0.9;
        }
        .status-badge {
            background: rgba(255,255,255,0.2);
            padding: 2px 6px;
            border-radius: 4px;
        }
        
        .card-content {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 5px;
        }
        
        .stock-icon {
            background: white;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            overflow: hidden;
            padding: 2px;
            flex-shrink: 0;
        }
        .stock-icon img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }

        .stock-ticker { font-size: 16px; font-weight: 800; line-height: 1.2; }
        .stock-name { font-size: 11px; opacity: 0.9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 120px; }

        .price-section {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-top: 10px;
            background: rgba(0,0,0,0.15);
            padding: 8px;
            border-radius: 8px;
        }
        
        .current-price { font-size: 18px; font-weight: bold; font-family: monospace; }
        .price-change { font-size: 11px; font-weight: 600; }
        .text-green { color: #86efac; }
        .text-red { color: #fca5a5; }
        .text-yellow { color: #fde047; }

        .mini-chart { width: 80px; height: 30px; display: flex; align-items: center; justify-content: center; }

        .card-footer {
            display: flex;
            justify-content: space-between;
            font-size: 9px;
            margin-top: 8px;
            opacity: 0.7;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 6px;
        }

        /* Button Tweaks */
        div.stButton > button {
            background-color: #1f2937;
            color: white;
            border: 1px solid #374151;
            margin-top: -10px;
        }
        div.stButton > button:hover {
            border-color: #60a5fa;
            color: #60a5fa;
        }
    </style>
    """, unsafe_allow_html=True)