import pandas as pd
import os
import streamlit as st
from datetime import datetime
from src.core.config import TRADES_FILE, SETUPS_FILE, GROUPS_FILE, TRADES_COLUMNS, SETUPS_COLUMNS, GROUPS_COLUMNS
from src.core.logging_setup import logger, csv_logger
from src.ui.utils import validate_dates, validate_percentages

def load_trades():
    """Загрузка сделок из trades.csv."""
    try:
        if os.path.exists(TRADES_FILE):
            # Попробуем сначала utf-8
            try:
                trades_df = pd.read_csv(TRADES_FILE, encoding='utf-8', parse_dates=['entry_date', 'release_date'])
                csv_logger.info(f"Успешно загружен файл {TRADES_FILE} с кодировкой utf-8")
            except UnicodeDecodeError:
                # Если utf-8 не сработал, пробуем utf-8-sig
                trades_df = pd.read_csv(TRADES_FILE, encoding='utf-8-sig', parse_dates=['entry_date', 'release_date'])
                csv_logger.info(f"Успешно загружен файл {TRADES_FILE} с кодировкой utf-8-sig")
            logger.info(f"Загружено {len(trades_df)} сделок из {TRADES_FILE}")
            return trades_df
        else:
            csv_logger.warning(f"Файл {TRADES_FILE} не найден, возвращён пустой DataFrame")
            logger.info(f"Файл {TRADES_FILE} не найден")
            return pd.DataFrame(columns=TRADES_COLUMNS)
    except Exception as e:
        logger.error(f"Ошибка загрузки trades.csv: {str(e)}")
        csv_logger.error(f"Ошибка загрузки trades.csv: {str(e)}")
        return pd.DataFrame(columns=TRADES_COLUMNS)

def save_trades(trades_df):
    """Сохранение сделок в trades.csv."""
    try:
        trades_df.to_csv(TRADES_FILE, index=False, encoding='utf-8')
        logger.info("Сделки сохранены в trades.csv")
        csv_logger.info(f"Сделки успешно сохранены в {TRADES_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения trades.csv: {str(e)}")
        csv_logger.error(f"Ошибка сохранения trades.csv: {str(e)}")
        raise

def load_setups():
    """Загрузка сетапов из setups.csv."""
    try:
        if os.path.exists(SETUPS_FILE):
            setups_df = pd.read_csv(SETUPS_FILE, encoding='utf-8')
            csv_logger.info(f"Успешно загружен файл {SETUPS_FILE}")
            return setups_df
        else:
            csv_logger.warning(f"Файл {SETUPS_FILE} не найден, возвращён пустой DataFrame")
            return pd.DataFrame(columns=SETUPS_COLUMNS)
    except Exception as e:
        logger.error(f"Ошибка загрузки setups.csv: {str(e)}")
        csv_logger.error(f"Ошибка загрузки setups.csv: {str(e)}")
        return pd.DataFrame(columns=SETUPS_COLUMNS)

def save_setups(setups_df):
    """Сохранение сетапов в setups.csv."""
    try:
        setups_df.to_csv(SETUPS_FILE, index=False, encoding='utf-8')
        logger.info("Сетапы сохранены в setups.csv")
        csv_logger.info(f"Сетапы успешно сохранены в {SETUPS_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения setups.csv: {str(e)}")
        csv_logger.error(f"Ошибка сохранения setups.csv: {str(e)}")
        raise

def load_groups():
    """Загрузка групп из groups.csv."""
    try:
        if os.path.exists(GROUPS_FILE):
            groups_df = pd.read_csv(GROUPS_FILE, encoding='utf-8-sig')  # Используем utf-8-sig для обработки BOM
            csv_logger.info(f"Успешно загружен файл {GROUPS_FILE}")
            logger.debug(f"Содержимое groups_df после загрузки: {groups_df.to_dict()}")
            return groups_df
        else:
            csv_logger.warning(f"Файл {GROUPS_FILE} не найден, возвращён пустой DataFrame")
            logger.debug(f"Файл {GROUPS_FILE} не найден, возвращён пустой DataFrame с колонками {GROUPS_COLUMNS}")
            return pd.DataFrame(columns=GROUPS_COLUMNS)
    except Exception as e:
        logger.error(f"Ошибка загрузки groups.csv: {str(e)}")
        csv_logger.error(f"Ошибка загрузки groups.csv: {str(e)}")
        return pd.DataFrame(columns=GROUPS_COLUMNS)

