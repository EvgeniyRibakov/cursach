import json
import os
from datetime import datetime
from typing import Any, Dict
from venv import logger

import pandas as pd
import requests
from dotenv import load_dotenv

from logging_config import get_logger

utils_logger = get_logger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

API_KEY = os.getenv("api_key")
if not API_KEY:
    logger.error("API-ключ не установлен. Пожалуйста, установите ключ в переменной окружения 'api_key'.")
    raise ValueError("API-ключ не установлен.")


def fetch_data_from_api(api_url: str) -> Dict[str, Any]:
    """Fetches data from the specified API URL."""
    utils_logger.debug(f"Fetching data from API: {api_url}")
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        utils_logger.debug(f"API response: {response.json()}")
        return response.json()
    except requests.RequestException as e:
        utils_logger.error(f"Error fetching data from API: {e}")
        raise


def read_transactions_json(file_path: str) -> Any:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def dataframe_to_json(dataframe: pd.DataFrame) -> str:
    """Converts DataFrame to JSON string."""
    return dataframe.to_json(orient="records")


def write_json(file_path: str, data: Dict) -> None:
    """Writes data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def read_xlsx(file_path: str) -> pd.DataFrame:
    """Reads an xlsx file into a DataFrame."""
    df = pd.read_excel(file_path)
    df.columns = [str(col) for col in df.columns]
    return df


def welcome_message(data_time: str) -> str:
    """Returns a greeting message based on the time of day."""
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
