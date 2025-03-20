import json
import os
from typing import Dict, List, Optional
from datetime import datetime

def get_user_reports_path(user_id):
    """Возвращает путь к папке с отчетами пользователя"""
    return os.path.join("static/users", str(user_id), "reports")

def validate_report_config(config: Dict) -> tuple[bool, str]:
    """Проверяет конфигурацию отчета на корректность"""
    required_fields = ['REPORT_NAME', 'FIELD_NAMES', 'SAVE_TO_CONNECTOR']

    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"

    return True, "OK"

def load_report_config(user_id: int, report_name: str) -> Optional[Dict]:
    """Загружает конфигурацию отчета"""
    config_path = get_user_reports_path(user_id)
    file_path = os.path.join(config_path, f"{report_name}.json")

    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_report_config(user_id: int, report_name: str, config: Dict) -> tuple[bool, str]:
    """Сохраняет конфигурацию отчета"""
    is_valid, error = validate_report_config(config)
    if not is_valid:
        return False, error

    config_path = get_user_reports_path(user_id)
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    file_path = os.path.join(config_path, f"{report_name}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    return True, "OK"

def load_all_reports(user_id: int) -> List[Dict]:
    """Загружает все отчеты пользователя"""
    reports = []
    reports_path = get_user_reports_path(user_id)

    if not os.path.exists(reports_path):
        return reports

    for filename in os.listdir(reports_path):
        if filename.endswith('.json'):
            report_name = filename.replace('.json', '')
            report_config = load_report_config(user_id, report_name)
            if report_config:
                reports.append({
                    'name': report_name,
                    'config': report_config
                })

    return reports