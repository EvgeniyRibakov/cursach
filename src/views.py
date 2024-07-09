import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Tuple


# Локальный импорт для предотвращения циклических импортов
def get_utils() -> Tuple[Callable, Callable, Callable]:
    """
    Импортирует и возвращает функции из модуля utils.

    :return: Кортеж функций (read_xlsx, welcome_message, write_json).
    """
    from src.utils import read_xlsx, welcome_message, write_json

    return read_xlsx, welcome_message, write_json


# Получение функций из utils
read_xlsx, welcome_message, write_json = get_utils()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("main.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def card_data(operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Работа с данными карты"""
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
    """Считаем кешбек"""
    result_cashback = total_sum // 100
    logger.info("Успешно! Результат - %s" % result_cashback)
    return result_cashback


def calculate_cashback(cards: list) -> list:
    """Считаем кешбек"""
    for card in cards:
        if card["total_spent"] >= 0:
            card["cashback"] = card["total_spent"] * 0.01
            logger.info("Успешно! Результат - %s" % card["cashback"])
        else:
            card["cashback"] = 0
            logger.info("Отрицательная сумма трат, кэшбэк установлен в 0")
    return cards


def filter_transactions_by_date(transactions: List[Dict], filter_date: datetime) -> List[Dict]:
    """
    Фильтрует список транзакций по дате.

    :param transactions: Список словарей, представляющих транзакции.
    :param filter_date: Дата, до которой должны быть включены транзакции.
    :return: Список отфильтрованных транзакций.
    """
    filtered_transactions: List[Dict] = []
    for transaction in transactions:
        transaction_date_str: Any | None = transaction.get("Дата операции")
        if transaction_date_str:
            transaction_date: datetime = datetime.strptime(transaction_date_str, "%d.%m.%Y %H:%M:%S")
            logger.debug(f"Сравнение дат: транзакция {transaction_date}, фильтр {filter_date}")
            if transaction_date <= filter_date:
                logger.debug(f"Добавление транзакции: {transaction}")
                filtered_transactions.append(transaction)
            else:
                logger.debug(f"Транзакция не соответствует фильтру: {transaction}")
        else:
            logger.warning(f"Отсутствует дата операции в транзакции: {transaction}")
    logger.debug(f"Отфильтрованные транзакции: {filtered_transactions}")
    return filtered_transactions


def index_page(data_time: str, transactions: List[Dict[str, Any]]) -> str:
    """главная функция  модуля, работает со всеми данными"""
    logger.info("Запуск главной страницы")
    greeting = welcome_message(data_time)
    logger.debug(f"Приветствие: {greeting}")

    # Преобразование строки с датой и временем в объект datetime
    user_datetime = datetime.strptime(data_time, "%Y-%m-%d %H:%M:%S")

    # Фильтрация транзакций по дате
    filtered_transactions = filter_transactions_by_date(transactions, user_datetime)
    logger.debug(f"Отфильтрованные транзакции: {filtered_transactions}")

    # Получение данных по картам и расчёт кэшбэка
    cards = card_data(filtered_transactions)
    cards_with_cashback = calculate_cashback(cards)
    logger.debug(f"Данные карт с кэшбэком: {cards_with_cashback}")

    # Создание результата
    result = {"greeting": greeting, "cards": cards_with_cashback}
    write_json("index_page.json", result)

    # Преобразование результата в JSON
    result_json = json.dumps(result, indent=2, ensure_ascii=False)
    logger.debug(f"Результат JSON: {result_json}")
    return result_json
