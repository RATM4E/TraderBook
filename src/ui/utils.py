import streamlit as st
import pandas as pd
import os
from PIL import Image
import io
from src.core.config import SCREENSHOTS_ENTRY_DIR, SCREENSHOTS_EXIT_DIR, SETUP_IMAGES_DIR
from src.core.logging_setup import logger

def validate_dates(entry_datetime, release_datetime, lang_dict):
    """Валидация дат входа и выхода."""
    if entry_datetime is None:
        st.error(lang_dict.get('entry_date_required', "Дата входа обязательна"))
        return False
    if release_datetime and entry_datetime and release_datetime < entry_datetime:
        st.error(lang_dict.get('date_validation_error', "Дата выхода должна быть позже даты входа"))
        return False
    return True

def validate_percentages(take_profit_one_percent, take_profit_two_percent, take_profit_three_percent, lang_dict):
    """Валидация процентов тейк-профитов."""
    total_percent = sum([p for p in [take_profit_one_percent, take_profit_two_percent, take_profit_three_percent] if p])
    if total_percent > 0 and not 99.9 <= total_percent <= 100.1:
        st.error(lang_dict.get('percent_sum_error', "Сумма процентов тейк-профитов должна быть 100%"))
        return False
    return True

def save_screenshot(uploaded_file, filename, screenshot_type, directory=SETUP_IMAGES_DIR):
    """Сохранение одного скриншота."""
    try:
        if uploaded_file and hasattr(uploaded_file, 'read'):
            # Формируем имя файла с учётом типа
            screenshot_filename = f"{filename}_{screenshot_type}.png" if screenshot_type else f"{filename}.png"
            screenshot_path = os.path.join(directory, screenshot_filename)
            img = Image.open(uploaded_file)
            img.save(screenshot_path, format='PNG')
            logger.info(f"Скриншот сохранён: {screenshot_path}")
            return screenshot_path
        return ''
    except Exception as e:
        logger.error(f"Ошибка сохранения скриншота {filename}: {str(e)}")
        return ''

def save_screenshots(entry_screenshots, exit_screenshots, trade_deal, edit_mode=False, existing_screenshots=None, deleted_screenshots=None):
    """Сохранение скриншотов входа и выхода."""
    try:
        entry_screenshot_paths = [''] * 3
        exit_screenshot_paths = [''] * 3
        existing_screenshots = existing_screenshots or {'entry': ['', '', ''], 'exit': ['', '', '']}
        deleted_screenshots = deleted_screenshots or {'entry': [False, False, False], 'exit': [False, False, False]}

        # Обработка скриншотов входа
        for i, screenshot in enumerate(entry_screenshots):
            if i >= 3:
                break
            if deleted_screenshots['entry'][i]:
                # Удаляем существующий скриншот, если он помечен для удаления
                old_path = existing_screenshots['entry'][i]
                if old_path and isinstance(old_path, str) and os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                        logger.info(f"Удалён скриншот входа {i+1}: {old_path}")
                    except Exception as e:
                        logger.error(f"Ошибка удаления скриншота входа {i+1}: {str(e)}")
                continue

            if isinstance(screenshot, str) and screenshot.strip() and os.path.exists(screenshot):
                # Если передан существующий путь, сохраняем его
                entry_screenshot_paths[i] = screenshot
                logger.debug(f"Сохранён существующий скриншот входа {i+1}: {screenshot}")
            elif hasattr(screenshot, 'read'):  # Проверяем, является ли это загруженным файлом
                screenshot_path = os.path.join(SCREENSHOTS_ENTRY_DIR, f"{trade_deal}_entry_{i+1}.png")
                try:
                    img = Image.open(screenshot)
                    img.save(screenshot_path, format='PNG')
                    entry_screenshot_paths[i] = screenshot_path
                    logger.info(f"Скриншот входа {i+1} сохранён: {screenshot_path}")
                except Exception as e:
                    logger.error(f"Ошибка сохранения скриншота входа {i+1}: {str(e)}")
            else:
                # Если скриншот не загружен и не удалён, сохраняем существующий путь
                if not edit_mode or not deleted_screenshots['entry'][i]:
                    entry_screenshot_paths[i] = existing_screenshots['entry'][i] if existing_screenshots['entry'][i] else ''

        # Обработка скриншотов выхода
        for i, screenshot in enumerate(exit_screenshots):
            if i >= 3:
                break
            if deleted_screenshots['exit'][i]:
                # Удаляем существующий скриншот, если он помечен для удаления
                old_path = existing_screenshots['exit'][i]
                if old_path and isinstance(old_path, str) and os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                        logger.info(f"Удалён скриншот выхода {i+1}: {old_path}")
                    except Exception as e:
                        logger.error(f"Ошибка удаления скриншота выхода {i+1}: {str(e)}")
                continue

            if isinstance(screenshot, str) and screenshot.strip() and os.path.exists(screenshot):
                # Если передан существующий путь, сохраняем его
                exit_screenshot_paths[i] = screenshot
                logger.debug(f"Сохранён существующий скриншот выхода {i+1}: {screenshot}")
            elif hasattr(screenshot, 'read'):  # Проверяем, является ли это загруженным файлом
                screenshot_path = os.path.join(SCREENSHOTS_EXIT_DIR, f"{trade_deal}_exit_{i+1}.png")
                try:
                    img = Image.open(screenshot)
                    img.save(screenshot_path, format='PNG')
                    exit_screenshot_paths[i] = screenshot_path
                    logger.info(f"Скриншот выхода {i+1} сохранён: {screenshot_path}")
                except Exception as e:
                    logger.error(f"Ошибка сохранения скриншота выхода {i+1}: {str(e)}")
            else:
                # Если скриншот не загружен и не удалён, сохраняем существующий путь
                if not edit_mode or not deleted_screenshots['exit'][i]:
                    exit_screenshot_paths[i] = existing_screenshots['exit'][i] if existing_screenshots['exit'][i] else ''

        return entry_screenshot_paths, exit_screenshot_paths
    except Exception as e:
        logger.error(f"Ошибка сохранения скриншотов: {str(e)}")
        return [''] * 3, [''] * 3