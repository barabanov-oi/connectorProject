import json
import os
from datetime import datetime

REPORT_CONFIG_PATH = os.path.abspath("services/reports/config")  # Абсолютный путь

def save_report_config(client_login, report_name, config_data):
    """Сохраняет конфигурацию отчета в JSON-файл."""
    file_name = f"{report_name}.json"
    file_path = os.path.join(REPORT_CONFIG_PATH, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

def load_report_config(client_login, report_name):
    """Загружает конфигурацию отчета из JSON-файла."""
    file_name = f"{report_name}.json"
    file_path = os.path.join(REPORT_CONFIG_PATH, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_all_reports():
    """Загружает список всех отчётов из JSON-файлов."""
    reports = []
    config_path = REPORT_CONFIG_PATH # Use the correct path

    if not os.path.exists(config_path):
        os.makedirs(config_path, exist_ok=True) #Handle case where dir doesn't exist
        return reports

    for filename in os.listdir(config_path):
        if filename.endswith(".json"):
            try:
                file_path = os.path.join(config_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)
                    client = report_data.get('CLIENT_LOGIN', 'unknown')
                    name = filename.replace(".json", "").replace(f"{client}_", "")
                    reports.append({
                        "name": name,
                        "client": client,
                        "date": report_data.get("START_DATE", "Не указано"),
                        "fields": report_data.get("FIELD_NAMES", [])
                    })
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading report {filename}: {str(e)}")

    return reports