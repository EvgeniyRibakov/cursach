import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from src.utils import (
    convert_to_datetime,
    dataframe_to_json,
    fetch_data_from_api,
    read_xlsx,
    welcome_message,
    write_json,
)

logger = logging.getLogger("main_logger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("main.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

#2021-12-30 19:06:39
def card_data(operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Эта функция обрабатывает данные о картах из списка транзакций.
    """
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

        if isinstance(card_number, str):  # Убираем проверку на startswith('*')
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


def index_page(data_time: str, transactions: List[Dict[str, Any]]) -> str:
    """
    Главная функция для генерации главной страницы.
    """
    logger.info("Запуск главной страницы")
    greeting = welcome_message(data_time)
    cards = card_data(transactions)
    result = {"greeting": greeting, "cards": cards}
    write_json("index_page.json", result)
    return json.dumps(result, indent=2, ensure_ascii=False)


def cashback(total_sum: int) -> int:
    """
    Возвращает весь кешбек
    """
    result_cashback = total_sum // 100
    logger.info("Успешно! Результат - %s" % result_cashback)
    return result_cashback


def main() -> None:
    """
    Главная функция для запуска всей программы.
    """
    logger.info("Запуск веб-страниц")
    transactions = read_xlsx("../data/operations.xls")
    logger.debug(f"Загруженные транзакции: {transactions}")
    user_data = input("Введите текущую дату и время в формате YYYY-MM-DD HH:MM:SS: ")
    logger.debug(f"Введенные данные: {user_data}")
    result = index_page(user_data, transactions)
    print(result)


if __name__ == "__main__":
    main()
