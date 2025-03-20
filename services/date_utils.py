
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

def parse_dates(start_date: str, end_date: str) -> Tuple[datetime, datetime]:
    """Парсит строковые даты в datetime объекты"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return start, end

def get_periods(start_date: datetime, end_date: datetime, period_detail: str = "none") -> List[Tuple[str, str]]:
    """Разбивает период на части в зависимости от детализации"""
    if period_detail == "none":
        return [(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))]
    
    periods = []
    current = start_date
    
    while current <= end_date:
        if period_detail == "day":
            period_end = min(current + timedelta(days=1), end_date)
        elif period_detail == "week":
            period_end = min(current + timedelta(days=7), end_date)
        elif period_detail == "month":
            next_month = current.replace(day=28) + timedelta(days=4)
            period_end = min(next_month - timedelta(days=next_month.day), end_date)
            
        periods.append((
            current.strftime("%Y-%m-%d"),
            period_end.strftime("%Y-%m-%d")
        ))
        current = period_end + timedelta(days=1)
        
    return periods
