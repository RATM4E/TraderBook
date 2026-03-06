import os
import streamlit as st
import plotly.express as px
import pandas as pd
from src.core.data_manager import load_trades
from src.core.logging_setup import logger
from src.ui.analytics.data_processing import filter_trades_by_market, prepare_time_histogram_data, prepare_day_of_week_data
from src.ui.analytics.metrics import calculate_metrics
from src.ui.analytics.monte_carlo import monte_carlo_simulation
from src.ui.analytics.plotting import (
    plot_time_histogram, plot_rr_histogram, plot_setup_tf_heatmap,
    plot_trend_tag_bar, plot_direction_bar, plot_session_histogram,
    plot_trade_type_histogram, plot_day_of_week_histogram, plot_calendar_heatmap,
    plot_monte_carlo_equity, plot_monte_carlo_drawdown_histogram, plot_monte_carlo_heatmap
)
from src.ui.export_pdf import export_monte_carlo_to_pdf
from datetime import datetime

def display_analytics(market, lang):
    """Отображение аналитики для указанного рынка."""
    try:
        timezone = st.session_state.get('timezone', 0)
        trades_df = load_trades()
        market_trades = filter_trades_by_market(trades_df, market)
        total_trades, win_rate, avg_rr, max_drawdown, win_rate_by_timeframe = calculate_metrics(market_trades, market)

        if market_trades.empty:
            st.write(lang.get('no_profitable_trades', 'Нет данных'))
            logger.info(f"Нет сделок для аналитики {market}")
            return

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label=lang.get('total_trades', 'Общее количество сделок'), value=total_trades)
        with col2:
            st.metric(label=lang.get('win_rate', 'Винрейт'), value=f"{win_rate:.2f}%")
        with col3:
            st.metric(label=lang.get('avg_rr', 'Средний RR'), value=f"{avg_rr:.2f}")
        with col4:
            st.metric(label=lang.get('max_drawdown', 'Максимальная просадка'), value=f"{max_drawdown:.2f}%")

        with st.expander(label=lang.get('win_rate_by_timeframe', 'Винрейт по таймфреймам'), expanded=True):
            for tf, rate in sorted(win_rate_by_timeframe.items()):
                st.write(f"{tf}: {rate:.2f}%")

        fig = px.line(
            data_frame=market_trades.sort_values('entry_date'),
            x='entry_date',
            y=market_trades['profit_percent'].cumsum(),
            title=lang.get('equity_curve', 'Кривая эквити'),
            color_discrete_sequence=['#4682B4']
        )
        fig.update_layout(
            xaxis_title=lang.get('date', 'Дата'),
            yaxis_title=lang.get('profit_percent', 'Прибыль, %'),
            plot_bgcolor='#F5F6F5',
            paper_bgcolor='#F5F6F5',
            font=dict(family='Arial', size=12, color='#333333'),
            xaxis=dict(gridcolor='#D3D3D3'),
            yaxis=dict(gridcolor='#D3D3D3')
        )
        st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_equity_curve")

        grouped = market_trades.groupby('pair')['profit_percent'].sum().reset_index()
        fig = px.bar(
            data_frame=grouped,
            x='pair',
            y='profit_percent',
            title=lang.get('profit_by_pair', 'Прибыль по парам'),
            color_discrete_sequence=['#4682B4']
        )
        fig.update_layout(
            xaxis_title=lang.get('pair', 'Пара'),
            yaxis_title=lang.get('profit_percent', 'Прибыль, %'),
            plot_bgcolor='#F5F6F5',
            paper_bgcolor='#F5F6F5',
            font=dict(family='Arial', size=12, color='#333333'),
            xaxis=dict(gridcolor='#D3D3D3'),
            yaxis=dict(gridcolor='#D3D3D3')
        )
        st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_profit_by_pair")

        fig = px.histogram(
            data_frame=market_trades,
            x='profit_percent',
            nbins=20,
            title=lang.get('profit_distribution', 'Распределение прибыли'),
            color_discrete_sequence=['#4682B4'],
            opacity=0.7
        )
        fig.update_layout(
            xaxis_title=lang.get('profit_percent', 'Прибыль, %'),
            yaxis_title=lang.get('count', 'Количество'),
            plot_bgcolor='#F5F6F5',
            paper_bgcolor='#F5F6F5',
            font=dict(family='Arial', size=12, color='#333333'),
            xaxis=dict(gridcolor='#D3D3D3'),
            yaxis=dict(gridcolor='#D3D3D3')
        )
        st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_profit_distribution")

        grouped = market_trades.groupby(['trade_setup', 'timeframe'])['profit_percent'].sum().reset_index()
        best_combination = grouped.loc[grouped['profit_percent'].idxmax()] if not grouped.empty else None
        fig = px.bar(
            data_frame=grouped,
            x='timeframe',
            y='profit_percent',
            color='trade_setup',
            title=lang.get('profit_by_setup_tf', 'Прибыль по сетапам и таймфреймам'),
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(
            xaxis_title=lang.get('timeframe', 'Таймфрейм'),
            yaxis_title=lang.get('profit_percent', 'Прибыль, %'),
            plot_bgcolor='#F5F6F5',
            paper_bgcolor='#F5F6F5',
            font=dict(family='Arial', size=12, color='#333333'),
            xaxis=dict(gridcolor='#D3D3D3'),
            yaxis=dict(gridcolor='#D3D3D3'),
            legend_title=lang.get('trade_setup', 'Сетап')
        )
        st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_profit_by_setup_tf")
        if best_combination is not None:
            st.write(lang.get('best_combination', 'Лучшая комбинация') + f": {best_combination['trade_setup']} ({best_combination['timeframe']}): {best_combination['profit_percent']:.2f}%")

        with st.expander(label=lang.get('time_charts', 'Графики по времени'), expanded=False):
            if st.checkbox(label=lang.get('show_time_histogram', 'Показать гистограмму времени'), key=f"{market}_check_time_histogram"):
                time_data = prepare_time_histogram_data(market_trades, timezone, lang)
                fig = plot_time_histogram(time_data, market, lang)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_time_histogram")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))
            if st.checkbox(label=lang.get('show_day_of_week_histogram', 'Показать гистограмму дней недели'), key=f"{market}_check_day_of_week_histogram"):
                day_data = prepare_day_of_week_data(market_trades, timezone, lang)
                fig, _ = plot_day_of_week_histogram(day_data, market, lang)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_day_of_week_histogram")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))
            if st.checkbox(label=lang.get('show_calendar_heatmap', 'Показать календарную тепловую карту'), key=f"{market}_check_calendar_heatmap"):
                metric = st.selectbox(
                    label=lang.get('calendar_metric', 'Выберите метрику'),
                    options=[lang.get('calendar_metric_count', 'Количество сделок'), lang.get('calendar_metric_profit', 'Прибыльность')],
                    key=f"{market}_select_calendar_metric"
                )
                fig = plot_calendar_heatmap(market_trades, market, lang, timezone, metric)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_calendar_heatmap")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))

        with st.expander(label=lang.get('setup_charts', 'Графики по сетапам'), expanded=False):
            if st.checkbox(label=lang.get('show_setup_tf_heatmap', 'Показать тепловую карту сетапов'), key=f"{market}_check_setup_tf_heatmap"):
                limit_top_10 = st.checkbox(
                    label=lang.get('limit_top_10_setups', 'Ограничить топ-10 сетапами'),
                    key=f"{market}_check_limit_top_10"
                )
                fig = plot_setup_tf_heatmap(market_trades, market, lang, limit_top_10)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_setup_tf_heatmap")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))
            if st.checkbox(label=lang.get('show_trend_tag_bar', 'Показать график тегов тренда'), key=f"{market}_check_trend_tag_bar"):
                fig = plot_trend_tag_bar(market_trades, market, lang)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_trend_tag_bar")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))

        with st.expander(label=lang.get('trade_charts', 'Графики по сделкам'), expanded=False):
            if st.checkbox(label=lang.get('show_rr_histogram', 'Показать гистограмму RR'), key=f"{market}_check_rr_histogram"):
                fig = plot_rr_histogram(market_trades, market, lang)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"{market}_plot_rr_histogram")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))
            if st.checkbox(label=lang.get('show_direction_bar', 'Показать график направления'), key=f"{market}_check_direction_bar"):
                fig_count, fig_profit = plot_direction_bar(market_trades, market, lang)
                if fig_count and fig_profit:
                    st.plotly_chart(fig_count, use_container_width=True, key=f"{market}_plot_direction_bar_count")
                    st.plotly_chart(fig_profit, use_container_width=True, key=f"{market}_plot_direction_bar_profit")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))
            if st.checkbox(label=lang.get('show_session_histogram', 'Показать гистограмму сессий'), key=f"{market}_check_session_histogram"):
                fig_count, fig_profit = plot_session_histogram(market_trades, market, lang)
                if fig_count and fig_profit:
                    st.plotly_chart(fig_count, use_container_width=True, key=f"{market}_plot_session_histogram_count")
                    st.plotly_chart(fig_profit, use_container_width=True, key=f"{market}_plot_session_histogram_profit")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))
            if st.checkbox(label=lang.get('show_trade_type_histogram', 'Показать гистограмму типов сделок'), key=f"{market}_check_trade_type_histogram"):
                fig_count, fig_profit = plot_trade_type_histogram(market_trades, market, lang)
                if fig_count and fig_profit:
                    st.plotly_chart(fig_count, use_container_width=True, key=f"{market}_plot_trade_type_histogram_count")
                    st.plotly_chart(fig_profit, use_container_width=True, key=f"{market}_plot_trade_type_histogram_profit")
                else:
                    st.error(lang.get('no_profitable_trades', 'Нет данных'))

    except Exception as e:
        logger.error(f"Ошибка отображения аналитики для {market}: {str(e)}")
        st.error(lang.get('error_displaying_analytics', 'Ошибка отображения аналитики') + f": {str(e)}")

