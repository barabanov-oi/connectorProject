
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

REPORT_CONFIG_PATH = "services/reports/config"

def validate_report_config(config: Dict) -> tuple[bool, str]:
    """Проверяет конфигурацию отчета на корректность"""
    required_fields = ['CLIENT_LOGIN', 'REPORT_NAME', 'FIELD_NAMES', 'SAVE_TO_CONNECTOR']
    
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
            
    return True, "OK"

def format_json_config(config: Dict) -> str:
    """Форматирует JSON-конфигурацию с отступами"""
    return json.dumps(config, indent=4, ensure_ascii=False)

def load_report_config(client_login: str, report_name: str) -> Optional[Dict]:
    """Загружает конфигурацию отчета"""
    # Убираем client_login из report_name если он там уже есть
    clean_report_name = report_name.replace(f"{client_login}_", "")
    file_path = os.path.join(REPORT_CONFIG_PATH, f"{client_login}_{clean_report_name}.json")
    
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_report_config(user_id: int, client_login: str, report_name: str, config: Dict) -> tuple[bool, str]:
    """Сохраняет конфигурацию отчета"""
    is_valid, error = validate_report_config(config)
    if not is_valid:
        return False, error
        
    if not os.path.exists(REPORT_CONFIG_PATH):
        os.makedirs(REPORT_CONFIG_PATH)
        
    file_path = os.path.join(REPORT_CONFIG_PATH, f"{client_login}_{report_name}.json")
    formatted_config = format_json_config(config)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted_config)
        
    return True, "Report configuration saved successfully"

def load_all_reports(user_id: int) -> List[Dict]:
    """Загружает список всех отчетов"""
    reports = []
    
    user_reports_path = os.path.join("static/users", str(user_id), "reports")
    if not os.path.exists(user_reports_path):
        os.makedirs(user_reports_path)
        return reports
        
    for filename in os.listdir(REPORT_CONFIG_PATH):
        if filename.endswith(".json"):
            try:
                file_path = os.path.join(REPORT_CONFIG_PATH, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)
                    client = report_data.get('CLIENT_LOGIN', 'unknown')
                    display_name = report_data.get('REPORT_NAME')
                    file_name = filename.replace(".json", "")
                    
                    reports.append({
                        "display_name": display_name,
                        "file_name": file_name,
                        "client": client,
                        "date": report_data.get("START_DATE", "Не указано"),
                        "fields": report_data.get("FIELD_NAMES", [])
                    })
            except json.JSONDecodeError:
                continue
                
    return reports