def save_groups(groups_df):
    """Сохранение групп в groups.csv."""
    try:
        groups_df.to_csv(GROUPS_FILE, index=False, encoding='utf-8')
        logger.info("Группы сохранены в groups.csv")
        csv_logger.info(f"Группы успешно сохранены в {GROUPS_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения groups.csv: {str(e)}")
        csv_logger.error(f"Ошибка сохранения groups.csv: {str(e)}")
        raise

def import_csv(uploaded_file):
    """Импорт данных из CSV."""
    try:
        lang = st.session_state.get('language', 'ru')
        translations = {
            'ru': {
                'csv_import_success': 'CSV успешно импортирован!',
                'csv_import_warning': 'Некоторые строки пропущены из-за ошибок: {errors}',
                'csv_missing_columns': 'В CSV отсутствуют новые колонки: {cols}. Заполнены пустыми значениями.'
            },
            'uk': {
                'csv_import_success': 'CSV успішно імпортовано!',
                'csv_import_warning': 'Деякі рядки пропущено через помилки: {errors}',
                'csv_missing_columns': 'У CSV відсутні нові колонки: {cols}. Заповнено порожніми значеннями.'
            },
            'en': {
                'csv_import_success': 'CSV successfully imported!',
                'csv_import_warning': 'Some rows were skipped due to errors: {errors}',
                'csv_missing_columns': 'CSV is missing new columns: {cols}. Filled with empty values.'
            }
        }
        lang_dict = translations.get(lang, translations['ru'])

        trades_df = load_trades()
        new_data = pd.read_csv(uploaded_file, encoding='utf-8')
        csv_logger.info(f"Начало импорта CSV: {uploaded_file.name}")

        missing_cols = [col for col in TRADES_COLUMNS if col not in new_data.columns]
        if missing_cols:
            for col in missing_cols:
                new_data[col] = ''
            st.warning(lang_dict['csv_missing_columns'].format(cols=', '.join(missing_cols)))
            logger.info(f"Отсутствующие колонки в импорте: {missing_cols}")
            csv_logger.info(f"Отсутствующие колонки в импорте: {missing_cols}")

        valid_rows = []
        errors = []
        for idx, row in new_data.iterrows():
            try:
                entry_dt = pd.to_datetime(row['entry_date']) if pd.notna(row['entry_date']) else None
                release_dt = pd.to_datetime(row['release_date']) if pd.notna(row['release_date']) else None
                dates_valid = validate_dates(entry_dt, release_dt, lang_dict)

                percent_valid = validate_percentages(
                    row['take_profit_one_percent'],
                    row['take_profit_two_percent'],
                    row['take_profit_three_percent'],
                    lang_dict
                )

                if dates_valid and percent_valid:
                    valid_rows.append(row)
                else:
                    errors.append(f"Строка {idx+2}: неверные даты или проценты")
            except Exception as e:
                errors.append(f"Строка {idx+2}: {str(e)}")

        if valid_rows:
            valid_df = pd.DataFrame(valid_rows, columns=TRADES_COLUMNS)
            trades_df = pd.concat([trades_df, valid_df], ignore_index=True)
            save_trades(trades_df)
            st.toast(lang_dict['csv_import_success'], icon="✅")
            logger.info(f"Импортировано {len(valid_rows)} строк из CSV")
            csv_logger.info(f"Импортировано {len(valid_rows)} строк из CSV")
        else:
            st.error("Нет валидных строк для импорта")
            logger.error("Импорт CSV не удался: нет валидных строк")
            csv_logger.error("Импорт CSV не удался: нет валидных строк")
            return False

        if errors:
            st.warning(lang_dict['csv_import_warning'].format(errors='; '.join(errors)))
            logger.warning(f"Пропущены строки при импорте: {errors}")
            csv_logger.warning(f"Пропущены строки при импорте: {errors}")

        return True
    except Exception as e:
        logger.error(f"Ошибка импорта CSV: {str(e)}")
        csv_logger.error(f"Ошибка импорта CSV: {str(e)}")
        st.error(f"Ошибка импорта: {str(e)}")
        return False