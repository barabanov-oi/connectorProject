import json
import os

CONNECTOR_CONFIG_PATH = "services/connectors/config"
CONNECTORS_PATH = "services/connectors/config"
os.makedirs(CONNECTOR_CONFIG_PATH, exist_ok=True)  # Create directory if it doesn't exist


def get_user_config_path(user_id):
    """Создает директорию для конфигураций пользователя."""
    user_path = os.path.join(CONNECTOR_CONFIG_PATH, str(user_id))
    os.makedirs(user_path, exist_ok=True)
    return user_path

def save_connector_config(connector_name, config_data, user_id):
    """Сохраняет конфигурацию коннектора."""
    file_name = f"{connector_name}.json"
    user_path = get_user_config_path(user_id)
    file_path = os.path.join(user_path, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


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
    for filename in os.listdir(user_path):
        file_path = os.path.join(user_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            connectors.append({
                "name": filename.replace(".json", ""),
                "service": config.get("CONNECTOR_SERVICE", "Неизвестный сервис"),
                "type": config.get("CONNECTOR_TYPE", "unknown")  # read / write
            })
    return connectors
from models.connector import Connector
from extensions import db
import os
import json

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

def save_connector_config(name, config_data, user_id):
    """Сохраняет конфигурацию коннектора в файл и БД."""
    # Сохраняем конфиг в файл
    config_path = "services/connectors/config"
    os.makedirs(config_path, exist_ok=True)
    
    # Транслитерация имени файла
    file_name = f"{transliterate(name)}.json"
    file_path = os.path.join(config_path, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    # Сохраняем в БД
    connector = Connector(
        name=name,
        connector_type=config_data.get("CONNECTOR_TYPE", "read"),
        service=config_data.get("CONNECTOR_SERVICE", "Unknown"),
        config_file=file_name,
        user_id=user_id
    )
    
    db.session.add(connector)
    db.session.commit()
