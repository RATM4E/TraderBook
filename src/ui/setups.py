import streamlit as st
import pandas as pd
import os
from src.core.config import SETUP_IMAGES_DIR, SETUPS_COLUMNS
from src.core.data_manager import load_setups, save_setups, load_groups, save_groups
from src.core.logging_setup import logger
from src.ui.utils import save_screenshot
from src.ui.translations import load_translations

def setups_tab():
    """Вкладка для управления сетапами."""
    try:
        lang = load_translations()[st.session_state.language]
        st.header(lang['setups'])

        # Секция управления группами
        st.subheader(lang.get('manage_groups', "Управление группами"))
        groups_df = load_groups()
        with st.form("add_group_form", clear_on_submit=True):
            new_group_name = st.text_input(lang.get('group_name', "Название группы"), key='new_group_name_input')
            add_group_submitted = st.form_submit_button(lang.get('add_group', "Добавить группу"))
            if add_group_submitted:
                if not new_group_name:
                    st.error(lang.get('group_name_required', "Название группы обязательно"))
                    return
                if new_group_name in groups_df['group_name'].values:
                    st.error(lang.get('group_name_exists', "Группа с таким названием уже существует"))
                    return
                new_group = pd.DataFrame([{'group_name': new_group_name}], columns=['group_name'])
                groups_df = pd.concat([groups_df, new_group], ignore_index=True)
                save_groups(groups_df)
                st.success(f"{lang.get('group_added', 'Группа добавлена')}: {new_group_name}")
                st.rerun()

        # Отображение существующих групп
        if not groups_df.empty:
            st.write(lang.get('existing_groups', "Существующие группы:"))
            for _, row in groups_df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(row['group_name'])
                with col2:
                    if st.button(lang.get('delete', "Удалить"), key=f"delete_group_{row['group_name']}"):
                        setups_df = load_setups()
                        if not setups_df.empty and row['group_name'] in setups_df['group_name'].values:
                            st.error(f"{lang.get('group_in_use', 'Нельзя удалить группу')} '{row['group_name']}', {lang.get('group_in_use_suffix', 'так как она используется в сетапах')}")
                        else:
                            groups_df = groups_df[groups_df['group_name'] != row['group_name']].reset_index(drop=True)
                            save_groups(groups_df)
                            st.success(f"{lang.get('group_deleted', 'Группа удалена')}: {row['group_name']}")
                            st.rerun()
        else:
            st.write(lang.get('no_groups', "Групп пока нет"))

        # Секция добавления сетапа
        st.subheader(lang.get('add_setup', "Добавить сетап"))
        with st.form("add_setup_form", clear_on_submit=True):
            setup_name = st.text_input(lang.get('setup_name', "Название сетапа"), key='new_setup_name')
            description = st.text_area(lang.get('description', "Описание"), key='new_description')
            image = st.file_uploader(lang.get('upload_image', "Загрузить изображение"), ['png', 'jpg', 'jpeg'], key='new_setup_image')
            group_name = st.selectbox(lang.get('group_name', "Название группы"), [''] + groups_df['group_name'].dropna().tolist(), key='new_group_name')
            submitted = st.form_submit_button(lang.get('submit', "Добавить"))
            if submitted:
                if not setup_name:
                    st.error(lang.get('setup_name_required', "Название сетапа обязательно"))
                    return
                if not group_name:
                    st.error(lang.get('group_name_required', "Выберите группу"))
                    return
                setups_df = load_setups()
                # Проверяем уникальность комбинации setup_name и group_name
                if not setups_df.empty and any((setups_df['setup_name'] == setup_name) & (setups_df['group_name'] == group_name)):
                    st.error(lang.get('setup_name_exists', "Сетап с таким названием уже существует в этой группе"))
                    return
                image_path = save_screenshot(image, f"{setup_name}_{group_name}", 'setup', SETUP_IMAGES_DIR) if image else ''
                new_setup = pd.DataFrame([{
                    'setup_name': setup_name,
                    'image_path': image_path,
                    'description': description,
                    'group_name': group_name
                }], columns=SETUPS_COLUMNS)
                setups_df = pd.concat([setups_df, new_setup], ignore_index=True)
                save_setups(setups_df)
                st.success(f"{lang.get('setup_added', 'Сетап добавлен')}: {setup_name}")
                st.rerun()

        # Секция редактирования сетапа
        st.subheader(lang.get('edit_setup', "Редактировать сетап"))
        setups_df = load_setups()
        # Формируем список сетапов с указанием групп для уникальности
        setups_df['display_setup'] = setups_df['group_name'] + ': ' + setups_df['setup_name']
        setup_options = [''] + setups_df['display_setup'].dropna().tolist()
        setup_to_edit = st.selectbox(lang.get('select_setup', "Выберите сетап"), setup_options, key='setup_to_edit')
        if setup_to_edit:
            # Находим сетап по комбинации group_name и setup_name
            matching_setups = setups_df[setups_df['display_setup'] == setup_to_edit]
            if matching_setups.empty:
                st.error(f"{lang.get('setup_not_found', 'Сетап не найден')}: {setup_to_edit}")
                logger.error(f"Сетап '{setup_to_edit}' не найден в setups_df")
                return
            idx = matching_setups.index[0]
            setup_data = setups_df.loc[idx]
            with st.form("edit_setup_form", clear_on_submit=False):
                new_setup_name = st.text_input(lang.get('setup_name', "Название сетапа"), value=setup_data['setup_name'] or '', key='edit_setup_name')
                new_description = st.text_area(lang.get('description', "Описание"), value=setup_data['description'] or '', key='edit_description')
                new_image = st.file_uploader(lang.get('upload_image', "Загрузить изображение"), ['png', 'jpg', 'jpeg'], key='edit_setup_image')
                # Отображаем текущий скриншот
                if setup_data['image_path'] and isinstance(setup_data['image_path'], str) and os.path.exists(setup_data['image_path']):
                    st.image(setup_data['image_path'], caption=lang.get('current_image', "Текущее изображение"), width=200)
                    delete_image = st.checkbox(lang.get('delete_screenshot', "Удалить изображение"), key='delete_setup_image')
                else:
                    delete_image = False
                # Выбор группы
                group_options = [''] + groups_df['group_name'].dropna().tolist()
                default_index = group_options.index(setup_data['group_name']) if setup_data['group_name'] in group_options else 0
                new_group_name = st.selectbox(
                    lang.get('group_name', "Название группы"),
                    group_options,
                    index=int(default_index),
                    key='edit_group_name'
                )
                col_update, col_delete = st.columns(2)
                with col_update:
                    update_submitted = st.form_submit_button(lang.get('update_setup', "Обновить"))
                with col_delete:
                    delete_submitted = st.form_submit_button(lang.get('delete_setup', "Удалить"))

                if update_submitted:
                    if not new_setup_name:
                        st.error(lang.get('setup_name_required', "Название сетапа обязательно"))
                        return
                    if not new_group_name:
                        st.error(lang.get('group_name_required', "Выберите группу"))
                        return
                    # Проверяем, не конфликтует ли новое имя с существующим
                    existing_setups = setups_df[setups_df.index != idx]
                    if not existing_setups.empty and any((existing_setups['setup_name'] == new_setup_name) & (existing_setups['group_name'] == new_group_name)):
                        st.error(lang.get('setup_name_exists', "Сетап с таким названием уже существует в этой группе"))
                        return
                    new_image_path = setup_data['image_path']
                    if delete_image and new_image_path and isinstance(new_image_path, str) and os.path.exists(new_image_path):
                        try:
                            os.remove(new_image_path)
                            logger.info(f"Удалён скриншот сетапа: {new_image_path}")
                            new_image_path = ''
                        except Exception as e:
                            logger.error(f"Ошибка удаления скриншота сетапа: {str(e)}")
                    if new_image:
                        # Удаляем старый скриншот, если он существует
                        if new_image_path and isinstance(new_image_path, str) and os.path.exists(new_image_path):
                            try:
                                os.remove(new_image_path)
                                logger.info(f"Удалён старый скриншот сетапа при замене: {new_image_path}")
                            except Exception as e:
                                logger.error(f"Ошибка удаления старого скриншота: {str(e)}")
                        new_image_path = save_screenshot(new_image, f"{new_setup_name}_{new_group_name}", 'setup', SETUP_IMAGES_DIR)
                    setups_df.loc[idx] = {
                        'setup_name': new_setup_name,
                        'image_path': new_image_path,
                        'description': new_description,
                        'group_name': new_group_name
                    }
                    save_setups(setups_df)
                    st.success(f"{lang.get('setup_updated', 'Сетап обновлён')}: {new_setup_name}")
                    st.rerun()

                if delete_submitted:
                    image_path = setup_data['image_path']
                    if image_path and isinstance(image_path, str) and os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            logger.info(f"Удалён скриншот сетапа: {image_path}")
                        except Exception as e:
                            logger.error(f"Ошибка удаления скриншота сетапа: {str(e)}")
                    setups_df = setups_df.drop(idx).reset_index(drop=True)
                    save_setups(setups_df)
                    st.success(f"{lang.get('setup_deleted', 'Сетап удалён')}: {setup_to_edit}")
                    st.rerun()

        # Секция просмотра сетапов
        st.subheader(lang.get('view_setups', 'Просмотр сетапов'))
        group_filter = st.selectbox(lang.get('filter_by_group', 'Фильтрация по группе'), [''] + groups_df['group_name'].dropna().tolist(), key='group_filter')
        if group_filter:
            filtered_setups = setups_df[setups_df['group_name'] == group_filter]
        else:
            filtered_setups = setups_df
        for _, row in filtered_setups.iterrows():
            st.write(f"**{lang.get('setup_name', 'Название сетапа')}:** {row['setup_name']}")
            st.write(f"**{lang.get('description', 'Описание')}:** {row['description']}")
            st.write(f"**{lang.get('group_name', 'Группа')}:** {row['group_name']}")
            if isinstance(row['image_path'], str) and row['image_path'] and os.path.exists(row['image_path']):
                st.image(row['image_path'], caption=lang.get('setup_image', 'Изображение сетапа'))
            st.markdown('---')

    except Exception as e:
        logger.error(f"Ошибка во вкладке сетапов: {str(e)}")
        st.error(f"{lang.get('error', 'Произошла ошибка')}: {str(e)}")