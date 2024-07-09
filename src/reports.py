import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

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

# --- Логирование модуля reports ---
reports_logger.setLevel(logging.DEBUG)

# Добавляем обработчик к логгеру
reports_logger.addHandler(reports_file_handler)


def category_expenses_report(df: pd.DataFrame, category: str, start_date: str) -> str:
    """
    Создает отчет о расходах по категории за определенный период.

    :param df: DataFrame с транзакциями.
    :param category: Категория расходов для отчета.
    :param start_date: Дата начала отчетного периода в формате 'YYYY-MM-DD'.
    :return: JSON-строка с результатами отчета.
    """
    # Логирование запуска функции
    reports_logger.debug(
        f"Запуск функции category_expenses_report с параметрами: category={category}, start_date={start_date}"
    )

    # Парсинг даты и расчет конечной даты
    start_date_parsed: datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date: datetime = start_date_parsed + timedelta(days=90)

    # Фильтрация DataFrame
    filtered_df: pd.DataFrame = df[
        (df["category"] == category) & (df["date"] >= start_date_parsed) & (df["date"] <= end_date)
    ]

    # Расчет общих расходов
    total_expenses: int = int(filtered_df["amount"].sum())  # Преобразование в int

    # Формирование результата
    result: Dict[str, Any] = {
        "category": category,
        "total_expenses": total_expenses,
        "period": f"{start_date_parsed.date()} to {end_date.date()}",
    }

    # Логирование результата
    reports_logger.debug(f"Результат функции category_expenses_report: {result}")
    return json.dumps(result)


def weekday_expenses_report(df: pd.DataFrame, start_date: Optional[str] = None) -> str:
    """
    Функция для получения отчета о расходах по дням недели.

    :param df: DataFrame с транзакциями.
    :param start_date: Необязательная дата начала отчетного периода в формате 'YYYY-MM-DD'.
    :return: JSON-строка с результатами отчета.
    """
    reports_logger.debug(f"Запуск функции weekday_expenses_report с параметром start_date={start_date}")

    if start_date:
        start_date_parsed: datetime = datetime.strptime(start_date, "%Y-%m-%d")
        df = df[df["date"] >= start_date_parsed]

    df["weekday"] = df["date"].dt.day_name()
    expenses_by_weekday: Dict[str, int] = df.groupby("weekday")["amount"].sum().astype(int).to_dict()

    result: Dict[str, Any] = {"expenses_by_weekday": expenses_by_weekday}

    reports_logger.debug(f"Результат функции weekday_expenses_report: {result}")
    return json.dumps(result)


def weekday_vs_weekend_expenses_report(df: pd.DataFrame, start_date: str) -> str:
    """
    Функция для получения отчета о расходах в будние дни по сравнению с выходными.

    :param df: DataFrame с транзакциями.
    :param start_date: Дата начала отчетного периода в формате 'YYYY-MM-DD'.
    :return: JSON-строка с результатами отчета.
    """
    reports_logger.debug(f"Запуск функции weekday_vs_weekend_expenses_report с параметром start_date={start_date}")

    start_date_parsed: datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date: datetime = start_date_parsed + timedelta(days=90)

    filtered_df: pd.DataFrame = df[(df["date"] >= start_date_parsed) & (df["date"] <= end_date)]

    filtered_df["is_weekend"] = filtered_df["date"].dt.weekday >= 5
    weekend_expenses: int = int(filtered_df[filtered_df["is_weekend"]]["amount"].sum())
    weekday_expenses: int = int(filtered_df[~filtered_df["is_weekend"]]["amount"].sum())

    result: Dict[str, Any] = {
        "weekday_expenses": weekday_expenses,
        "weekend_expenses": weekend_expenses,
        "period": f"{start_date_parsed.date()} to {end_date.date()}",
    }

    reports_logger.debug(f"Результат функции weekday_vs_weekend_expenses_report: {result}")
    return json.dumps(result)
