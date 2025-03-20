import json
import os
from datetime import datetime
from enum import Enum

class ReportStatus(Enum):
    PENDING = "Выполняется"
    COMPLETED = "Готово"
    ERROR = "Ошибка"

QUEUE_FILE = "static/reports_queue.json"

def load_report_queue():
    """Загружает очередь отчетов"""
    if not os.path.exists(QUEUE_FILE):
        return []

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_report_queue(queue):
    """Сохраняет очередь отчетов"""
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

def add_report_to_queue(user_id: int, report_name: str) -> None:
    """Добавляет отчет в очередь"""
    queue = load_report_queue()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_report = {
        "user_id": user_id,
        "report": report_name,
        "status": ReportStatus.PENDING.value,
        "start_time": now,
        "end_time": None,
        "rows_count": 0,
        "period": None,
        "result_link": None
    }

    queue.append(new_report)
    save_report_queue(queue)

def update_report_status(user_id: int, report_name: str, 
                        status: str, rows_count: int = 0, 
                        period: str = None, result_link: str = None) -> None:
    """Обновляет статус отчета в очереди"""
    queue = load_report_queue()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for report in queue:
        if (report["report"] == report_name and 
            report["user_id"] == user_id):

            report["status"] = status
            report["end_time"] = now
            report["rows_count"] = rows_count
            report["period"] = period
            report["result_link"] = result_link
            break

    save_report_queue(queue)