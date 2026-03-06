import pandas as pd
import numpy as np
import streamlit as st
from src.core.logging_setup import logger
from src.ui.analytics.data_processing import filter_trades_by_market

@st.cache_data
def monte_carlo_simulation(trades_df, market, iterations=5000, sample_size=None, period=None, trend_tag=None, direction=None, trade_type=None, lang=None):
    """Симуляция Монте-Карло для анализа сделок."""
    try:
        # Фильтрация по рынку
        trades_df = filter_trades_by_market(trades_df, market)
        if trades_df.empty:
            logger.info(f"Нет данных для симуляции Монте-Карло для {market}")
            return None, None, None, None

        # Применение фильтров
        if period:
            end_date = pd.Timestamp.now()
            if period == '1M':
                start_date = end_date - pd.Timedelta(days=30)
            elif period == '3M':
                start_date = end_date - pd.Timedelta(days=90)
            elif period == '1Y':
                start_date = end_date - pd.Timedelta(days=365)
            else:
                start_date = trades_df['entry_date'].min()
            trades_df = trades_df[(trades_df['entry_date'] >= start_date) & (trades_df['entry_date'] <= end_date)]
        
        if trend_tag:
            trades_df = trades_df[trades_df['trend_tag'] == trend_tag]
        if direction:
            trades_df = trades_df[trades_df['type'] == direction]
        if trade_type:
            trades_df = trades_df[trades_df['trade_type'] == trade_type]
        
        if trades_df.empty:
            logger.info(f"Нет данных после фильтрации для симуляции Монте-Карло для {market}")
            return None, None, None, None

        # Определяем размер выборки
        sample_size = sample_size or len(trades_df)
        results = []
        drawdowns = []
        recovery_factors = []
        equity_curves = []

        # Прогресс-бар
        progress_bar = st.progress(0)
        for i in range(iterations):
            sample = trades_df.sample(n=sample_size, replace=True)
            equity = sample['profit_percent'].cumsum()
            max_drawdown = equity.min() if not equity.empty else 0
            final_profit = equity.iloc[-1] if not equity.empty else 0
            recovery_factor = final_profit / abs(max_drawdown) if max_drawdown != 0 else float('inf')
            results.append({
                'trade_setup': sample['trade_setup'].mode().iloc[0] if not sample['trade_setup'].mode().empty else '',
                'timeframe': sample['timeframe'].mode().iloc[0] if not sample['timeframe'].mode().empty else '',
                'final_profit': final_profit,
                'max_drawdown': max_drawdown,
                'recovery_factor': recovery_factor
            })
            drawdowns.append(max_drawdown)
            recovery_factors.append(recovery_factor)
            if i < 10:  # Сохраняем 10 кривых эквити для визуализации
                equity_curves.append(equity.values)
            progress_bar.progress((i + 1) / iterations)

        results_df = pd.DataFrame(results)
        # Определяем оптимальные стратегии
        optimal_profit = results_df.groupby(['trade_setup', 'timeframe'])['final_profit'].mean().idxmax()
        optimal_drawdown = results_df.groupby(['trade_setup', 'timeframe'])['max_drawdown'].mean().idxmax()
        optimal_balanced = results_df.groupby(['trade_setup', 'timeframe'])['recovery_factor'].mean().idxmax()
        
        optimal_results = {
            'max_profit': optimal_profit,
            'min_drawdown': optimal_drawdown,
            'balanced': optimal_balanced
        }
        
        logger.info(f"Монте-Карло для {market}: оптимальная стратегия по прибыли {optimal_profit}")
        return results_df, drawdowns, recovery_factors, optimal_results, equity_curves
    except Exception as e:
        logger.error(f"Ошибка симуляции Монте-Карло для {market}: {str(e)}")
        return None, None, None, None, None