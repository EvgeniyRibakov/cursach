import json
import logging
from datetime import datetime
from typing import Any, Dict, List, cast

import pandas as pd
import requests

utils_logger = logging.getLogger("utils")
utils_logger.setLevel(logging.DEBUG)

utils_file_handler = logging.FileHandler("utils.log")
utils_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
utils_file_handler.setFormatter(utils_formatter)
utils_logger.addHandler(utils_file_handler)


def fetch_data_from_api(api_url: str) -> List[Dict[str, Any]]:
    """Обращение к api"""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return cast(List[Dict[str, Any]], data)
    except requests.RequestException as e:
        utils_logger.error(f"Ошибка при обращении к API: {e}")
        raise


def dataframe_to_json(dataframe: pd.DataFrame) -> str:
    """перевод данных в json"""
    return dataframe.to_json(orient="records")


def write_json(file_path: str, data: dict) -> None:
    """запись в json файл"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def read_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """Чтение хlsx файла"""
    df = pd.read_excel(file_path)
    transactions = df.to_dict(orient="records")
    transactions_str_keys = [{str(k): v for k, v in transaction.items()} for transaction in transactions]

    utils_logger.debug(f"Транзакции, считанные из файла {file_path}: {transactions_str_keys}")

    return transactions_str_keys


def welcome_message(data_time: str) -> str:
    """Вывод приветствия в зависимости от времени"""
    data_time = data_time.strip()
    current_time = datetime.strptime(data_time, "%Y-%m-%d %H:%M:%S").time()

    if current_time < datetime.strptime("06:00:00", "%H:%M:%S").time():
        return "Доброй ночи!"
    elif current_time < datetime.strptime("12:00:00", "%H:%M:%S").time():
        return "Доброе утро!"
    elif current_time < datetime.strptime("18:00:00", "%H:%M:%S").time():
        return "Добрый день!"
    else:
        return "Добрый вечер!"
