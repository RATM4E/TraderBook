import streamlit as st
import os
import platform
from src.core.config import DATA_DIR, TIMEZONE_FILE, LANGUAGE_FILE, REWARD_RISK_FILE, BACKUPS_DIR
from src.core.backup_manager import create_backup, restore_backup
from src.core.data_manager import import_csv
from src.core.logging_setup import logger
from src.ui.translations import load_translations

def setup_sidebar():
    """Настройка боковой панели."""
    try:
        translations = load_translations()
        lang = translations.get(st.session_state.language, translations.get('ru', {}))

        # Выбор языка
        lang_mapping = {'Русский': 'ru', 'Українська': 'uk', 'English': 'en'}
        display_mapping = {v: k for k, v in lang_mapping.items()}
        language_options = list(lang_mapping.keys())
        current_display = display_mapping.get(st.session_state.language, 'Русский')
        selected_display = st.sidebar.selectbox(
            lang.get('select_language', 'Select language'),
            language_options,
            index=language_options.index(current_display),
            key='language_selectbox',
            label_visibility='visible'
        )
        selected_language = lang_mapping[selected_display]
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            with open(LANGUAGE_FILE, 'w', encoding='utf-8') as f:
                f.write(selected_language)
            st.rerun()

        # Настройка часового пояса
        if 'change_timezone' not in st.session_state:
            st.session_state.change_timezone = False
        if st.session_state.change_timezone:
            timezone = st.sidebar.number_input(
                lang.get('select_timezone', 'Select timezone'),
                min_value=-12,
                max_value=14,
                value=st.session_state.timezone,
                step=1,
                label_visibility='visible'
            )
            if st.sidebar.button("OK"):
                st.session_state.timezone = timezone
                with open(TIMEZONE_FILE, 'w') as f:
                    f.write(str(timezone))
                st.session_state.change_timezone = False
                st.rerun()
        else:
            st.sidebar.write(lang.get('current_timezone', 'Current timezone: UTC{offset}').format(offset=f"{st.session_state.timezone:+d}"))
            if st.sidebar.button(lang.get('change_timezone', 'Change timezone')):
                st.session_state.change_timezone = True
                st.rerun()

        # Настройка Reward/Risk
        if 'reward_risk' not in st.session_state:
            try:
                with open(REWARD_RISK_FILE, 'r') as f:
                    st.session_state.reward_risk = float(f.read().strip())
            except:
                st.session_state.reward_risk = 0.5

        reward_risk = st.sidebar.number_input(
            lang.get('reward_risk', 'Risk per 1 reward, %'),
            min_value=0.0,
            format="%.2f",
            step=0.1,
            value=st.session_state.reward_risk,
            key='reward_risk_input',
            label_visibility='visible'
        )
        if reward_risk != st.session_state.reward_risk:
            st.session_state.reward_risk = reward_risk
            try:
                with open(REWARD_RISK_FILE, 'w') as f:
                    f.write(str(reward_risk))
                logger.info(f"Reward/Risk обновлён: {reward_risk}")
            except Exception as e:
                logger.error(f"Ошибка записи Reward/Risk в файл: {e}")
                st.sidebar.error(f"Ошибка сохранения Reward/Risk: {e}")

        # Создание резервной копии
        if st.sidebar.button(lang.get('create_backup', 'Create backup'), key="create_backup"):
            success, error = create_backup()
            if success:
                st.sidebar.success(lang.get('backup_success', 'Backup created!'))
            else:
                st.sidebar.error(lang.get('backup_error', 'Error creating backup: {error}').format(error=error))

        # Восстановление из ZIP
        st.sidebar.write(lang.get('restore_backup', 'Restore from backup'))
        if not os.path.exists(BACKUPS_DIR):
            st.sidebar.error(f"Директория {BACKUPS_DIR} не найдена.")
        else:
            backup_zips = [f for f in os.listdir(BACKUPS_DIR) if f.startswith("backup_") and f.endswith(".zip")]
            if not backup_zips:
                st.sidebar.warning("ZIP-архивы бэкапов не найдены.")
            selected_backup = st.sidebar.selectbox(
                lang.get('select_backup', 'Select backup ZIP'),
                [''] + sorted(backup_zips, reverse=True),
                key='restore_backup',
                label_visibility='visible'
            )
            if selected_backup and st.sidebar.button(lang.get('restore_button', 'Restore'), key="restore_button"):
                success, result = restore_backup(os.path.join(BACKUPS_DIR, selected_backup))
                if success:
                    st.sidebar.success(f"{lang.get('restore_success', 'Restore successful!')} Восстановлены: {', '.join(result)}")
                else:
                    st.sidebar.error(lang.get('restore_error', 'Restore error: {error}').format(error=result))

        # Импорт CSV
        st.sidebar.write(lang.get('upload_csv', 'Import CSV'))
        st.sidebar.write(lang.get('csv_instruction', 'CSV file must contain columns: ...'))
        uploaded_file = st.sidebar.file_uploader(
            lang.get('upload_csv', 'Import CSV'),
            type='csv',
            key='csv_upload',
            label_visibility='collapsed'
        )
        if uploaded_file:
            if import_csv(uploaded_file):
                st.sidebar.success(lang.get('csv_success', 'CSV data imported!'))
            else:
                st.sidebar.error("Ошибка импорта CSV")

        st.sidebar.markdown("---")

        # Завершение приложения
        if st.sidebar.button(lang.get('close_button', 'Close'), key="close_app_button"):
            try:
                if platform.system() == "Windows":
                    result = os.system("taskkill /IM TraderBook.exe /F")
                else:
                    result = 1
                if result == 0:
                    st.sidebar.success(lang.get('process_termination_success', 'Process terminated successfully.'))
                else:
                    st.sidebar.error(lang.get('process_termination_failure', 'Failed to terminate process.'))
                st.sidebar.warning(lang.get('close_warning', 'Application closed. Please close the browser manually.'))
                st.session_state.show_close_warning = True
                st.stop()
            except Exception as e:
                st.sidebar.error(f"{lang.get('process_termination_failure', 'Failed to terminate process.')} Ошибка: {str(e)}")

        if st.session_state.show_close_warning:
            st.sidebar.markdown(
                f'<div style="color: red; font-size: 14px; font-weight: bold;">{lang.get("close_warning", "Application closed.")}</div>',
                unsafe_allow_html=True
            )

    except Exception as e:
        logger.error(f"Ошибка в настройке боковой панели: {str(e)}")
        st.sidebar.error(f"Произошла ошибка: {str(e)}")