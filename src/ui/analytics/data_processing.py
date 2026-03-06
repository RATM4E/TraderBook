import pandas as pd
import pytz
from src.core.logging_setup import logger

def filter_trades_by_market(trades_df, market):
    """Фильтрация сделок по рынку."""
    try:
        filtered_df = trades_df[trades_df['market'] == market]
        logger.info(f"Фильтрация по рынку {market}: {len(filtered_df)} сделок")
        return filtered_df
    except Exception as e:
        logger.error(f"Ошибка фильтрации по рынку {market}: {str(e)}")
        return pd.DataFrame()

def prepare_time_histogram_data(trades_df, timezone, lang):
    """Подготовка данных для гистограммы времени."""
    try:
        if trades_df.empty:
            logger.info("Нет данных для гистограммы времени")
            return pd.DataFrame()
        entry_df = trades_df[['entry_date']].copy()
        entry_df['Hour'] = entry_df['entry_date'].dt.tz_convert(pytz.FixedOffset(timezone * 60)).dt.hour
        entry_df['Type'] = lang.get('entry_date', 'Открытие')
        release_df = trades_df[trades_df['release_date'].notna()][['release_date']].copy()
        release_df['Hour'] = release_df['release_date'].dt.tz_convert(pytz.FixedOffset(timezone * 60)).dt.hour
        release_df['Type'] = lang.get('release_date', 'Закрытие')
        combined_df = pd.concat([entry_df[['Hour', 'Type']], release_df[['Hour', 'Type']]], ignore_index=True)
        logger.info(f"Подготовлено {len(combined_df)} записей для гистограммы времени")
        return combined_df
    except Exception as e:
        logger.error(f"Ошибка подготовки данных для гистограммы времени: {str(e)}")
        return pd.DataFrame()

def prepare_day_of_week_data(trades_df, timezone, lang):
    """Подготовка данных для гистограммы дней недели."""
    try:
        filtered_df = trades_df[trades_df['status'] == 'Закрытая']
        if filtered_df.empty:
            logger.info("Нет закрытых сделок для гистограммы дней недели")
            return pd.DataFrame()
        entry_df = filtered_df[['entry_date']].copy()
        entry_df['Day'] = entry_df['entry_date'].dt.tz_convert(pytz.FixedOffset(timezone * 60)).dt.day_name()
        entry_df['Type'] = lang.get('entry_date', 'Открытие')
        release_df = filtered_df[filtered_df['release_date'].notna()][['release_date']].copy()
        release_df['Day'] = release_df['release_date'].dt.tz_convert(pytz.FixedOffset(timezone * 60)).dt.day_name()
        release_df['Type'] = lang.get('release_date', 'Закрытие')
        combined_df = pd.concat([entry_df[['Day', 'Type']], release_df[['Day', 'Type']]], ignore_index=True)
        logger.info(f"Подготовлено {len(combined_df)} записей для гистограммы дней недели")
        return combined_df
    except Exception as e:
        logger.error(f"Ошибка подготовки данных для гистограммы дней недели: {str(e)}")
        return pd.DataFrame()