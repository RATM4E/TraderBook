import json
import os
import logging
from src.core.config import BASE_DIR
import streamlit as st

logger = logging.getLogger(__name__)

@st.cache_data
def load_translations():
    translations = {}
    base_dir = os.path.normpath(BASE_DIR)
    logger.debug(f"BASE_DIR: {base_dir}")
    logger.debug(f"Текущая директория: {os.getcwd()}")
    
    trans_dir = os.path.join(os.getcwd(), 'src', 'translations')
    logger.debug(f"Папка переводов: {trans_dir}")
    
    for lang in ['ru', 'uk', 'en']:
        file_path = os.path.normpath(os.path.join(trans_dir, f'{lang}.json'))
        logger.debug(f"Проверяю: {file_path}, Существует: {os.path.exists(file_path)}")
        if not os.path.exists(file_path):
            logger.error(f"Файл {file_path} не найден")
            translations[lang] = {}
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                translations[lang] = data
            logger.info(f"Загружен {file_path}")
        except Exception as e:
            logger.error(f"Ошибка с {file_path}: {str(e)}")
            translations[lang] = {}
    
    if not translations:
        logger.warning("Нет переводов")
        translations["ru"] = {"select_language": "Выберите язык"}  # Фаллбэк
    else:
        logger.debug(f"Загружено: {list(translations.keys())}")
    return translations