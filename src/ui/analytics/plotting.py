import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.core.logging_setup import logger

def _apply_plotly_style(fig, x_title, y_title, lang, title=None):
    """Применение общего стиля к графикам."""
    fig.update_layout(
        title=lang.get(title, title) if title else None,
        xaxis_title=lang.get(x_title, x_title),
        yaxis_title=lang.get(y_title, y_title),
        plot_bgcolor='#F5F6F5',
        paper_bgcolor='#F5F6F5',
        font=dict(family='Arial', size=12, color='#333333'),
        xaxis=dict(gridcolor='#D3D3D3'),
        yaxis=dict(gridcolor='#D3D3D3')
    )
    return fig

@st.cache_data
def plot_monte_carlo_equity(equity_curves, market, lang):
    """График кривых эквити для симуляции Монте-Карло."""
    try:
        if not equity_curves:
            logger.info(f"Нет данных для графика кривых эквити для {market}")
            return None
        fig = go.Figure()
        for i, curve in enumerate(equity_curves):
            fig.add_trace(go.Scatter(
                x=list(range(len(curve))),
                y=curve,
                mode='lines',
                name=f'Кривая {i+1}',
                line=dict(color=f'rgba(70, 130, 180, {0.5/len(equity_curves)})')
            ))
        fig = _apply_plotly_style(fig, 'trade_number', 'profit_percent', lang, 'monte_carlo_equity')
        logger.info(f"Построен график кривых эквити для {market}: {len(equity_curves)} кривых")
        return fig
    except Exception as e:
        logger.error(f"Ошибка построения графика кривых эквити для {market}: {str(e)}")
        return None

@st.cache_data
def plot_monte_carlo_drawdown_histogram(drawdowns, market, lang):
    """Гистограмма максимальных просадок."""
    try:
        if not drawdowns:
            logger.info(f"Нет данных для гистограммы просадок для {market}")
            return None
        fig = px.histogram(
            x=drawdowns,
            nbins=50,
            title=lang.get('monte_carlo_drawdown_histogram', 'Гистограмма максимальных просадок'),
            color_discrete_sequence=['#4682B4'],
            opacity=0.7
        )
        fig = _apply_plotly_style(fig, 'max_drawdown', 'count', lang)
        logger.info(f"Построена гистограмма просадок для {market}: {len(drawdowns)} записей")
        return fig
    except Exception as e:
        logger.error(f"Ошибка построения гистограммы просадок для {market}: {str(e)}")
        return None

@st.cache_data
def plot_monte_carlo_heatmap(results_df, market, lang):
    """Тепловая карта прибыли по сетапам и таймфреймам."""
    try:
        if results_df.empty:
            logger.info(f"Нет данных для тепловой карты Монте-Карло для {market}")
            return None
        grouped = results_df.groupby(['trade_setup', 'timeframe'])['final_profit'].mean().unstack(fill_value=0)
        if grouped.empty:
            logger.info(f"Нет данных после группировки для тепловой карты Монте-Карло для {market}")
            return None
        fig = px.imshow(
            grouped,
            title=lang.get('monte_carlo_heatmap', 'Тепловая карта прибыли'),
            color_continuous_scale='RdYlGn',
            labels=dict(x=lang.get('timeframe', 'Таймфрейм'), y=lang.get('trade_setup', 'Сетап'), color=lang.get('profit_percent', 'Прибыль, %'))
        )
        fig = _apply_plotly_style(fig, 'timeframe', 'trade_setup', lang)
        logger.info(f"Построена тепловая карта Монте-Карло для {market}: {len(grouped)} сетапов")
        return fig
    except Exception as e:
        logger.error(f"Ошибка построения тепловой карты Монте-Карло для {market}: {str(e)}")
        return None

@st.cache_data
def plot_time_histogram(data_df, market, lang):
    """Гистограмма времени открытия и закрытия сделок."""
    try:
        if data_df.empty:
            logger.info(f"Нет данных для гистограммы времени для {market}")
            return None
        fig = px.histogram(
            data_df,
            x='Hour',
            color='Type',
            barmode='overlay',
            nbins=24,
            title=lang.get('time_histogram', 'Гистограмма времени открытия/закрытия'),
            color_discrete_map={
                lang.get('entry_date', 'Открытие'): '#4682B4',
                lang.get('release_date', 'Закрытие'): '#8B008B'
            },
            opacity=0.7
        )
        fig = _apply_plotly_style(fig, 'hour', 'count', lang)
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1), legend_title=None)
        logger.info(f"Гистограмма времени для {market}: {len(data_df)} записей")
        return fig
    except Exception as e:
        logger.error(f"Ошибка построения гистограммы времени для {market}: {str(e)}")
        return None

