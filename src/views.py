import json
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

from logging_config import get_logger
from src.utils import read_transactions_json, read_xlsx, welcome_message, write_json

logger = get_logger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

API_KEY = os.getenv("api_key")
if not API_KEY:
    logger.error("API-ключ не установлен. Пожалуйста, установите ключ в переменной окружения 'api_key'.")
    raise ValueError("API-ключ не установлен.")


def get_utils() -> Tuple[
    Callable[[str], pd.DataFrame],
    Callable[[str], str],
    Callable[[str, Dict[str, Any]], None],
    Callable[[str], Any],
]:
    """Импортирует и возвращает функции из модуля utils."""
    from src.utils import read_xlsx, welcome_message, write_json

    return read_xlsx, welcome_message, write_json, read_transactions_json


def card_data(operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Обрабатывает данные карт из транзакций."""
    card_data = {}
    for operation in operations:
        card_number = operation.get("Номер карты")
        cashback = operation.get("Бонусы (включая кэшбэк)")
        logger.debug("Операция: %s", operation)
        if card_number:
            logger.debug("Обработка транзакции с номером карты: %s", card_number)
        else:
            logger.warning("Пропущена операция без номера карты: %s", operation)
            continue

        # Преобразование номера карты в строку
        card_number = str(card_number)
        last_digits = card_number[-4:]

        if last_digits not in card_data:
            card_data[last_digits] = {"last_digits": last_digits, "total_spent": 0.0, "cashback": 0.0}

        if operation["Сумма операции"] < 0:
            card_data[last_digits]["total_spent"] += round(operation["Сумма операции"] * -1, 1)

        if cashback is not None:
            card_data[last_digits]["cashback"] += cashback
        else:
            logger.debug("Кэшбэк отсутствует для операции: %s", operation)

    cards = list(card_data.values())
    logger.debug("Обработанные данные карт: %s", cards)
    return cards


def cashback(total_sum: int) -> int:
    """Рассчитывает кэшбэк."""
    result_cashback = total_sum // 100
    logger.info("Успешно! Результат - %s", result_cashback)
    return result_cashback


def calculate_cashback(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Рассчитывает кэшбэк для каждой карты."""
    for card in cards:
        if card["total_spent"] >= 0:
            card["cashback"] = card["total_spent"] * 0.01
            logger.info("Успешно! Результат - %s", card["cashback"])
        else:
            card["cashback"] = 0
            logger.info("Отрицательная сумма трат, кэшбэк установлен в 0")
    return cards


def filter_transactions_by_date(transactions: List[Dict[str, Any]], filter_date: datetime) -> List[Dict[str, Any]]:
    """Фильтрует транзакции по дате."""
    filtered_transactions: List[Dict[str, Any]] = []
    for transaction in transactions:
        transaction_date_str: Any = transaction.get("Дата операции")
        if transaction_date_str:
            transaction_date: datetime = datetime.strptime(transaction_date_str, "%d.%m.%Y %H:%M:%S")
            logger.debug("Сравнение дат: транзакция %s, фильтр %s", transaction_date, filter_date)
            if transaction_date < filter_date:
                filtered_transactions.append(transaction)
    logger.debug("Отфильтрованные транзакции: %s", filtered_transactions)
    return filtered_transactions


def index_page(data_time: str, sample_transactions: List[Dict[str, Any]]) -> str:
    """Обрабатывает главную страницу."""
    try:
        logger.info("Начало обработки данных для главной страницы")

        greeting: str = welcome_message("User")
        logger.debug("Приветственное сообщение: %s", greeting)

        try:
            filter_date: datetime = datetime.strptime(data_time, "%Y-%m-%d %H:%M:%S")
            filtered_transactions: List[Dict[str, Any]] = filter_transactions_by_date(sample_transactions, filter_date)
            logger.debug("Транзакции после фильтрации по дате: %s", filtered_transactions)
        except ValueError:
            logger.error("Неправильный формат даты: %s", data_time)
            return json.dumps({"error": "Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'."})

        cards: List[Dict[str, Any]] = process_card_data(filtered_transactions)
        logger.debug("Данные карт после обработки: %s", cards)

        response: Dict[str, Any] = {"greeting": greeting, "cards": cards}
        logger.info("Успешная обработка данных для главной страницы")

        return json.dumps(response, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error("Ошибка при обработке главной страницы: %s", e)
        return json.dumps({"error": "An error occurred while processing the request."})


def get_currency_rate(currency: str) -> float:
    """Возвращает текущий курс валюты."""
    try:
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}")
        response.raise_for_status()
        data = response.json()
        rate = data["rates"]["RUB"]
        logger.info("Текущий курс для %s: %s", currency, rate)
        return float(rate)
    except requests.RequestException as e:
        logger.error("Ошибка при запросе курса валют: %s", e)
        return 0.0


def get_stock_currency(stock_symbol: str) -> float:
    """Возвращает текущую цену акции."""
    try:
        stock = yf.Ticker(stock_symbol)
        history = stock.history(period="1d")
        price = history["High"].iloc[0]
        logger.info("Текущая цена акции %s: %s", stock_symbol, price)
        return float(price)  # Убедитесь, что возвращаете float
    except Exception as e:
        logger.error("Ошибка при запросе цены акции: %s", e)
        return 0.0


def process_card_data(operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Обрабатывает данные операций и возвращает список данных по картам."""
    card_data: Dict[str, Any] = {}
    for operation in operations:
        card_number = operation.get("Номер карты")
        if not card_number:
            continue

        # Преобразование номера карты в строку
        card_number = str(card_number)
        last_digits: str = card_number[-4:]

        if last_digits not in card_data:
            card_data[last_digits] = {"last_digits": last_digits, "total_spent": 0.0, "cashback": 0.0}

        if operation["Сумма операции"] < 0:
            card_data[last_digits]["total_spent"] += round(operation["Сумма операции"] * -1, 1)

        card_data[last_digits]["cashback"] += operation.get("Бонусы (включая кэшбэк)", 0.0)

    return list(card_data.values())


def total_costs(transactions: List[Dict[str, Any]]) -> float:
    """Возвращает общую сумму всех операций."""
    return float(
        sum(abs(transaction["Сумма операции"]) for transaction in transactions)
    )  # Убедитесь, что возвращаете float


def top_transactions(transactions: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """Возвращает топ-N транзакций по сумме."""
    return sorted(transactions, key=lambda x: abs(x["Сумма операции"]), reverse=True)[:n]


def main_views() -> None:
    """Основная функция для обработки транзакций."""
    user_input = input("Введите дату и время в формате YYYY-MM-DD HH:MM:SS: ")
    greeting = welcome_message(user_input if user_input else "User")  # Убедитесь, что передаете строку
    print(greeting)

    transactions_df = read_xlsx("../data/operations.xls")  # Используйте другое имя для переменной
    transactions = transactions_df.to_dict(orient="records")
    logger.debug("Прочитанные транзакции: %s", transactions)

    total_expenses = total_costs(transactions)
    logger.debug("Общие расходы: %s", total_expenses)
    print(f"Total expenses: {total_expenses}")

    cards_data = process_card_data(transactions)
    logger.debug("Данные карт: %s", cards_data)

    top_expenses = top_transactions(transactions)
    logger.debug("Топ транзакций: %s", top_expenses)
    print(f"Top transactions: {top_expenses}")

    currency_rate = None  # Инициализация переменной

    if not API_KEY:
        logger.error("API-ключ не установлен. Пожалуйста, установите ключ в переменной окружения 'api_key'.")
        print("API-ключ не установлен.")
    else:
        currency_rate = get_currency_rate("USD")
        if currency_rate is not None:
            logger.debug("Курс валюты: %s", currency_rate)
            print(f"Currency rate: {currency_rate}")
        else:
            logger.error("Не удалось получить курс валюты")
            print("Не удалось получить курс валюты")

    stock_price = get_stock_currency("AAPL")
    logger.debug("Цена акции: %s", stock_price)
    print(f"Stock price: {stock_price}")

    result = {
        "greeting": greeting,
        "total_expenses": total_expenses,
        "cards_data": cards_data,
        "top_expenses": top_expenses,
        "currency_rate": currency_rate,
        "stock_price": stock_price,
    }

    write_json("result.json", result)
    logger.debug("Результат JSON: %s", result)

    result_json = json.dumps(result, indent=2, ensure_ascii=False)
    logger.debug("Результат JSON: %s", result_json)
    print(result_json)


if __name__ == "__main__":
    main_views()
