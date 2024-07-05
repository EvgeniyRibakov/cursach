import json
import logging
import datetime
from typing import List, Dict, Any

# --- Логирование модуля services ---
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


def beneficial_cashback_categories(year: int, month: int, transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для получения выгодных категорий повышенного кешбэка.

    :param year: Год для расчета
    :param month: Месяц для расчета
    :param transactions: Список транзакций в формате списка словарей
    :return: JSON-ответ
    """
    services_logger.debug(f"Запуск функции beneficial_cashback_categories с параметрами: year={year}, month={month}")
    # Здесь может быть логика определения выгодных категорий кешбэка
    result = {
        "year": year,
        "month": month,
        "categories": ["category1", "category2", "category3"]
    }
    services_logger.debug(f"Результат функции beneficial_cashback_categories: {result}")
    return json.dumps(result)


def invest_piggy_bank(month: int, transactions: List[Dict[str, Any]], rounding_limit: float) -> str:
    """
    Функция для сервиса «Инвесткопилка».

    :param month: Месяц для расчета
    :param transactions: Список транзакций в формате списка словарей
    :param rounding_limit: Лимит округления
    :return: JSON-ответ
    """
    services_logger.debug(
        f"Запуск функции invest_piggy_bank с параметрами: month={month}, rounding_limit={rounding_limit}")
    result = {
        "month": month,
        "rounding_limit": rounding_limit,
        "saved_amount": 1234.56
    }
    services_logger.debug(f"Результат функции invest_piggy_bank: {result}")
    return json.dumps(result)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для сервиса «Простой поиск».

    :param query: Запрос для поиска
    :param transactions: Список транзакций в формате списка словарей
    :return: JSON-ответ
    """
    services_logger.debug(f"Запуск функции simple_search с параметром: query={query}")
    filtered_transactions = [t for t in transactions if query.lower() in t.get('description', '').lower()]
    services_logger.debug(f"Результат функции simple_search: {filtered_transactions}")
    return json.dumps(filtered_transactions)


def phone_number_search(transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для сервиса «Поиск по телефонным номерам».

    :param transactions: Список транзакций в формате списка словарей
    :return: JSON-ответ
    """
    services_logger.debug("Запуск функции phone_number_search")
    import re
    phone_pattern = re.compile(r'\+?\d{10,15}')
    phone_transactions = [t for t in transactions if phone_pattern.search(t.get('description', ''))]
    services_logger.debug(f"Результат функции phone_number_search: {phone_transactions}")
    return json.dumps(phone_transactions)


def person_to_person_search(transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для сервиса «Поиск переводов физическим лицам».

    :param transactions: Список транзакций в формате списка словарей
    :return: JSON-ответ
    """
    services_logger.debug("Запуск функции person_to_person_search")
    import re
    person_pattern = re.compile(r'перевод физическому лицу', re.IGNORECASE)
    person_transactions = [t for t in transactions if person_pattern.search(t.get('description', ''))]
    services_logger.debug(f"Результат функции person_to_person_search: {person_transactions}")
    return json.dumps(person_transactions)
