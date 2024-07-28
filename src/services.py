import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from src.views import logger, read_xlsx

# Логирование модуля services
services_logger = logging.getLogger("services")
services_logger.setLevel(logging.DEBUG)

# Создаем обработчик для записи логов в файл
services_file_handler = logging.FileHandler("services.log")

# Создаем форматтер для логов
services_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Устанавливаем форматтер для обработчика
services_file_handler.setFormatter(services_formatter)

# Добавляем обработчик к логгеру
services_logger.addHandler(services_file_handler)


def get_transactions(
    search_term: str, file_path: str = "../data/operations.xls", output_file: str = "transactions_search_result.json"
) -> str:
    """
    Возвращает JSON-ответ со всеми транзакциями, содержащими search_term
    в описании или категории.

    Args:
        search_term: Строка для поиска.
        file_path: Путь к файлу Excel с данными транзакций.
        output_file: Путь к выходному файлу JSON с результатами поиска.

    Returns:
        JSON-строка с результатами поиска.
    """
    logger.info(f"Поиск транзакций по ключевому слову: {search_term}")
    try:
        data = pd.read_excel(file_path)

        data["Описание"] = data["Описание"].astype(str)
        data["Категория"] = data["Категория"].astype(str)

        filtered_data = data[
            data["Описание"].str.contains(search_term, case=False)
            | data["Категория"].str.contains(search_term, case=False)
        ]

        transaction_list = filtered_data.to_dict(orient="records")

        if not transaction_list:
            transaction_list = [{"message": "Слово не найдено ни в одной категории"}]

        json_response = json.dumps(transaction_list, indent=4, ensure_ascii=False)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_response)

        logger.info(f"Результаты поиска записаны в файл {output_file}")
        return json_response

    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден.")
        return json.dumps({"error": f"Файл {file_path} не найден."}, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        return json.dumps({"error": f"Произошла ошибка: {str(e)}"}, indent=4, ensure_ascii=False)


def beneficial_cashback_categories(year: int, month: int, transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для получения выгодных категорий повышенного кешбэка.

    Args:
        year: Год для расчета.
        month: Месяц для расчета.
        transactions: Список транзакций в формате списка словарей.

    Returns:
        JSON-ответ с выгодными категориями.
    """
    services_logger.debug(f"Запуск функции beneficial_cashback_categories с параметрами: year={year}, month={month}")
    result = {"year": year, "month": month, "categories": ["category1", "category2", "category3"]}
    services_logger.debug(f"Результат функции beneficial_cashback_categories: {result}")
    return json.dumps(result)


def invest_piggy_bank(month: int, transactions: List[Dict[str, Any]], rounding_limit: float) -> str:
    """
    Функция для сервиса «Инвесткопилка».

    Args:
        month: Месяц для расчета.
        transactions: Список транзакций в формате списка словарей.
        rounding_limit: Лимит округления.

    Returns:
        JSON-ответ с результатами расчета.
    """
    services_logger.debug(
        f"Запуск функции invest_piggy_bank с параметрами: month={month}, rounding_limit={rounding_limit}"
    )
    result = {"month": month, "rounding_limit": rounding_limit, "saved_amount": 1234.56}
    services_logger.debug(f"Результат функции invest_piggy_bank: {result}")
    return json.dumps(result)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для сервиса «Простой поиск».

    Args:
        query: Запрос для поиска.
        transactions: Список транзакций в формате списка словарей.

    Returns:
        JSON-ответ с отфильтрованными транзакциями.
    """
    services_logger.debug(f"Запуск функции simple_search с параметром: query={query}")
    filtered_transactions = [t for t in transactions if query.lower() in t.get("Описание", "").lower()]
    services_logger.debug(f"Результат функции simple_search: {filtered_transactions}")
    return json.dumps(filtered_transactions)


def phone_number_search(transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для сервиса «Поиск по телефонным номерам».

    Args:
        transactions: Список транзакций в формате списка словарей.

    Returns:
        JSON-ответ с транзакциями, содержащими телефонные номера.
    """
    services_logger.debug("Запуск функции phone_number_search")
    phone_pattern = re.compile(r"\+?\d{11,15}")
    phone_transactions = [t for t in transactions if phone_pattern.search(t.get("description", ""))]
    services_logger.debug(f"Результат функции phone_number_search: {phone_transactions}")
    return json.dumps(phone_transactions)


def person_to_person_search(transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для сервиса «Поиск переводов физическим лицам».

    Args:
        transactions: Список транзакций в формате списка словарей.

    Returns:
        JSON-ответ с транзакциями, содержащими переводы физическим лицам.
    """
    services_logger.debug("Запуск функции person_to_person_search")
    person_pattern = re.compile(r"\bперевод физическому лицу\b", re.IGNORECASE)
    person_transactions = [t for t in transactions if person_pattern.search(t.get("description", ""))]
    services_logger.debug(f"Результат функции person_to_person_search: {person_transactions}")
    return json.dumps(person_transactions)


def get_expenses(transactions: pd.DataFrame, category: str, report_date: Optional[str] = None) -> str:
    """
    Вычисляет траты по категории за последние 3 месяца от указанной даты.

    Args:
        transactions: DataFrame с транзакциями.
        category: Категория для расчета.
        report_date: Дата, от которой отсчитывать 3 месяца.

    Returns:
        JSON-строка с результатами расчета.
    """
    report_date_dt = datetime.strptime(report_date, "%Y-%m-%d") if report_date else datetime.now()

    # Преобразуем столбец с датой к типу datetime
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")

    # Приведем категории к нижнему регистру и уберем пробелы по краям
    transactions["Категория"] = transactions["Категория"].astype(str).str.strip().str.lower()
    category = str(category).strip().lower()

    logger.info(
        f"Расчет трат по категории: {category} за период {report_date_dt - pd.DateOffset(months=3)}--{report_date_dt}"
    )

    # Отфильтруем транзакции по категории и дате
    filtered_transactions = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата платежа"] >= report_date_dt - pd.DateOffset(months=3))
        & (transactions["Дата платежа"] <= report_date_dt)
    ]

    # Выводим отфильтрованные транзакции для отладки
    logger.debug(f"Отфильтрованные транзакции: {filtered_transactions}")

    # Проверим количество отфильтрованных транзакций
    if filtered_transactions.empty:
        logger.warning(f"Не найдено транзакций по категории '{category}' за указанный период.")
    else:
        logger.info(f"Найдено {len(filtered_transactions)} транзакций по категории '{category}' за указанный период.")

    # Вычислим общую сумму трат по отфильтрованным транзакциям
    total_expenses = filtered_transactions["Сумма платежа"].sum()

    # Преобразуем total_expenses к типу int
    total_expenses = int(total_expenses)

    result = json.dumps(
        {"category": category, "total_expenses": total_expenses, "report_date": str(report_date_dt.date())},
        indent=4,
        ensure_ascii=False,
    )
    logger.info(f"Результаты расчета: {result}")
    return result


def main_services() -> None:
    """
    Основная функция модуля, которая объединяет взаимодействие пользователя и функций.
    """
    print("Введите слово для поиска. Например: Такси")
    search_term = input().strip()
    json_result = get_transactions(search_term)
    print(json_result)

    transactions_df = read_xlsx("../data/operations.xls")

    print("Введите слово для поиска. Например: Супермаркет")
    category_to_check = input().strip()
    print("Введите дату для поиска. Например: 2021-12-31")
    report_date_to_check = input().strip()
    json_expenses_result = get_expenses(transactions_df, category_to_check, report_date_to_check)
    print(json_expenses_result)


if __name__ == "__main__":
    main_services()
