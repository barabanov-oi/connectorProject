import json
import os
from models.connector import Connector
from extensions import db

def transliterate(name):
    """Транслитерация русских букв и замена пробелов на _"""
    ru_en = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        ' ': '_', '.': '_', ',': '_'
    }
    return ''.join(ru_en.get(c.lower(), c) for c in name).lower()

def get_user_config_path(user_id):
    """Создает директорию для конфигураций пользователя."""
    user_path = os.path.join("static/users", str(user_id), "connectors")
    os.makedirs(user_path, exist_ok=True)
    return user_path

def save_connector_config(name, config_data, user_id):
    """Сохраняет конфигурацию коннектора."""
    # Транслитерация имени файла
    file_name = f"{transliterate(name)}.json"
    user_path = get_user_config_path(user_id)
    file_path = os.path.join(user_path, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)

def load_connector_config(connector_name, user_id):
    """Загружает конфигурацию коннектора из JSON-файла."""
    user_path = get_user_config_path(user_id)
    file_path = os.path.join(user_path, f"{connector_name}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_all_connectors(user_id):
    """Загружает список всех доступных коннекторов для указанного пользователя."""
    user_path = get_user_config_path(user_id)
    connectors = []
    if os.path.exists(user_path):
        for filename in os.listdir(user_path):
            file_path = os.path.join(user_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                connectors.append({
                    "name": filename.replace(".json", ""),
                    "service": config.get("CONNECTOR_TYPE", "Неизвестный сервис"),
                    "type": config.get("CONNECTOR_TYPE", "unknown")
                })
    return connectors

USERS_PATH = "static/users"
os.makedirs(USERS_PATH, exist_ok=True)

def get_user_config_path(user_id):
    """Создает директорию для конфигураций пользователя."""
    user_path = os.path.join(USERS_PATH, str(user_id), "connectors")
    os.makedirs(user_path, exist_ok=True)
    return user_path