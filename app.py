import streamlit as st
# Import the functions from your templates folder
from templates.styles import apply_custom_css
from templates.home import render_home
from templates.analysis import render_analysis

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NeuroStock Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- APPLY CSS ---
apply_custom_css()

# --- STATE MANAGEMENT ---
# This keeps track of which stock you clicked
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# --- MAIN ROUTING LOGIC ---
if __name__ == "__main__":
    # If no stock is selected, show the Home Grid
    if st.session_state.selected_stock is None:
        render_home()
    # If a stock is selected, show the Analysis/Charts
    else:
        render_analysis()