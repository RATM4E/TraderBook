import streamlit as st
import pandas as pd
import os
from src.core.data_manager import load_trades
from src.core.logging_setup import logger
from src.ui.translations import load_translations

def list_tab():
    """Вкладка для отображения списка сделок."""
    # Добавляем стили для растяжки интерфейса
    st.markdown("""
        <style>
        div[data-testid="stAppViewContainer"] > div {
            max-width: 100% !important;
        }
        div[data-testid="stAppViewContainer"] .block-container {
            max-width: 100% !important;
            padding: 1rem !important;
        }
        div[data-testid="stAppViewContainer"] .stTextInput,
        div[data-testid="stAppViewContainer"] .stNumberInput,
        div[data-testid="stAppViewContainer"] .stSelectbox,
        div[data-testid="stAppViewContainer"] .stTextArea,
        div[data-testid="stAppViewContainer"] .stForm,
        div[data-testid="stAppViewContainer"] .stDataFrame {
            max-width: 100% !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    try:
        lang = load_translations()[st.session_state.language]
        trades_df = load_trades()

        if trades_df.empty:
            st.write(lang.get('no_trades', "Нет сделок для отображения"))
            return

        # Проверка наличия новых колонок скриншотов
        screenshot_cols = ['entry_screenshot_1', 'entry_screenshot_2', 'entry_screenshot_3',
                          'exit_screenshot_1', 'exit_screenshot_2', 'exit_screenshot_3']
        for col in screenshot_cols:
            if col not in trades_df.columns:
                trades_df[col] = ''

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            market_filter = st.selectbox(
                lang.get('filter_market', "Фильтр по рынку"),
                [''] + sorted(trades_df['market'].unique().tolist()),
                key='market_filter'
            )
        with col2:
            pair_filter = st.selectbox(
                lang.get('filter_pair', "Фильтр по паре"),
                [''] + sorted(trades_df['pair'].dropna().unique().tolist()),
                key='pair_filter'
            )
        with col3:
            type_filter = st.selectbox(
                lang.get('filter_type', "Фильтр по типу"),
                [''] + sorted(trades_df['type'].dropna().unique().tolist()),
                key='type_filter'
            )
        with col4:
            result_filter = st.selectbox(
                lang.get('filter_result', "Фильтр по результату"),
                [''] + sorted(trades_df['result'].dropna().unique().tolist()),
                key='result_filter'
            )
        with col5:
            status_filter = st.selectbox(
                lang.get('filter_status', "Фильтр по статусу"),
                [''] + sorted(trades_df['status'].dropna().unique().tolist()),
                key='status_filter'
            )
        with col6:
            screenshot_filter = st.checkbox(
                "Показать только сделки со скриншотами",
                key='screenshot_filter'
            )

        filtered_df = trades_df.copy()
        if market_filter:
            filtered_df = filtered_df[filtered_df['market'] == market_filter]
        if pair_filter:
            filtered_df = filtered_df[filtered_df['pair'] == pair_filter]
        if type_filter:
            filtered_df = filtered_df[filtered_df['type'] == type_filter]
        if result_filter:
            filtered_df = filtered_df[filtered_df['result'] == result_filter]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if screenshot_filter:
            filtered_df = filtered_df[filtered_df[screenshot_cols].apply(lambda x: x.str.strip().ne('').any(), axis=1)]

        if filtered_df.empty:
            st.write("Нет сделок, соответствующих фильтру.")
            return

        if 'selected' not in filtered_df.columns:
            filtered_df.insert(0, 'selected', False)

        selected_data = st.data_editor(
            filtered_df,
            column_config={
                "selected": st.column_config.CheckboxColumn(
                    "Выбрать",
                    help="Выберите сделку для просмотра деталей",
                    default=False
                ),
                "entry_date": st.column_config.DateColumn("Дата входа"),
                "release_date": st.column_config.DateColumn("Дата выхода"),
                "entry_screenshot_1": st.column_config.ImageColumn(
                    "Скриншот входа 1",
                    help="Первый скриншот точки входа"
                ),
                "entry_screenshot_2": st.column_config.ImageColumn(
                    "Скриншот входа 2",
                    help="Второй скриншот точки входа"
                ),
                "entry_screenshot_3": st.column_config.ImageColumn(
                    "Скриншот входа 3",
                    help="Третий скриншот точки входа"
                ),
                "exit_screenshot_1": st.column_config.ImageColumn(
                    "Скриншот выхода 1",
                    help="Первый скриншот точки выхода"
                ),
                "exit_screenshot_2": st.column_config.ImageColumn(
                    "Скриншот выхода 2",
                    help="Второй скриншот точки выхода"
                ),
                "exit_screenshot_3": st.column_config.ImageColumn(
                    "Скриншот выхода 3",
                    help="Третий скриншот точки выхода"
                ),
            },
            use_container_width=True,
            hide_index=True
        )

        selected_rows = selected_data[selected_data['selected'] == True]
        if len(selected_rows) > 1:
            st.warning("Пожалуйста, выберите только одну сделку для просмотра деталей.")
        elif len(selected_rows) == 1:
            trade = selected_rows.iloc[0]
            selected_trade = trade['trade_deal']
            st.write(f"**Сделка {selected_trade}**")

            col_screenshot1, col_screenshot2 = st.columns(2)
            with col_screenshot1:
                for i in range(1, 4):
                    screenshot = trade.get(f'entry_screenshot_{i}', '')
                    description = trade.get(f'entry_description_{i}', '')
                    if screenshot and pd.notna(screenshot) and screenshot.strip():
                        if os.path.exists(screenshot):
                            st.image(screenshot, caption=f"Скриншот точки входа {i}", use_container_width=True)
                        else:
                            st.warning(f"Скриншот точки входа {i} для сделки {selected_trade} не найден: {screenshot}")
                    if description and pd.notna(description) and description.strip():
                        st.write(f"Описание точки входа {i}: {description}")

            with col_screenshot2:
                for i in range(1, 4):
                    screenshot = trade.get(f'exit_screenshot_{i}', '')
                    description = trade.get(f'exit_description_{i}', '')
                    if screenshot and pd.notna(screenshot) and screenshot.strip():
                        if os.path.exists(screenshot):
                            st.image(screenshot, caption=f"Скриншот точки выхода {i}", use_container_width=True)
                        else:
                            st.warning(f"Скриншот точки выхода {i} для сделки {selected_trade} не найден: {screenshot}")
                    if description and pd.notna(description) and description.strip():
                        st.write(f"Описание точки выхода {i}: {description}")

    except Exception as e:
        logger.error(f"Ошибка во вкладке списка сделок: {str(e)}")
        st.error(f"Произошла ошибка: {str(e)}")