@st.cache_data
def plot_rr_histogram(trades_df, market, lang):
    """Гистограмма по AVG RR."""
    try:
        filtered_df = trades_df[trades_df['status'] == 'Закрытая']
        if filtered_df.empty or filtered_df['avg_rr'].isna().all():
            logger.info(f"Нет закрытых сделок для гистограммы AVG RR для {market}")
            return None
        bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, float('inf')]
        fig = px.histogram(
            filtered_df,
            x='avg_rr',
            nbins=len(bins)-1,
            range_x=[0, 10],
            title=lang.get('rr_histogram', 'Гистограмма по AVG RR'),
            color_discrete_sequence=['#4682B4'],
            opacity=0.7
        )
        fig.update_traces(xbins=dict(start=0, end=10, size=1))
        fig = _apply_plotly_style(fig, 'avg_rr', 'count', lang)
        fig.update_layout(showlegend=False)
        logger.info(f"Гистограмма AVG RR для {market}: {len(filtered_df)} закрытых сделок")
        return fig
    except Exception as e:
        logger.error(f"Ошибка построения гистограммы AVG RR для {market}: {str(e)}")
        return None

@st.cache_data
def plot_setup_tf_heatmap(trades_df, market, lang, limit_top_10):
    """Тепловая карта сетапов и таймфреймов."""
    try:
        if trades_df.empty:
            logger.info(f"Нет данных для тепловой карты сетапов для {market}")
            return None
        grouped = trades_df.groupby(['trade_setup', 'timeframe'])['profit_percent'].sum().unstack(fill_value=0)
        if limit_top_10:
            top_setups = trades_df['trade_setup'].value_counts().head(10).index
            grouped = grouped.loc[grouped.index.isin(top_setups)]
        if grouped.empty:
            logger.info(f"Нет данных после фильтрации для тепловой карты сетапов для {market}")
            return None
        fig = px.imshow(
            grouped,
            title=lang.get('setup_tf_heatmap', 'Тепловая карта сетапов и таймфреймов'),
            color_continuous_scale='RdYlGn',
            labels=dict(x=lang.get('timeframe', 'Таймфрейм'), y=lang.get('trade_setup', 'Сетап'), color=lang.get('profit_percent', 'Прибыль, %'))
        )
        fig = _apply_plotly_style(fig, 'timeframe', 'trade_setup', lang)
        logger.info(f"Тепловая карта сетапов для {market}: {len(grouped)} сетапов, {len(grouped.columns)} таймфреймов")
        return fig
    except Exception as e:
        logger.error(f"Ошибка построения тепловой карты для {market}: {str(e)}")
        return None

@st.cache_data
def plot_trend_tag_bar(trades_df, market, lang):
    """График по тегам тренда."""
    try:
        if trades_df.empty:
            logger.info(f"Нет данных для графика тегов тренда для {market}")
            return None
        trend_tags = trades_df['trend_tag'].fillna(lang.get('no_tag', 'Без тега'))
        grouped = trend_tags.groupby(trend_tags).agg({'profit_percent': 'sum'}).reset_index()
        grouped['trend_tag'] = grouped['trend_tag'].replace('', lang.get('no_tag', 'Без тега'))
        fig = px.bar(
            grouped,
            x='trend_tag',
            y='profit_percent',
            title=lang.get('trend_tag_bar', 'Прибыль по тегам тренда'),
            color_discrete_sequence=['#4682B4']
        )
        fig = _apply_plotly_style(fig, 'trend_tag', 'profit_percent', lang)
        logger.info(f"График тегов тренда для {market}: {len(grouped)} категорий")
        return fig
    except Exception as e:
        logger.error(f"Ошибка построения графика тегов тренда для {market}: {str(e)}")
        return None

@st.cache_data
def plot_direction_bar(trades_df, market, lang):
    """График по направлению (Long/Short)."""
    try:
        if trades_df.empty:
            logger.info(f"Нет данных для графика направления для {market}")
            return None, None
        count_df = trades_df.groupby('type').size().reset_index(name='count')
        profit_df = trades_df.groupby('type').agg({'profit_percent': 'sum'}).reset_index()
        fig_count = px.bar(
            count_df,
            x='type',
            y='count',
            title=lang.get('direction_bar', 'Количество по направлениям (Long/Short)'),
            color_discrete_sequence=['#4682B4']
        )
        fig_profit = px.bar(
            profit_df,
            x='type',
            y='profit_percent',
            title=lang.get('direction_bar_profit', 'Прибыль по направлениям (Long/Short)'),
            color_discrete_sequence=['#4682B4']
        )
        for fig in [fig_count, fig_profit]:
            fig = _apply_plotly_style(fig, 'type', 'count' if fig is fig_count else 'profit_percent', lang)
        logger.info(f"График направления для {market}: {len(count_df)} типов")
        return fig_count, fig_profit
    except Exception as e:
        logger.error(f"Ошибка построения графика направления для {market}: {str(e)}")
        return None, None

