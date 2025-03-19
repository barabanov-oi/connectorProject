import json
import requests
import time
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


def get_direct_report(token, field_names, config, start_date, end_date):
    """
    Получает отчет из API Яндекс Директа.

    :param token: OAuth-токен API Яндекс Директа
    :param field_names: Список полей для выгрузки
    :param config: Конфигурация отчета
    :param start_date: Дата начала отчета
    :param end_date: Дата окончания отчета
    :return: DataFrame с данными
    """
    api_url = "https://api.direct.yandex.com/json/v5/reports"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "ru",
        "Content-Type": "application/json",
        "Client-Login": config.get("CLIENT_LOGIN"),
        "skipReportHeader": "true",
        "skipReportSummary": "true"
    }

    report_type = config.get("REPORT_TYPE", "CUSTOM_REPORT")
    goals_param = list(map(int, config.get("CONVERSIONS", []))) if "CONVERSIONS" in config else None

    body = {
        "params": {
            "SelectionCriteria": {
                "DateFrom": start_date,
                "DateTo": end_date
            },
            "DateRangeType": "CUSTOM_DATE",
            "FieldNames": field_names,
            "ReportName": f"Direct_Report_{start_date}_to_{end_date}_{datetime.now().strftime('%H%M%S')}",
            "ReportType": report_type,
            "Format": "TSV",
            "IncludeVAT": config.get("IncludeVAT", "NO"),
            "IncludeDiscount": config.get("IncludeDiscount", "NO"),
        }
    }

    if goals_param:
        body["params"]["Goals"] = goals_param

    while True:
        response = requests.post(api_url, headers=headers, data=json.dumps(body))

        if response.status_code == 200:
            return _process_report(response.text)
        elif response.status_code == 201:
            time.sleep(10)
        elif response.status_code in [400, 500]:
            return None
        else:
            return None


def _process_report(data):
    """Преобразует TSV-отчет в DataFrame."""
    lines = data.strip().split("\n")
    header = lines[0].split("\t")
    rows = [line.split("\t") for line in lines[1:]]
    df = pd.DataFrame(rows, columns=header)
    df.replace("--", 0, inplace=True)
    return df


def process_reports(token, field_names, config):
    """
    Запускает процесс получения отчетов по периодам.

    :param token: OAuth-токен API Яндекс Директа
    :param field_names: Список полей для выгрузки
    :param config: Конфигурация отчета
    :return: DataFrame с объединенными отчетами
    """
    periods = config.get("Periods", [])
    summary_df = pd.DataFrame()
    reports_line_count = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_period = {executor.submit(get_direct_report, token, field_names, config, start, end): (start, end)
                            for start, end in periods}

        for future in future_to_period:
            start_completed, end_completed = future_to_period[future]
            result = future.result()

            if result is not None:
                reports_line_count[f"{start_completed} - {end_completed}"] = result.shape[0]
                summary_df = pd.concat([summary_df, result], ignore_index=True)

    total_rows = sum(reports_line_count.values())
    print(f"📊 Данные успешно загружены. Итоговое количество строк: {total_rows}")

    return summary_df, reports_line_count
