import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz
from src.core.config import TRADES_FILE, TRADES_COLUMNS, SCREENSHOTS_ENTRY_DIR, SCREENSHOTS_EXIT_DIR, DATE_FORMAT
from src.core.data_manager import load_trades, save_trades, load_setups
from src.core.logging_setup import logger
from src.ui.utils import save_screenshots, validate_dates, validate_percentages
from src.ui.translations import load_translations
from src.core.calculations import calculate_fields

def trade_input_tab(market):
    """Вкладка для ввода и редактирования сделок."""
    try:
        lang = load_translations()[st.session_state.language]
        st.header(lang.get('trade_input', 'Ввод сделки'))

        # Инициализация флага видимости формы редактирования
        market_lower = market.lower()
        edit_form_visible_key = f'{market_lower}_edit_form_visible'
        edit_trade_deal_key = f'{market_lower}_edit_trade_deal'
        if edit_form_visible_key not in st.session_state:
            st.session_state[edit_form_visible_key] = False
        if edit_trade_deal_key not in st.session_state:
            st.session_state[edit_trade_deal_key] = ''

        # Секция добавления новой сделки
        st.subheader(lang.get('add_trade', 'Добавить сделку'))
        with st.form(f"{market_lower}_trade_form", clear_on_submit=True):
            pair = st.text_input(lang.get('pair', 'Торговая пара'), key=f'{market_lower}_pair')
            entry_date = st.date_input(lang.get('entry_date', 'Дата входа'), key=f'{market_lower}_entry_date')
            entry_time = st.time_input(lang.get('entry_time', 'Время входа'), key=f'{market_lower}_entry_time')
            release_date = st.date_input(lang.get('release_date', 'Дата выхода'), value=None, key=f'{market_lower}_release_date')
            release_time = st.time_input(lang.get('release_time', 'Время выхода'), value=None, key=f'{market_lower}_release_time')
            risk_percent = st.number_input(lang.get('risk_percent', 'Процент риска'), min_value=0.0, max_value=100.0, step=0.1, key=f'{market_lower}_risk_percent')
            tick_size = st.number_input(lang.get('tick_size', 'Размер тика'), min_value=0.0, step=0.0001, key=f'{market_lower}_tick_size')
            entry_point = st.number_input(lang.get('entry_point', 'Точка входа'), min_value=0.0, step=0.0001, key=f'{market_lower}_entry_point')
            stop_loss = st.number_input(lang.get('stop_loss', 'Стоп-лосс'), min_value=0.0, step=0.0001, key=f'{market_lower}_stop_loss')
            take_profit_one = st.number_input(lang.get('take_profit_one', 'Тейк-профит 1'), min_value=0.0, step=0.0001, key=f'{market_lower}_take_profit_one')
            take_profit_two = st.number_input(lang.get('take_profit_two', 'Тейк-профит 2'), min_value=0.0, step=0.0001, key=f'{market_lower}_take_profit_two')
            take_profit_three = st.number_input(lang.get('take_profit_three', 'Тейк-профит 3'), min_value=0.0, step=0.0001, key=f'{market_lower}_take_profit_three')
            take_profit_one_percent = st.number_input(lang.get('take_profit_one_percent', 'Процент TP1'), min_value=0.0, max_value=100.0, step=0.1, key=f'{market_lower}_take_profit_one_percent')
            take_profit_two_percent = st.number_input(lang.get('take_profit_two_percent', 'Процент TP2'), min_value=0.0, max_value=100.0, step=0.1, key=f'{market_lower}_take_profit_two_percent')
            take_profit_three_percent = st.number_input(lang.get('take_profit_three_percent', 'Процент TP3'), min_value=0.0, max_value=100.0, step=0.1, key=f'{market_lower}_take_profit_three_percent')
            
            setups_df = load_setups()
            setups_df['display_setup'] = setups_df['group_name'] + ': ' + setups_df['setup_name']
            trade_setup = st.selectbox(lang.get('trade_setup', 'Сетап'), [''] + setups_df['display_setup'].dropna().tolist(), key=f'{market_lower}_trade_setup')
            trade_setup_group = setups_df[setups_df['display_setup'] == trade_setup]['group_name'].iloc[0] if trade_setup else ''
            
            timeframe = st.selectbox(lang.get('timeframe', 'Таймфрейм'), ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'], key=f'{market_lower}_timeframe')
            entry_screenshots = [st.file_uploader(lang.get('entry_screenshot', 'Скриншот входа') + f" {i+1}", ['png', 'jpg', 'jpeg'], key=f'{market_lower}_entry_screenshot_{i}') for i in range(3)]
            exit_screenshots = [st.file_uploader(lang.get('exit_screenshot', 'Скриншот выхода') + f" {i+1}", ['png', 'jpg', 'jpeg'], key=f'{market_lower}_exit_screenshot_{i}') for i in range(3)]
            entry_descriptions = [st.text_area(lang.get('entry_description', 'Описание входа') + f" {i+1}", key=f'{market_lower}_entry_description_{i}') for i in range(3)]
            exit_descriptions = [st.text_area(lang.get('exit_description', 'Описание выхода') + f" {i+1}", key=f'{market_lower}_exit_description_{i}') for i in range(3)]
            trend_tag = st.text_input(lang.get('trend_tag', 'Тег тренда'), key=f'{market_lower}_trend_tag')

            submitted = st.form_submit_button(lang.get('submit', 'Добавить'))
            if submitted:
                entry_datetime = pd.Timestamp(datetime.combine(entry_date, entry_time), tz=pytz.UTC) if entry_date and entry_time else None
                release_datetime = pd.Timestamp(datetime.combine(release_date, release_time), tz=pytz.UTC) if release_date and release_time else None
                if not validate_dates(entry_datetime, release_datetime, lang):
                    return
                if not validate_percentages(take_profit_one_percent, take_profit_two_percent, take_profit_three_percent, lang):
                    return
                
                trades_df = load_trades()
                trade_deal = f"{pair}_{entry_datetime.strftime('%Y%m%d_%H%M%S')}"
                entry_screenshot_paths, exit_screenshot_paths = save_screenshots(entry_screenshots, exit_screenshots, trade_deal)
                
                # Вычисление полей
                trade_type, session, avg_rr, profit_percent, result, direction = calculate_fields(
                    entry_point, stop_loss, take_profit_one, take_profit_two, take_profit_three,
                    take_profit_one_percent, take_profit_two_percent, take_profit_three_percent,
                    entry_datetime, release_datetime, st.session_state.timezone,
                    risk_percent, tick_size, st.session_state.reward_risk
                )
                
                new_trade = pd.DataFrame([{
                    'trade_deal': trade_deal, 'market': market, 'pair': pair,
                    'entry_date': entry_datetime.strftime(DATE_FORMAT) if entry_datetime else '',
                    'release_date': release_datetime.strftime(DATE_FORMAT) if release_datetime else '',
                    'risk_percent': risk_percent, 'tick_size': tick_size, 'entry_point': entry_point,
                    'stop_loss': stop_loss, 'take_profit_one': take_profit_one,
                    'take_profit_two': take_profit_two, 'take_profit_three': take_profit_three,
                    'take_profit_one_percent': take_profit_one_percent,
                    'take_profit_two_percent': take_profit_two_percent,
                    'take_profit_three_percent': take_profit_three_percent,
                    'trade_setup': trade_setup.split(': ')[1] if trade_setup else '',
                    'trade_setup_group': trade_setup_group,
                    'timeframe': timeframe, 'type': direction, 'session': session,
                    'avg_rr': avg_rr, 'profit_percent': profit_percent, 'result': result,
                    'status': 'Pending', 'notion_text': '', 'screenshot': '',
                    'entry_screenshot_1': entry_screenshot_paths[0], 'entry_screenshot_2': entry_screenshot_paths[1],
                    'entry_screenshot_3': entry_screenshot_paths[2],
                    'entry_description_1': entry_descriptions[0], 'entry_description_2': entry_descriptions[1],
                    'entry_description_3': entry_descriptions[2],
                    'exit_screenshot_1': exit_screenshot_paths[0], 'exit_screenshot_2': exit_screenshot_paths[1],
                    'exit_screenshot_3': exit_screenshot_paths[2],
                    'exit_description_1': exit_descriptions[0], 'exit_description_2': exit_descriptions[1],
                    'exit_description_3': exit_descriptions[2],
                    'trend_tag': trend_tag
                }], columns=TRADES_COLUMNS)
                save_trades(trades_df)
                st.success(f"{lang.get('trade_added', 'Сделка добавлена')}: {trade_deal}")
                st.rerun()

        # Секция редактирования сделки
        st.subheader(lang.get('edit_trade', 'Редактировать сделку'))
        trades_df = load_trades()
        # Фильтруем сделки по текущему рынку
        trade_options = [''] + trades_df[trades_df['market'] == market]['trade_deal'].dropna().tolist()
        selected_trade = st.selectbox(lang.get('select_trade', 'Выберите сделку'), trade_options, key=f'{market_lower}_edit_trade_select')
        
        if selected_trade:
            st.session_state[edit_form_visible_key] = True
            st.session_state[edit_trade_deal_key] = selected_trade

        if st.session_state[edit_form_visible_key] and st.session_state[edit_trade_deal_key]:
            trade_data = trades_df[trades_df['trade_deal'] == st.session_state[edit_trade_deal_key]].iloc[0]
            with st.form(f"{market_lower}_edit_trade_form", clear_on_submit=False):
                # Поле market отображается как текст
                st.write(f"{lang.get('market', 'Рынок')}: {market}")
                pair = st.text_input(lang.get('pair', 'Торговая пара'), value=trade_data['pair'], key=f'{market_lower}_edit_pair')
                entry_date = pd.Timestamp(trade_data['entry_date']).date() if trade_data['entry_date'] else None
                entry_time = pd.Timestamp(trade_data['entry_date']).time() if trade_data['entry_date'] else None
                entry_date = st.date_input(lang.get('entry_date', 'Дата входа'), value=entry_date, key=f'{market_lower}_edit_entry_date')
                entry_time = st.time_input(lang.get('entry_time', 'Время входа'), value=entry_time, key=f'{market_lower}_edit_entry_time')
                release_date = pd.Timestamp(trade_data['release_date']).date() if trade_data['release_date'] else None
                release_time = pd.Timestamp(trade_data['release_date']).time() if trade_data['release_date'] else None
                release_date = st.date_input(lang.get('release_date', 'Дата выхода'), value=release_date, key=f'{market_lower}_edit_release_date')
                release_time = st.time_input(lang.get('release_time', 'Время выхода'), value=release_time, key=f'{market_lower}_edit_release_time')
                risk_percent = st.number_input(lang.get('risk_percent', 'Процент риска'), min_value=0.0, max_value=100.0, step=0.1, value=float(trade_data['risk_percent']), key=f'{market_lower}_edit_risk_percent')
                tick_size = st.number_input(lang.get('tick_size', 'Размер тика'), min_value=0.0, step=0.0001, value=float(trade_data['tick_size']), key=f'{market_lower}_edit_tick_size')
                entry_point = st.number_input(lang.get('entry_point', 'Точка входа'), min_value=0.0, step=0.0001, value=float(trade_data['entry_point']), key=f'{market_lower}_edit_entry_point')
                stop_loss = st.number_input(lang.get('stop_loss', 'Стоп-лосс'), min_value=0.0, step=0.0001, value=float(trade_data['stop_loss']), key=f'{market_lower}_edit_stop_loss')
                take_profit_one = st.number_input(lang.get('take_profit_one', 'Тейк-профит 1'), min_value=0.0, step=0.0001, value=float(trade_data['take_profit_one']), key=f'{market_lower}_edit_take_profit_one')
                take_profit_two = st.number_input(lang.get('take_profit_two', 'Тейк-профит 2'), min_value=0.0, step=0.0001, value=float(trade_data['take_profit_two']), key=f'{market_lower}_edit_take_profit_two')
                take_profit_three = st.number_input(lang.get('take_profit_three', 'Тейк-профит 3'), min_value=0.0, step=0.0001, value=float(trade_data['take_profit_three']), key=f'{market_lower}_edit_take_profit_three')
                take_profit_one_percent = st.number_input(lang.get('take_profit_one_percent', 'Процент TP1'), min_value=0.0, max_value=100.0, step=0.1, value=float(trade_data['take_profit_one_percent']), key=f'{market_lower}_edit_take_profit_one_percent')
                take_profit_two_percent = st.number_input(lang.get('take_profit_two_percent', 'Процент TP2'), min_value=0.0, max_value=100.0, step=0.1, value=float(trade_data['take_profit_two_percent']), key=f'{market_lower}_edit_take_profit_two_percent')
                take_profit_three_percent = st.number_input(lang.get('take_profit_three_percent', 'Процент TP3'), min_value=0.0, max_value=100.0, step=0.1, value=float(trade_data['take_profit_three_percent']), key=f'{market_lower}_edit_take_profit_three_percent')
                
                setups_df = load_setups()
                setups_df['display_setup'] = setups_df['group_name'] + ': ' + setups_df['setup_name']
                current_setup = f"{trade_data['trade_setup_group']}: {trade_data['trade_setup']}" if trade_data['trade_setup'] else ''
                trade_setup = st.selectbox(lang.get('trade_setup', 'Сетап'), [''] + setups_df['display_setup'].dropna().tolist(), index=setups_df['display_setup'].tolist().index(current_setup) if current_setup in setups_df['display_setup'].tolist() else 0, key=f'{market_lower}_edit_trade_setup')
                trade_setup_group = setups_df[setups_df['display_setup'] == trade_setup]['group_name'].iloc[0] if trade_setup else ''
                
                # Обработка некорректного timeframe
                valid_timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
                current_timeframe = trade_data['timeframe'] if trade_data['timeframe'] in valid_timeframes else 'M1'
                timeframe = st.selectbox(
                    lang.get('timeframe', 'Таймфрейм'),
                    valid_timeframes,
                    index=valid_timeframes.index(current_timeframe),
                    key=f'{market_lower}_edit_timeframe'
                )
                
                existing_screenshots = {
                    'entry': [trade_data[f'entry_screenshot_{i+1}'] for i in range(3)],
                    'exit': [trade_data[f'exit_screenshot_{i+1}'] for i in range(3)]
                }
                deleted_screenshots = {'entry': [False] * 3, 'exit': [False] * 3}
                
                entry_screenshots = []
                for i in range(3):
                    if existing_screenshots['entry'][i] and os.path.exists(existing_screenshots['entry'][i]):
                        st.image(existing_screenshots['entry'][i], caption=lang.get('current_entry_screenshot', 'Текущий скриншот входа') + f" {i+1}", width=200)
                        deleted_screenshots['entry'][i] = st.checkbox(lang.get('delete_screenshot', 'Удалить скриншот') + f" {i+1}", key=f'{market_lower}_delete_entry_screenshot_{i}')
                    entry_screenshots.append(st.file_uploader(lang.get('entry_screenshot', 'Скриншот входа') + f" {i+1}", ['png', 'jpg', 'jpeg'], key=f'{market_lower}_edit_entry_screenshot_{i}'))
                
                exit_screenshots = []
                for i in range(3):
                    if existing_screenshots['exit'][i] and os.path.exists(existing_screenshots['exit'][i]):
                        st.image(existing_screenshots['exit'][i], caption=lang.get('current_exit_screenshot', 'Текущий скриншот выхода') + f" {i+1}", width=200)
                        deleted_screenshots['exit'][i] = st.checkbox(lang.get('delete_screenshot', 'Удалить скриншот') + f" {i+1}", key=f'{market_lower}_delete_exit_screenshot_{i}')
                    exit_screenshots.append(st.file_uploader(lang.get('exit_screenshot', 'Скриншот выхода') + f" {i+1}", ['png', 'jpg', 'jpeg'], key=f'{market_lower}_edit_exit_screenshot_{i}'))
                
                entry_descriptions = [st.text_area(lang.get('entry_description', 'Описание входа') + f" {i+1}", value=trade_data[f'entry_description_{i+1}'], key=f'{market_lower}_edit_entry_description_{i}') for i in range(3)]
                exit_descriptions = [st.text_area(lang.get('exit_description', 'Описание выхода') + f" {i+1}", value=trade_data[f'exit_description_{i+1}'], key=f'{market_lower}_edit_exit_description_{i}') for i in range(3)]
                trend_tag = st.text_input(lang.get('trend_tag', 'Тег тренда'), value=trade_data['trend_tag'], key=f'{market_lower}_edit_trend_tag')

                col_update, col_delete = st.columns(2)
                with col_update:
                    update_submitted = st.form_submit_button(lang.get('update_trade', 'Обновить'))
                with col_delete:
                    delete_submitted = st.form_submit_button(lang.get('delete_trade', 'Удалить'))

                if update_submitted:
                    entry_datetime = pd.Timestamp(datetime.combine(entry_date, entry_time), tz=pytz.UTC) if entry_date and entry_time else None
                    release_datetime = pd.Timestamp(datetime.combine(release_date, release_time), tz=pytz.UTC) if release_date and release_time else None
                    if not validate_dates(entry_datetime, release_datetime, lang):
                        return
                    if not validate_percentages(take_profit_one_percent, take_profit_two_percent, take_profit_three_percent, lang):
                        return
                    
                    entry_screenshot_paths, exit_screenshot_paths = save_screenshots(
                        entry_screenshots, exit_screenshots, trade_data['trade_deal'],
                        edit_mode=True, existing_screenshots=existing_screenshots, deleted_screenshots=deleted_screenshots
                    )
                    
                    # Вычисление полей
                    trade_type, session, avg_rr, profit_percent, result, direction = calculate_fields(
                        entry_point, stop_loss, take_profit_one, take_profit_two, take_profit_three,
                        take_profit_one_percent, take_profit_two_percent, take_profit_three_percent,
                        entry_datetime, release_datetime, st.session_state.timezone,
                        risk_percent, tick_size, st.session_state.reward_risk
                    )
                    
                    idx = trades_df[trades_df['trade_deal'] == st.session_state[edit_trade_deal_key]].index[0]
                    trades_df.loc[idx] = {
                        'trade_deal': trade_data['trade_deal'], 'market': market, 'pair': pair,
                        'entry_date': entry_datetime.strftime(DATE_FORMAT) if entry_datetime else '',
                        'release_date': release_datetime.strftime(DATE_FORMAT) if release_datetime else '',
                        'risk_percent': risk_percent, 'tick_size': tick_size, 'entry_point': entry_point,
                        'stop_loss': stop_loss, 'take_profit_one': take_profit_one,
                        'take_profit_two': take_profit_two, 'take_profit_three': take_profit_three,
                        'take_profit_one_percent': take_profit_one_percent,
                        'take_profit_two_percent': take_profit_two_percent,
                        'take_profit_three_percent': take_profit_three_percent,
                        'trade_setup': trade_setup.split(': ')[1] if trade_setup else '',
                        'trade_setup_group': trade_setup_group,
                        'timeframe': timeframe, 'type': direction, 'session': session,
                        'avg_rr': avg_rr, 'profit_percent': profit_percent,
                        'result': result, 'status': trade_data['status'],
                        'notion_text': trade_data['notion_text'], 'screenshot': trade_data['screenshot'],
                        'entry_screenshot_1': entry_screenshot_paths[0], 'entry_screenshot_2': entry_screenshot_paths[1],
                        'entry_screenshot_3': entry_screenshot_paths[2],
                        'entry_description_1': entry_descriptions[0], 'entry_description_2': entry_descriptions[1],
                        'entry_description_3': entry_descriptions[2],
                        'exit_screenshot_1': exit_screenshot_paths[0], 'exit_screenshot_2': exit_screenshot_paths[1],
                        'exit_screenshot_3': exit_screenshot_paths[2],
                        'exit_description_1': exit_descriptions[0], 'exit_description_2': exit_descriptions[1],
                        'exit_description_3': exit_descriptions[2],
                        'trend_tag': trend_tag
                    }
                    save_trades(trades_df)
                    st.success(f"{lang.get('trade_updated', 'Сделка обновлена')}: {trade_data['trade_deal']}")
                    # Сбрасываем форму и скрываем её
                    st.session_state[edit_form_visible_key] = False
                    st.session_state[edit_trade_deal_key] = ''
                    # Очищаем ключи формы
                    form_keys = [
                        f'{market_lower}_edit_pair', f'{market_lower}_edit_entry_date', f'{market_lower}_edit_entry_time',
                        f'{market_lower}_edit_release_date', f'{market_lower}_edit_release_time', f'{market_lower}_edit_risk_percent',
                        f'{market_lower}_edit_tick_size', f'{market_lower}_edit_entry_point', f'{market_lower}_edit_stop_loss',
                        f'{market_lower}_edit_take_profit_one', f'{market_lower}_edit_take_profit_two', f'{market_lower}_edit_take_profit_three',
                        f'{market_lower}_edit_take_profit_one_percent', f'{market_lower}_edit_take_profit_two_percent',
                        f'{market_lower}_edit_take_profit_three_percent', f'{market_lower}_edit_trade_setup', f'{market_lower}_edit_timeframe',
                        f'{market_lower}_edit_trend_tag',
                        f'{market_lower}_edit_trade_select'
                    ] + [f'{market_lower}_edit_entry_screenshot_{i}' for i in range(3)] \
                    + [f'{market_lower}_edit_exit_screenshot_{i}' for i in range(3)] \
                    + [f'{market_lower}_edit_entry_description_{i}' for i in range(3)] \
                    + [f'{market_lower}_edit_exit_description_{i}' for i in range(3)] \
                    + [f'{market_lower}_delete_entry_screenshot_{i}' for i in range(3)] \
                    + [f'{market_lower}_delete_exit_screenshot_{i}' for i in range(3)]
                    for key in form_keys:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

                if delete_submitted:
                    for screenshot in existing_screenshots['entry'] + existing_screenshots['exit']:
                        if screenshot and isinstance(screenshot, str) and os.path.exists(screenshot):
                            try:
                                os.remove(screenshot)
                                logger.info(f"Удалён скриншот: {screenshot}")
                            except Exception as e:
                                logger.error(f"Ошибка удаления скриншота: {str(e)}")
                    trades_df = trades_df[trades_df['trade_deal'] != st.session_state[edit_trade_deal_key]].reset_index(drop=True)
                    save_trades(trades_df)
                    st.success(f"{lang.get('trade_deleted', 'Сделка удалена')}: {st.session_state[edit_trade_deal_key]}")
                    # Сбрасываем форму и скрываем её
                    st.session_state[edit_form_visible_key] = False
                    st.session_state[edit_trade_deal_key] = ''
                    st.rerun()

    except Exception as e:
        logger.error(f"Ошибка во вкладке ввода сделок ({market}): {str(e)}")
        st.error(f"{lang.get('error', 'Произошла ошибка')}: {str(e)}")