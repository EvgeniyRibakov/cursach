from typing import Any, Dict, List
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest

from src.utils import dataframe_to_json, fetch_data_from_api, read_xlsx, welcome_message, write_json


# Фикстура для тестовых данных API
@pytest.fixture
def mock_api_response() -> List[Dict[str, Any]]:
    return [
        {"date": "2024-07-08", "amount": 100, "category": "food"},
        {"date": "2024-07-09", "amount": 150, "category": "transport"},
    ]


# Фикстура для тестовых данных DataFrame
@pytest.fixture
def test_dataframe(mock_api_response: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(mock_api_response)


# Фикстура для тестовых данных файла
@pytest.fixture
def test_file_data() -> List[Dict[str, Any]]:
    return [
        {"date": "2024-07-08", "amount": 100, "category": "food"},
        {"date": "2024-07-09", "amount": 150, "category": "transport"},
    ]


# Тест для функции fetch_data_from_api
@patch("src.utils.requests.get")
def test_fetch_data_from_api(mock_get: Mock, mock_api_response: List[Dict[str, Any]]) -> None:
    mock_get.return_value.json.return_value = mock_api_response
    mock_get.return_value.raise_for_status = Mock()
    assert fetch_data_from_api("fake_url") == mock_api_response
    mock_get.assert_called_once_with("fake_url")


# Тест для функции dataframe_to_json
def test_dataframe_to_json(test_dataframe: pd.DataFrame) -> None:
    expected_json = test_dataframe.to_json(orient="records")
    assert dataframe_to_json(test_dataframe) == expected_json


# Тест для функции write_json
@patch("builtins.open", new_callable=mock_open)
def test_write_json(mock_open: Mock, test_file_data: Dict[str, Any]) -> None:
    # Преобразование списка словарей в словарь
    data_to_write = {str(index): value for index, value in enumerate(test_file_data)}
    write_json("fake_path.json", data_to_write)
    mock_open.assert_called_once_with("fake_path.json", "w", encoding="utf-8")


# Тест для функции read_xlsx
@patch("src.utils.pd.read_excel")
def test_read_xlsx(mock_read_excel: Mock, test_file_data: List[Dict[str, Any]]) -> None:
    mock_read_excel.return_value.to_dict.return_value = test_file_data
    assert read_xlsx("fake_path.xlsx") == test_file_data
    mock_read_excel.assert_called_once_with("fake_path.xlsx")


# Параметризированный тест для функции welcome_message
@pytest.mark.parametrize(
    "input_time, expected_output",
    [
        ("2024-07-08 09:00:00", "Доброе утро!"),
        ("2024-07-08 14:00:00", "Добрый день!"),
        ("2024-07-08 19:00:00", "Добрый вечер!"),
    ],
)
def test_welcome_message(input_time: str, expected_output: str) -> None:
    assert welcome_message(input_time) == expected_output
