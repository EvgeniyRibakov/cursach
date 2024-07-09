from datetime import datetime


def convert_to_datetime(date_str: str) -> datetime:
    """Конвертирует дату на вводе в нужный формат"""
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