@st.cache_data
def plot_session_histogram(trades_df, market, lang):
    """Гистограмма по сессиям."""
    try:
        if trades_df.empty:
            logger.info(f"Нет данных для гистограммы сессий для {market}")
            return None, None
        count_df = trades_df.groupby('session').size().reset_index(name='count')
        profit_df = trades_df.groupby('session').agg({'profit_percent': 'sum'}).reset_index()
        fig_count = px.histogram(
            count_df,
            x='session',
            y='count',
            title=lang.get('session_histogram_count', 'Количество по сессиям'),
            color_discrete_sequence=['#4682B4']
        )
        fig_profit = px.histogram(
            profit_df,
            x='session',
            y='profit_percent',
            title=lang.get('session_histogram_profit', 'Прибыль по сессиям'),
            color_discrete_sequence=['#4682B4']
        )
        for fig in [fig_count, fig_profit]:
            fig = _apply_plotly_style(fig, 'session', 'count' if fig is fig_count else 'profit_percent', lang)
        logger.info(f"Гистограмма сессий для {market}: {len(count_df)} сессий")
        return fig_count, fig_profit
    except Exception as e:
        logger.error(f"Ошибка построения гистограммы сессий для {market}: {str(e)}")
        return None, None

@st.cache_data
def plot_trade_type_histogram(trades_df, market, lang):
    """Гистограмма по типам сделок."""
    try:
        if trades_df.empty:
            logger.info(f"Нет данных для гистограммы типов сделок для {market}")
            return None, None
        count_df = trades_df.groupby('trade_type').size().reset_index(name='count')
        profit_df = trades_df.groupby('trade_type').agg({'profit_percent': 'sum'}).reset_index()
        fig_count = px.histogram(
            count_df,
            x='trade_type',
            y='count',
            title=lang.get('trade_type_histogram_count', 'Количество по типам сделок'),
            color_discrete_sequence=['#4682B4']
        )
        fig_profit = px.histogram(
            profit_df,
            x='trade_type',
            y='profit_percent',
            title=lang.get('trade_type_histogram_profit', 'Прибыль по типам сделок'),
            color_discrete_sequence=['#4682B4']
        )
        for fig in [fig_count, fig_profit]:
            fig = _apply_plotly_style(fig, 'trade_type', 'count' if fig is fig_count else 'profit_percent', lang)
        logger.info(f"Гистограмма типов сделок для {market}: {len(count_df)} типов")
        return fig_count, fig_profit
    except Exception as e:
        logger.error(f"Ошибка построения гистограммы типов сделок для {market}: {str(e)}")
        return None, None

@st.cache_data
def plot_day_of_week_histogram(data_df, market, lang):
    """Гистограмма по дням недели."""
    try:
        if data_df.empty:
            logger.info(f"Нет данных для гистограммы дней недели для {market}")
            return None, None
        fig = px.histogram(
            data_df,
            x='Day',
            color='Type',
            barmode='group',
            title=lang.get('day_of_week_histogram', 'Гистограмма по дням недели'),
            category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']},
            color_discrete_map={
                lang.get('entry_date', 'Открытие'): '#4682B4',
                lang.get('release_date', 'Закрытие'): '#8B008B'
            }
        )
        fig = _apply_plotly_style(fig, 'day', 'count', lang)
        logger.info(f"Гистограмма дней недели для {market}: {len(data_df)} записей")
        return fig, None
    except Exception as e:
        logger.error(f"Ошибка построения гистограммы дней недели для {market}: {str(e)}")
        return None, None

@st.cache_data
def plot_calendar_heatmap(trades_df, market, lang, timezone, metric):
    """Календарный вид (heatmap)."""
    try:
        if trades_df.empty:
            logger.info(f"Нет данных для календарного вида для {market}")
            return None
        trades_df['date'] = trades_df['entry_date'].dt.tz_convert(pytz.FixedOffset(timezone * 60)).dt.date
        if metric == lang.get('calendar_metric_count', 'Количество сделок'):
            grouped = trades_df.groupby('date').size().reset_index(name='value')
        else:  # Предполагаем, что это 'Прибыльность'
            grouped = trades_df.groupby('date').agg({'profit_percent': 'sum'}).reset_index(name='value')
        grouped['date'] = pd.to_datetime(grouped['date'])
        grouped['year'] = grouped['date'].dt.year
        grouped['week'] = grouped['date'].dt.isocalendar().week
        grouped['day'] = grouped['date'].dt.day_name()
        pivot = grouped.pivot_table(values='value', index='week', columns='day', fill_value=0)
        pivot = pivot.reindex(columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        if pivot.empty:
            logger.info(f"Нет данных для календарного вида после обработки для {market}")
            return None
        fig = px.imshow(
            pivot,
            title=lang.get('calendar_heatmap', 'Календарный вид'),
            color_continuous_scale='RdYlGn',
            labels=dict(x=lang.get('day', 'День недели'), y=lang.get('week', 'Неделя'), color=metric)
        )
        fig = _apply_plotly_style(fig, 'day', 'week', lang)
        logger.info(f"Календарный вид для {market}: {len(grouped)} дней")
        return fig
    except Exception as e:
        logger.error(f"Ошибка построения календарного вида для {market}: {str(e)}")
        return None