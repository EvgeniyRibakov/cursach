import json
import logging
from datetime import datetime, timedelta

import pandas as pd

# --- Логирование модуля reports ---
reports_logger = logging.getLogger("reports")
reports_logger.setLevel(logging.DEBUG)

# Создаем обработчик для записи логов в файл
reports_file_handler = logging.FileHandler("reports.log")

# Создаем форматтер для логов
reports_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Устанавливаем форматтер для обработчика
reports_file_handler.setFormatter(reports_formatter)

# Добавляем обработчик к логгеру
reports_logger.addHandler(reports_file_handler)


def category_expenses_report(df: pd.DataFrame, category: str, start_date: str) -> str:
    reports_logger.debug(
        f"Запуск функции category_expenses_report с параметрами: category={category}, start_date={start_date}"
    )

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = start_date + timedelta(days=90)

    filtered_df = df[(df["category"] == category) & (df["date"] >= start_date) & (df["date"] <= end_date)]

    total_expenses = filtered_df["amount"].sum().item()  # Используйте .item() для преобразования в int
    result = {
        "category": category,
        "total_expenses": total_expenses,
        "period": f"{start_date.date()} to {end_date.date()}",
    }

    reports_logger.debug(f"Результат функции category_expenses_report: {result}")
    return json.dumps(result)


def weekday_expenses_report(df: pd.DataFrame, start_date: str = None) -> str:
    """
    Функция для получения отчета «Траты по дням недели».

    :param df: DataFrame с транзакциями
    :param start_date: Дата отсчета в формате 'YYYY-MM-DD', по умолчанию None
    :return: JSON-ответ
    """
    reports_logger.debug(f"Запуск функции weekday_expenses_report с параметром start_date={start_date}")

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        df = df[df["date"] >= start_date]

    df["weekday"] = df["date"].dt.day_name()
    expenses_by_weekday = df.groupby("weekday")["amount"].sum().to_dict()

    result = {"expenses_by_weekday": expenses_by_weekday}

    reports_logger.debug(f"Результат функции weekday_expenses_report: {result}")
    return json.dumps(result)


def weekday_vs_weekend_expenses_report(df: pd.DataFrame, start_date: str) -> str:
    reports_logger.debug(f"Запуск функции weekday_vs_weekend_expenses_report с параметром start_date={start_date}")

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = start_date + timedelta(days=90)

    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    filtered_df["is_weekend"] = filtered_df["date"].dt.weekday >= 5
    weekend_expenses = (
        filtered_df[filtered_df["is_weekend"]]["amount"].sum().item()
    )  # Используйте .item() для преобразования в int
    weekday_expenses = (
        filtered_df[~filtered_df["is_weekend"]]["amount"].sum().item()
    )  # Используйте .item() для преобразования в int

    result = {
        "weekday_expenses": weekday_expenses,
        "weekend_expenses": weekend_expenses,
        "period": f"{start_date.date()} to {end_date.date()}",
    }

    reports_logger.debug(f"Результат функции weekday_vs_weekend_expenses_report: {result}")
    return json.dumps(result)
