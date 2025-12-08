# demo/app.py
import streamlit as st
from main_orchestrator import TradlOrchestrator
import os

# Page config – beautiful title & icon
st.set_page_config(
    page_title="Secure Financial Copilot",
    page_icon="",
    layout="centered"
)

# Custom CSS for finance dark vibe
st.markdown("""
<style>
    .main {background-color: #0a0a0f; color: white;}
    .stTextInput > div > div > input {background-color: #1a1a2e; color: white; border: 1px solid #00d4aa;}
    .stButton>button {background-color: #00d4aa; color: black; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("")
st.markdown("##### Agentic Financial Copilot – News-grounded • Secure • Multilingual")

# Initialize orchestrator once
@st.cache_resource
def get_orchestrator():
    return TradlOrchestrator()

orch = get_orchestrator()

# Input section
col1, col2 = st.columns([3,1])
with col1:
    query = st.text_input(
        "Ask anything in English/Hindi",
        placeholder="e.g. Generate RSI strategy for HDFC or RBI policy का impact HDFC पर",
        value="Generate RSI strategy for HDFC"
    )
with col2:
    ticker = st.text_input("Ticker", value="HDFC.NS", max_chars=15)

if st.button("Run Copilot", type="primary", use_container_width=True):
    if not query.strip() or not ticker.strip():
        st.error("Query aur ticker dono भरना ज़रूरी है!")
    else:
        with st.spinner("Secure agents processing news + backtest..."):
            try:
                response = orch.copilot_query(query, ticker, user_id="streamlit-user")
                st.markdown("### Copilot Response")
                st.markdown(response)
            except Exception as e:
                st.error(f"Error: {str(e)} – Check your API keys in Secrets?")

# Footer
st.markdown("---")
st.caption("Built with LangGraph • 7 Autonomous Agents • JWT + Fernet Security • Live on Streamlit Cloud")
