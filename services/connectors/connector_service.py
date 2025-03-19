import json
import os

CONNECTOR_CONFIG_PATH = "services/connectors/config"
CONNECTORS_PATH = "services/connectors/config"
os.makedirs(CONNECTOR_CONFIG_PATH, exist_ok=True)  # Create directory if it doesn't exist


def save_connector_config(client_login, config_data):
    """Сохраняет конфигурацию коннектора в JSON-файл."""
    file_path = os.path.join(CONNECTOR_CONFIG_PATH, f"{client_login}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def load_connector_config(client_login):
    """Загружает конфигурацию коннектора из JSON-файла."""
    file_path = os.path.join(CONNECTOR_CONFIG_PATH, f"{client_login}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_connectors():
    """Загружает список всех доступных коннекторов."""
    connectors = []
    for filename in os.listdir(CONNECTORS_PATH):
        file_path = os.path.join(CONNECTORS_PATH, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            connectors.append({
                "name": filename.replace(".json", ""),
                "service": config.get("CONNECTOR_SERVICE", "Неизвестный сервис"),
                "type": config.get("CONNECTOR_TYPE", "unknown")  # read / write
            })
    return connectors
