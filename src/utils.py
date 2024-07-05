import json
import pandas as pd
import requests
import logging
from datetime import datetime
from typing import Any, Dict, List

utils_logger = logging.getLogger("utils")
utils_logger.setLevel(logging.DEBUG)

# Создаем обработчик для записи логов в файл
utils_file_handler = logging.FileHandler("utils.log")

# Создаем форматтер для логов
utils_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Устанавливаем форматтер для обработчика
utils_file_handler.setFormatter(utils_formatter)

# Добавляем обработчик к логгеру
utils_logger.addHandler(utils_file_handler)


def fetch_data_from_api(api_url: str) -> List[Dict[str, Any]]:
    """Функция для получения данных из API."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        utils_logger.error(f"Ошибка при обращении к API: {e}")
        raise


def convert_to_datetime(date_str: str) -> datetime:
    """Преобразует строку даты в объект datetime."""
    return datetime.fromisoformat(date_str)


def dataframe_to_json(dataframe: pd.DataFrame) -> str:
    """Преобразует DataFrame в JSON строку."""
    return dataframe.to_json(orient="records")


def write_json(file_path: str, data: dict) -> None:
    """Записывает данные в json файл"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def read_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает данные о транзакциях из Excel файла.
    """
    transactions = pd.read_excel(file_path)
    utils_logger.debug(f"Данные из Excel файла: {transactions.head()}")
    return transactions.to_dict("records")


def welcome_message(data_time: str) -> str:
    """Формирование приветственного сообщения на основе текущего времени"""
    data_time = data_time.strip()
    current_time = datetime.strptime(data_time, "%Y-%m-%d %H:%M:%S").time()
    if current_time < datetime.strptime("12:00:00", "%H:%M:%S").time():
        return "Доброе утро!"
    elif current_time < datetime.strptime("18:00:00", "%H:%M:%S").time():
        return "Добрый день!"
    else:
        return "Добрый вечер!"
