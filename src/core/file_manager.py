import os
import pandas as pd
from src.core.config import TRADES_FILE, SETUPS_FILE, GROUPS_FILE, TRADES_COLUMNS, SETUPS_COLUMNS, GROUPS_COLUMNS
from src.core.logging_setup import logger

def initialize_files():
    """Инициализация файлов trades.csv, setups.csv и groups.csv с нужными колонками."""
    try:
        # Создаём всю структуру папок если не существует
        from src.core.paths import ensure_user_data_dir, load_user_data_dir
        ensure_user_data_dir(load_user_data_dir())
        
        # Инициализация trades.csv
        if not os.path.exists(TRADES_FILE):
            trades_df = pd.DataFrame(columns=TRADES_COLUMNS)
            trades_df.to_csv(TRADES_FILE, index=False, encoding='utf-8')
            logger.info(f"Создан файл {TRADES_FILE}")
        else:
            # Проверка наличия всех колонок
            trades_df = pd.read_csv(TRADES_FILE, encoding='utf-8')
            missing_cols = [col for col in TRADES_COLUMNS if col not in trades_df.columns]
            if missing_cols:
                for col in missing_cols:
                    trades_df[col] = ''
                # Миграция старых данных
                migrated = False
                if 'entry_screenshot' in trades_df.columns and 'entry_screenshot_1' in missing_cols:
                    trades_df['entry_screenshot_1'] = trades_df['entry_screenshot'].where(trades_df['entry_screenshot'].notna() & (trades_df['entry_screenshot'] != ''), '')
                    trades_df['entry_description_1'] = trades_df.get('entry_description', '').where(trades_df.get('entry_description', '').notna() & (trades_df.get('entry_description', '') != ''), '')
                    migrated = True
                if 'exit_screenshot' in trades_df.columns and 'exit_screenshot_1' in missing_cols:
                    trades_df['exit_screenshot_1'] = trades_df['exit_screenshot'].where(trades_df['exit_screenshot'].notna() & (trades_df['exit_screenshot'] != ''), '')
                    trades_df['exit_description_1'] = trades_df.get('exit_description', '').where(trades_df.get('exit_description', '').notna() & (trades_df.get('exit_description', '') != ''), '')
                    migrated = True
                if migrated:
                    trades_df.to_csv(TRADES_FILE, index=False, encoding='utf-8')
                    logger.info(f"Миграция данных в {TRADES_FILE}: добавлены колонки {missing_cols}, перенесены данные из entry_screenshot/exit_screenshot")

        # Инициализация setups.csv
        if not os.path.exists(SETUPS_FILE):
            setups_df = pd.DataFrame(columns=SETUPS_COLUMNS)
            setups_df.to_csv(SETUPS_FILE, index=False, encoding='utf-8')
            logger.info(f"Создан файл {SETUPS_FILE}")
        else:
            setups_df = pd.read_csv(SETUPS_FILE, encoding='utf-8')
            missing_cols = [col for col in SETUPS_COLUMNS if col not in setups_df.columns]
            if missing_cols:
                for col in missing_cols:
                    setups_df[col] = ''
                setups_df.to_csv(SETUPS_FILE, index=False, encoding='utf-8')
                logger.info(f"Миграция данных в {SETUPS_FILE}: добавлены колонки {missing_cols}")

        # Инициализация groups.csv
        if not os.path.exists(GROUPS_FILE):
            groups_df = pd.DataFrame(columns=GROUPS_COLUMNS)
            groups_df.to_csv(GROUPS_FILE, index=False, encoding='utf-8')
            logger.info(f"Создан файл {GROUPS_FILE}")
    except Exception as e:
        logger.error(f"Ошибка при инициализации файлов: {str(e)}")
        raise