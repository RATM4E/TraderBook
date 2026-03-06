import streamlit as st
from src.ui.analytics.ui_components import display_analytics, display_monte_carlo

def crypto_analytics_tab():
    """Вкладка аналитики для криптовалют."""
    lang = st.session_state.get('lang', {})
    display_analytics("Crypto", lang)

def forex_analytics_tab():
    """Вкладка аналитики для форекс."""
    lang = st.session_state.get('lang', {})
    display_analytics("Forex", lang)

def monte_carlo_tab():
    """Вкладка симуляции Монте-Карло."""
    lang = st.session_state.get('lang', {})
    tab1, tab2 = st.tabs([lang.get('crypto_monte_carlo', 'Crypto Monte Carlo'), lang.get('forex_monte_carlo', 'Forex Monte Carlo')])
    with tab1:
        display_monte_carlo("Crypto", lang)
    with tab2:
        display_monte_carlo("Forex", lang)