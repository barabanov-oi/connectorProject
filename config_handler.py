import json
import os
from datetime import datetime, timedelta


def load_config(config_path="report_config.json"):
    """Загружает конфигурацию из JSON-файла."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Файл конфигурации {config_path} не найден.")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_auth_blocks(config):
    """Возвращает список блоков авторизации."""
    return config


def get_reports_for_auth(config, auth_index):
    """Возвращает список отчетов для определенного авторизационного блока."""
    return config[auth_index].get("reports", [])


def get_auth_data(config, auth_index):
    """Возвращает авторизационные данные для определенного блока."""
    return config[auth_index].get("auth_data", {})


def get_date_range(date_range_type):
    """Обрабатывает диапазон дат."""
    today = datetime.today()

    date_ranges = {
        "LAST_30_DAYS": (today - timedelta(days=30), today),
        "LAST_7_DAYS": (today - timedelta(days=7), today),
        "YESTERDAY": (today - timedelta(days=1), today - timedelta(days=1))
    }

    if date_range_type in date_ranges:
        start_date, end_date = date_ranges[date_range_type]
    else:
        raise ValueError(f"❌ Неизвестный тип диапазона дат: {date_range_type}")

    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def parse_dates(start_date, end_date):
    """
    Преобразует текстовый формат даты в объекты datetime.
    Поддерживает динамические параметры (yesterday, last_14_days, last_30_days) как для start_date, так и для end_date.

    :param start_date: Строка с датой в формате "ДД-ММ-ГГГГ" или динамическое значение.
    :param end_date: Строка с датой в формате "ДД-ММ-ГГГГ" или динамическое значение.
    :return: Кортеж (start_date, end_date)
    """
    today = datetime.today()

    # Словарь с динамическими параметрами для дат
    dynamic_dates = {
        "yesterday": today - timedelta(days=1),
        "last_7_days": today - timedelta(days=7),
        "last_14_days": today - timedelta(days=14),
        "last_30_days": today - timedelta(days=30),
        "today": today
    }

    # Определяем start_date
    if start_date in dynamic_dates:
        start_date = dynamic_dates[start_date]
    else:
        try:
            start_date = datetime.strptime(start_date.strip(), "%d-%m-%Y")
        except ValueError:
            raise ValueError(f"❌ Ошибка: Неверный формат start_date '{start_date}'. Используйте 'ДД-ММ-ГГГГ' или динамическое значение.")

    # Определяем end_date
    if end_date in dynamic_dates:
        end_date = dynamic_dates[end_date]
    else:
        try:
            end_date = datetime.strptime(end_date.strip(), "%d-%m-%Y")
        except ValueError:
            raise ValueError(f"❌ Ошибка: Неверный формат end_date '{end_date}'. Используйте 'ДД-ММ-ГГГГ' или динамическое значение.")

    # Проверяем, чтобы start_date не был больше end_date
    if start_date > end_date:
        raise ValueError(f"❌ Ошибка: start_date ({start_date.strftime('%d-%m-%Y')}) не может быть позже end_date ({end_date.strftime('%d-%m-%Y')}).")

    return start_date, end_date


def get_periods(start_date, end_date, detail):
    """
    Генерирует список периодов в зависимости от детализации (weekly, monthly, none).

    :param start_date: datetime, начало периода
    :param end_date: datetime, конец периода
    :param detail: строка, уровень детализации (none, weekly, monthly)
    :return: список кортежей (start_date, end_date) в строковом формате YYYY-MM-DD
    """
    periods = []
    current_date = start_date

    if detail == "none":
        periods.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    elif detail == "monthly":
        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            next_month = month_start + timedelta(days=32)
            month_end = (next_month.replace(day=1) - timedelta(days=1))

            if month_end > end_date:
                month_end = end_date

            periods.append((month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')))
            current_date = month_end + timedelta(days=1)
    elif detail == "weekly":
        while current_date <= end_date:
            week_start = current_date
            week_end = current_date + timedelta(days=6)

            if week_end > end_date:
                week_end = end_date

            periods.append((week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))
            current_date = week_end + timedelta(days=1)

    return periods
