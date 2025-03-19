import os
import pandas as pd
from datetime import datetime

# Папка для хранения отчетов
REPORTS_PATH = "static/users/reports"


def save_report_to_file(df, client_login, report_name, save_format):
    """Сохраняет отчет в CSV или XLSX в папку static/users/reports/текущая_дата/"""

    # Определяем текущую дату и создаем папку
    today = datetime.today().strftime("%Y-%m-%d")
    save_dir = os.path.join(REPORTS_PATH, today)
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, f"{client_login}_{report_name}")

    if save_format == "csv":
        file_path += ".csv"
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
    elif save_format == "xlsx":
        file_path += ".xlsx"
        df.to_excel(file_path, index=False)

    return file_path  # Возвращаем путь к файлу