def display_monte_carlo(market, lang):
    """Отображение симуляции Монте-Карло для указанного рынка."""
    try:
        trades_df = load_trades()
        market_trades = filter_trades_by_market(trades_df, market)
        if market_trades.empty:
            st.write(lang.get('no_profitable_trades', 'Нет данных'))
            logger.info(f"Нет сделок для симуляции Монте-Карло {market}")
            return

        st.subheader(lang.get('monte_carlo_simulation', 'Симуляция Монте-Карло'))

        # Инициализация session_state для хранения результатов
        if f"{market}_monte_carlo_results" not in st.session_state:
            st.session_state[f"{market}_monte_carlo_results"] = None

        # Фильтры
        with st.expander(lang.get('filters', 'Фильтры'), expanded=True):
            period = st.selectbox(
                label=lang.get('period', 'Период'),
                options=['Все время', '1 месяц', '3 месяца', '1 год'],
                key=f"{market}_monte_carlo_period"
            )
            period_map = {'Все время': None, '1 месяц': '1M', '3 месяца': '3M', '1 год': '1Y'}
            trend_tag = st.selectbox(
                label=lang.get('trend_tag', 'Тег тренда'),
                options=[None] + ['Трендовая', 'Контртрендовая', 'Баланс/Флет'],
                key=f"{market}_monte_carlo_trend_tag"
            )
            direction = st.selectbox(
                label=lang.get('direction', 'Направление'),
                options=[None, 'Long', 'Short'],
                key=f"{market}_monte_carlo_direction"
            )
            trade_type = st.selectbox(
                label=lang.get('trade_type', 'Тип сделки'),
                options=[None, 'Scalp', 'Intraday', 'Swing'],
                key=f"{market}_monte_carlo_trade_type"
            )

        # Запуск симуляции
        if st.button(lang.get('run_simulation', 'Запустить симуляцию'), key=f"{market}_run_simulation"):
            with st.spinner(lang.get('running_simulation', 'Выполняется симуляция...')):
                results_df, drawdowns, recovery_factors, optimal_results, equity_curves = monte_carlo_simulation(
                    trades_df, market, iterations=5000, period=period_map[period],
                    trend_tag=trend_tag, direction=direction, trade_type=trade_type, lang=lang
                )
                # Сохраняем результаты в session_state
                st.session_state[f"{market}_monte_carlo_results"] = {
                    "results_df": results_df,
                    "drawdowns": drawdowns,
                    "recovery_factors": recovery_factors,
                    "optimal_results": optimal_results,
                    "equity_curves": equity_curves
                }
                logger.info(f"Симуляция Монте-Карло для {market} завершена и сохранена в session_state")

        # Отображение результатов, если они есть
        if st.session_state[f"{market}_monte_carlo_results"]:
            results = st.session_state[f"{market}_monte_carlo_results"]
            results_df = results["results_df"]
            drawdowns = results["drawdowns"]
            optimal_results = results["optimal_results"]
            equity_curves = results["equity_curves"]

            if results_df is None:
                st.error(lang.get('no_data_after_filter', 'Нет данных после применения фильтров'))
                return

            # Отображение результатов
            st.subheader(lang.get('optimal_strategies', 'Оптимальные стратегии'))
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label=lang.get('max_profit_strategy', 'Макс. прибыль'),
                    value=f"{optimal_results['max_profit'][0]} ({optimal_results['max_profit'][1]})"
                )
            with col2:
                st.metric(
                    label=lang.get('min_drawdown_strategy', 'Мин. просадка'),
                    value=f"{optimal_results['min_drawdown'][0]} ({optimal_results['min_drawdown'][1]})"
                )
            with col3:
                st.metric(
                    label=lang.get('balanced_strategy', 'Баланс'),
                    value=f"{optimal_results['balanced'][0]} ({optimal_results['balanced'][1]})"
                )

            # Таблица результатов
            st.subheader(lang.get('results_table', 'Таблица результатов'))
            summary_df = results_df.groupby(['trade_setup', 'timeframe']).agg({
                'final_profit': 'mean',
                'max_drawdown': 'mean',
                'recovery_factor': 'mean'
            }).reset_index()
            summary_df.columns = [
                lang.get('trade_setup', 'Сетап'),
                lang.get('timeframe', 'Таймфрейм'),
                lang.get('avg_profit', 'Средняя прибыль, %'),
                lang.get('avg_drawdown', 'Средняя просадка, %'),
                lang.get('avg_recovery_factor', 'Коэффициент восстановления')
            ]
            st.dataframe(summary_df, use_container_width=True)

            # Графики
            st.subheader(lang.get('visualizations', 'Визуализация'))
            fig_equity = plot_monte_carlo_equity(equity_curves, market, lang)
            if fig_equity:
                st.plotly_chart(fig_equity, use_container_width=True, key=f"{market}_monte_carlo_equity")

            fig_drawdown = plot_monte_carlo_drawdown_histogram(drawdowns, market, lang)
            if fig_drawdown:
                st.plotly_chart(fig_drawdown, use_container_width=True, key=f"{market}_monte_carlo_drawdown")

            fig_heatmap = plot_monte_carlo_heatmap(results_df, market, lang)
            if fig_heatmap:
                st.plotly_chart(fig_heatmap, use_container_width=True, key=f"{market}_monte_carlo_heatmap")

            # Экспорт в PDF (перемещён внутрь условия)
            if st.button(lang.get('export_pdf', 'Экспортировать в PDF'), key=f"{market}_export_pdf"):
                with st.spinner(lang.get('generating_pdf', 'Генерация PDF...')):
                    try:
                        pdf_file, pdf_bytes = export_monte_carlo_to_pdf(
                            market, lang, summary_df, fig_equity, fig_drawdown, fig_heatmap, optimal_results
                        )
                        st.download_button(
                            label=lang.get('download_pdf', 'Скачать PDF'),
                            data=pdf_bytes,
                            file_name=os.path.basename(pdf_file),
                            mime="application/pdf",
                            key=f"{market}_download_pdf"
                        )
                        st.success(f"{lang.get('pdf_generated', 'PDF успешно создан и готов к скачиванию!')} Сохранён в: {pdf_file}")
                        logger.info(f"PDF для {market} готов для скачивания: {pdf_file}")
                    except Exception as e:
                        st.error(lang.get('pdf_error', 'Ошибка при создании PDF') + f": {str(e)}")
                        logger.error(f"Ошибка при экспорте PDF для {market}: {str(e)}")

    except Exception as e:
        logger.error(f"Ошибка отображения симуляции Монте-Карло для {market}: {str(e)}")
        st.error(lang.get('error_displaying_simulation', 'Ошибка отображения симуляции') + f": {str(e)}")