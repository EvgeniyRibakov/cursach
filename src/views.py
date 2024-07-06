import logging
import json
from src.helpers import convert_to_datetime
from typing import Any, Dict, List
import pandas as pd
from datetime import datetime


# Локальный импорт для предотвращения циклических импортов
def get_utils():
    from src.utils import (
        read_xlsx,
        welcome_message,
        write_json,
    )
    return read_xlsx, welcome_message, write_json


read_xlsx, welcome_message, write_json = get_utils()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("main.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def card_data(operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    card_data = {}

    for operation in operations:
        card_number = operation.get("Номер карты")
        cashback = operation.get("Бонусы (включая кэшбэк)")
        logger.debug(f"Операция: {operation}")
        if card_number:
            logger.debug(f"Обработка транзакции с номером карты: {card_number}")
        else:
            logger.warning(f"Пропущена операция без номера карты: {operation}")
            continue

        if isinstance(card_number, str):
            last_digits = card_number[-4:]
            if last_digits not in card_data:
                card_data[last_digits] = {"last_digits": last_digits, "total_spent": 0.0, "cashback": 0.0}
            if operation["Сумма операции"] < 0:
                card_data[last_digits]["total_spent"] += round(operation["Сумма операции"] * -1, 1)
            if cashback is not None:
                card_data[last_digits]["cashback"] += cashback
            else:
                logger.debug(f"Кэшбэк отсутствует для операции: {operation}")
        else:
            logger.warning(f"Неверный формат номера карты: {card_number}")

    cards = list(card_data.values())
    logger.debug(f"Обработанные данные карт: {cards}")
    return cards


def cashback(total_sum: int) -> int:
    result_cashback = total_sum // 100
    logger.info("Успешно! Результат - %s" % result_cashback)
    return result_cashback


def filter_transactions_by_date(transactions, date_str):
    # Преобразование строки даты в объект datetime
    filter_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    # Фильтрация транзакций по дате
    filtered_transactions = []
    for transaction in transactions:
        # Преобразование даты операции в объект datetime
        transaction_date_str = transaction.get("Дата операции")
        if transaction_date_str:
            transaction_date = datetime.strptime(transaction_date_str, "%d.%m.%Y %H:%M:%S")
            if transaction_date <= filter_date:
                filtered_transactions.append(transaction)
    return filtered_transactions


def index_page(data_time: str, transactions: List[Dict[str, Any]]) -> str:
    logger.info("Запуск главной страницы")
    greeting = welcome_message(data_time)
    filtered_transactions = filter_transactions_by_date(transactions, data_time)
    cards = card_data(filtered_transactions)
    result = {"greeting": greeting, "cards": cards}
    write_json("index_page.json", result)
    return json.dumps(result, indent=2, ensure_ascii=False)


def main() -> None:
    logger.info("Запуск веб-страниц")
    transactions = read_xlsx("../data/operations.xls")
    logger.debug(f"Загруженные транзакции: {transactions}")

    user_data = input("Введите текущую дату и время в формате YYYY-MM-DD HH:MM:SS: ")
    logger.debug(f"Введенные данные: {user_data}")
    result = index_page(user_data, transactions)
    print(result)


if __name__ == "__main__":
    main()
