import json
import os
from datetime import datetime

LOGS_PATH = "services/reports/logs"
QUEUE_FILE = os.path.join(LOGS_PATH, "report_queue.json")

# ✅ Создаём папку logs при запуске
if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)

# ✅ Создаём пустой JSON-файл, если его нет
if not os.path.exists(QUEUE_FILE):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def format_date(date_str):
    """Форматирует дату в формат ДД-ММ-ГГГГ без времени."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    except ValueError:
        return date_str  # Если формат не подходит, возвращаем как есть

def format_datetime(datetime_str):
    """Форматирует дату и время: ДД-ММ-ГГГГ ЧЧ:ММ:СС."""
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
    except ValueError:
        return datetime_str  # Если формат не подходит, возвращаем как есть


def load_report_queue():
    """Загружает список запущенных отчётов."""
    if not os.path.exists(QUEUE_FILE):
        return []

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        try:
            reports = json.load(f)

            # ✅ Форматируем даты
            for report in reports:
                if "period" in report:
                    if report.get("period"):
                        period_parts = report["period"].split(" - ")
                    else:
                        period_parts = ["Неизвестно", "Неизвестно"]

                if "start_time" in report:
                    report["start_time"] = format_datetime(report["start_time"])

            return reports
        except json.JSONDecodeError:
            return []

def save_report_queue(queue):
    """Сохраняет список запущенных отчётов в JSON-файл."""
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

def add_report_to_queue(client_login, report_name, status="Выполняется"):
    """Добавляет новый отчет в очередь."""
    queue = load_report_queue()
    new_report = {
        "client": client_login,
        "report": report_name,
        "status": status,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": None,
        "rows": None,
        "period": None
    }
    queue.append(new_report)
    save_report_queue(queue)
    return new_report

def update_report_status(client_login, report_name, status, rows=0, period="-", result="-", reports_ids=None):
    """Обновляет статус отчёта в очереди."""
    reports = load_report_queue()

    for report in reports:
        if report["client"] == client_login and report["report"] == report_name:
            report["status"] = status
            report["rows"] = rows
            report["period"] = period
            report["result"] = result
            report["reports_ids"] = reports_ids if reports_ids else []
            break

    save_report_queue(reports)
