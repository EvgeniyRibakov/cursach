import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd

from src.views import logger, read_xlsx

# --- Логирование модуля reports ---
reports_logger = logging.getLogger("reports")
reports_logger.setLevel(logging.DEBUG)

# Создаем обработчик для записи логов в файл
reports_file_handler = logging.FileHandler("reports.log")

# Создаем форматтер для логов
reports_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levellevel)s - %(message)s")

# Устанавливаем форматтер для обработчика
reports_file_handler.setFormatter(reports_formatter)

# Добавляем обработчик к логгеру
reports_logger.addHandler(reports_file_handler)


def category_expenses_report(df: pd.DataFrame, category: str, start_date: str) -> str:
    reports_logger.debug(
        f"Запуск функции category_expenses_report с параметрами: category={category}, start_date={start_date}"
    )

    start_date_parsed: datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date: datetime = start_date_parsed + timedelta(days=90)

    # Проверка наличия необходимых столбцов
    if not {"Категория", "Дата платежа", "Сумма операции"}.issubset(df.columns):
        raise KeyError("DataFrame должен содержать столбцы 'Категория', 'Дата платежа', 'Сумма операции'")

    filtered_df: pd.DataFrame = df[
        (df["Категория"] == category) & (df["Дата платежа"] >= start_date_parsed) & (df["Дата платежа"] <= end_date)
    ]

    total_expenses: int = int(filtered_df["Сумма операции"].sum())

    result: Dict[str, Any] = {
        "category": category,
        "total_expenses": total_expenses,
        "period": f"{start_date_parsed.date()} to {end_date.date()}",
    }

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
        df = df[df["Дата платежа"] >= start_date_parsed]

    df["weekday"] = df["Дата платежа"].dt.day_name()
    expenses_by_weekday: Dict[str, int] = df.groupby("weekday")["Сумма операции"].sum().astype(int).to_dict()

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

    filtered_df: pd.DataFrame = df[(df["Дата платежа"] >= start_date_parsed) & (df["Дата платежа"] <= end_date)]

    filtered_df["is_weekend"] = filtered_df["Дата платежа"].dt.weekday >= 5
    weekend_expenses: int = int(filtered_df[filtered_df["is_weekend"]]["Сумма операции"].sum())
    weekday_expenses: int = int(filtered_df[~filtered_df["is_weekend"]]["Сумма операции"].sum())

    result: Dict[str, Any] = {
        "weekday_expenses": weekday_expenses,
        "weekend_expenses": weekend_expenses,
        "period": f"{start_date_parsed.date()} to {end_date.date()}",
    }

    reports_logger.debug(f"Результат функции weekday_vs_weekend_expenses_report: {result}")
    return json.dumps(result)


def filter_transactions(transactions: pd.DataFrame, category: str, start_date: str) -> Any:
    """
    Фильтрация транзакций по категории и дате.

    Args:
        transactions: DataFrame с транзакциями.
        category: Категория для фильтрации.
        start_date: Дата начала 3-месячного периода в формате 'DD.MM.YYYY'.

    Returns:
        Список словарей с транзакциями, соответствующими запросу.
    """
    # Преобразование столбца "Дата платежа" в тип datetime
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")

    start_date_parsed = datetime.strptime(start_date, "%d.%m.%Y")
    end_date = start_date_parsed + timedelta(days=90)

    filtered_transactions = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата платежа"] >= start_date_parsed)
        & (transactions["Дата платежа"] < end_date)
    ]

    # Использование .loc для изменения значений в DataFrame
    filtered_transactions.loc[:, "Дата платежа"] = filtered_transactions["Дата платежа"].dt.strftime("%d.%m.%Y")

    # Преобразование объектов Timestamp в строки
    filtered_transactions = filtered_transactions.astype(str)

    return filtered_transactions.to_dict("records")


def main_reports() -> None:
    """
    Главная функция модуля.
    """
    operations = read_xlsx("../data/operations.xls")
    category = input("Введите категорию трат: ")
    start_date = input("Введите дату начала 3-месячного периода (DD.MM.YYYY): ")

    filtered_operations = filter_transactions(operations, category, start_date)

    with open("filtered_operations.json", "w", encoding="utf-8") as f:
        json.dump(filtered_operations, f, indent=4, ensure_ascii=False)

    logger.info("Отфильтрованные операции записаны в файл filtered_operations.json")
    print("Отфильтрованные операции записаны в файл filtered_operations.json")


if __name__ == "__main__":
    main_reports()
