import streamlit as st
from src.ui.sidebar import setup_sidebar
from src.ui.trade_input import trade_input_tab
from src.ui.trade_list import list_tab
from src.ui.setups import setups_tab
from src.ui.analytics.tabs import crypto_analytics_tab, forex_analytics_tab, monte_carlo_tab
from src.core.file_manager import initialize_files
from src.ui.translations import load_translations
from src.core.logging_setup import logger
import os
from src.core.config import TIMEZONE_FILE, LANGUAGE_FILE, REWARD_RISK_FILE

def main():
    try:
        st.set_page_config(page_title="TraderBook", layout="wide")
        initialize_files()
        translations = load_translations()
        if 'language' not in st.session_state:
            try:
                with open(LANGUAGE_FILE, 'r') as f:
                    st.session_state.language = f.read().strip()
            except:
                st.session_state.language = 'ru'
        st.session_state.lang = translations.get(st.session_state.language, translations['ru'])
        if 'timezone' not in st.session_state:
            try:
                with open(TIMEZONE_FILE, 'r') as f:
                    st.session_state.timezone = int(f.read().strip())
            except:
                st.session_state.timezone = 0
        if 'show_close_warning' not in st.session_state:
            st.session_state.show_close_warning = False
        setup_sidebar()
        st.title(st.session_state.lang.get('app_title', 'TraderBook'))
        tab_names = [
            st.session_state.lang.get('crypto_trades', 'Crypto Trades'),
            st.session_state.lang.get('forex_trades', 'Forex Trades'),
            st.session_state.lang.get('trade_list', 'Trade List'),
            st.session_state.lang.get('setups', 'Setups'),
            st.session_state.lang.get('crypto_analytics', 'Crypto Analytics'),
            st.session_state.lang.get('forex_analytics', 'Forex Analytics'),
            st.session_state.lang.get('monte_carlo', 'Monte Carlo Simulation')
        ]
        tabs = st.tabs(tab_names)
        with tabs[0]:
            trade_input_tab("Crypto")
        with tabs[1]:
            trade_input_tab("Forex")
        with tabs[2]:
            list_tab()
        with tabs[3]:
            setups_tab()
        with tabs[4]:
            crypto_analytics_tab()
        with tabs[5]:
            forex_analytics_tab()
        with tabs[6]:
            monte_carlo_tab()
    except Exception as e:
        logger.error(f"Ошибка в главном приложении: {str(e)}")
        st.error(f"{st.session_state.lang.get('error', 'Произошла ошибка')}: {str(e)}")

if __name__ == "__main__":
    main()