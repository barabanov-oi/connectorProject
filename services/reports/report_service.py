import json
import os

REPORT_CONFIG_PATH = os.path.abspath("services/reports/config")  # Абсолютный путь
REPORTS_DIR = "services\\reports\\config"

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
        raise FileNotFoundError(f"Файл {file_path} не найден.")  # ✅ Теперь путь корректный

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_all_reports():
    """Загружает список всех отчётов из JSON-файлов."""
    reports = []

    if os.path.exists(REPORTS_DIR):
        for filename in os.listdir(REPORTS_DIR):
            if filename.endswith(".json"):  # Загружаем только JSON
                with open(os.path.join(REPORTS_DIR, filename), "r", encoding="utf-8") as f:
                    report_data = json.load(f)
                    reports.append({
                        "name": filename.replace(".json", ""),
                        "client": report_data.get("CLIENT_LOGIN"),
                        "date": report_data.get("START_DATE", "Не указано"),
                        "fields": report_data.get("FIELD_NAMES", [])
                    })
    return reports
