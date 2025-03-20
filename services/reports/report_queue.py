
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

QUEUE_FILE = "services/reports/queue/reports_queue.json"

class ReportStatus:
    PENDING = "В очереди"
    RUNNING = "Выполняется"
    COMPLETED = "Завершен"
    ERROR = "Ошибка"

def format_datetime(dt: str) -> str:
    try:
        return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
    except ValueError:
        return dt

def load_report_queue(user_id: int) -> List[Dict]:
    """Загружает очередь отчетов пользователя"""
    if not os.path.exists(QUEUE_FILE):
        return []
        
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        try:
            all_reports = json.load(f)
            # Фильтруем отчеты по user_id
            user_reports = [r for r in all_reports if r.get('user_id') == user_id]
            
            for report in user_reports:
                if "start_time" in report:
                    report["start_time"] = format_datetime(report["start_time"])
                    
            return user_reports
        except json.JSONDecodeError:
            return []

def save_report_queue(queue: List[Dict]):
    """Сохраняет очередь отчетов"""
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

def add_report_to_queue(user_id: int, client_login: str, report_name: str) -> None:
    """Добавляет отчет в очередь"""
    queue = load_report_queue(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_report = {
        "user_id": user_id,
        "client": client_login,
        "report": report_name,
        "status": ReportStatus.PENDING,
        "start_time": now,
        "end_time": None,
        "rows_count": 0,
        "period": None,
        "result_link": None
    }
    
    queue.append(new_report)
    save_report_queue(queue)

def update_report_status(user_id: int, client_login: str, report_name: str, 
                        status: str, rows_count: int = 0, 
                        period: str = None, result_link: str = None) -> None:
    """Обновляет статус отчета в очереди"""
    queue = load_report_queue(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for report in queue:
        if (report["client"] == client_login and 
            report["report"] == report_name and 
            report["user_id"] == user_id):
            
            report["status"] = status
            report["end_time"] = now
            report["rows_count"] = rows_count
            report["period"] = period
            report["result_link"] = result_link
            
    save_report_queue(queue)
