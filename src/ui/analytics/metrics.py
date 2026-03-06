import pandas as pd
import streamlit as st
from src.core.logging_setup import logger

@st.cache_data
def calculate_metrics(trades_df, market):
    """Расчёт метрик для аналитики."""
    try:
        total_trades = len(trades_df)
        profitable_trades = len(trades_df[trades_df['profit_percent'] > 0])
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        avg_rr = trades_df['avg_rr'].mean() if not trades_df['avg_rr'].isna().all() else 0
        max_drawdown = (trades_df['profit_percent'].cumsum().min()) if not trades_df.empty else 0
        win_rate_by_timeframe = trades_df[trades_df['profit_percent'] > 0].groupby('timeframe').size() / trades_df.groupby('timeframe').size() * 100
        win_rate_by_timeframe = win_rate_by_timeframe.fillna(0).to_dict()
        logger.info(f"Рассчитаны метрики для {market}: total_trades={total_trades}, win_rate={win_rate:.2f}%")
        return total_trades, win_rate, avg_rr, max_drawdown, win_rate_by_timeframe
    except Exception as e:
        logger.error(f"Ошибка при расчёте метрик для {market}: {str(e)}")
        return 0, 0, 0, 0, {}