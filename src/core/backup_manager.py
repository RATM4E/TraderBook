import os
import shutil
import zipfile
from datetime import datetime
from src.core.config import (
    BASE_DIR, DATA_DIR, TRADES_FILE, SETUPS_FILE,
    SCREENSHOTS_DIR, SETUP_IMAGES_DIR, BACKUPS_DIR
)
from src.core.logging_setup import backup_logger

def create_backup():
    """Создание резервной копии в ZIP."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_backup_dir = os.path.join(DATA_DIR, f"temp_backup_{timestamp}")
        os.makedirs(temp_backup_dir, exist_ok=True)

        # Копирование файлов и папок
        items_to_backup = [
            (TRADES_FILE, os.path.join(temp_backup_dir, "trades.csv")),
            (SETUPS_FILE, os.path.join(temp_backup_dir, "setups.csv")),
            (SCREENSHOTS_DIR, os.path.join(temp_backup_dir, "screenshots")),
            (SETUP_IMAGES_DIR, os.path.join(temp_backup_dir, "setup_images")),
        ]
        for src, dst in items_to_backup:
            if os.path.exists(src):
                if os.path.isfile(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    backup_logger.info(f"Скопировано: {src} -> {dst}")
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    backup_logger.info(f"Скопировано: {src} -> {dst}")
            else:
                backup_logger.warning(f"Предупреждение: {src} не найден, пропущен.")

        # Упаковка в ZIP
        zip_path = os.path.join(BACKUPS_DIR, f"backup_{timestamp}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_backup_dir)
                    zipf.write(file_path, arcname)
        backup_logger.info(f"ZIP-архив создан: {zip_path}")

        # Удаление временной папки
        shutil.rmtree(temp_backup_dir)
        backup_logger.info(f"Резервная копия успешно создана в {zip_path}")
        return True, None
    except Exception as e:
        backup_logger.error(f"Ошибка при создании резервной копии: {str(e)}")
        return False, str(e)

def restore_backup(zip_path):
    """Восстановление данных из ZIP-архива."""
    try:
        temp_extract_dir = os.path.join(DATA_DIR, f"temp_extract_{os.path.basename(zip_path).replace('.zip', '')}")
        os.makedirs(temp_extract_dir, exist_ok=True)

        # Распаковка ZIP
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(temp_extract_dir)
        backup_logger.info(f"ZIP-архив распакован в {temp_extract_dir}")

        # Восстановление файлов и папок
        items_to_restore = [
            (os.path.join(temp_extract_dir, "trades.csv"), TRADES_FILE),
            (os.path.join(temp_extract_dir, "setups.csv"), SETUPS_FILE),
            (os.path.join(temp_extract_dir, "screenshots"), SCREENSHOTS_DIR),
            (os.path.join(temp_extract_dir, "setup_images"), SETUP_IMAGES_DIR),
        ]
        restored_items = []
        for src, dst in items_to_restore:
            if os.path.exists(src):
                try:
                    if os.path.isfile(src):
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                        restored_items.append(os.path.basename(src))
                        backup_logger.info(f"Восстановлено: {src} -> {dst}")
                    elif os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                        restored_items.append(os.path.basename(src))
                        backup_logger.info(f"Восстановлено: {src} -> {dst}")
                except Exception as e:
                    backup_logger.warning(f"Не удалось восстановить {os.path.basename(src)}: {str(e)}")
            else:
                backup_logger.warning(f"{os.path.basename(src)} не найден в бэкапе.")
        shutil.rmtree(temp_extract_dir)
        backup_logger.info("Временная папка удалена")
        return True, restored_items
    except Exception as e:
        backup_logger.error(f"Ошибка при восстановлении: {str(e)}")
        return False, str(e)