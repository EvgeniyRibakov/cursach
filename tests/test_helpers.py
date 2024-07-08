from datetime import datetime

import pytest

from src.helpers import convert_to_datetime


def test_convert_to_datetime_valid():
    # Проверка корректной конвертации строки в datetime
    date_str = "2024-07-08 19:43:17"
    expected_result = datetime(2024, 7, 8, 19, 43, 17)
    assert convert_to_datetime(date_str) == expected_result


def test_convert_to_datetime_invalid():
    # Проверка обработки некорректного формата строки
    date_str = "08-07-2024 19:43:17"
    with pytest.raises(ValueError):
        convert_to_datetime(date_str)


def test_convert_to_datetime_empty():
    # Проверка обработки пустой строки
    date_str = ""
    with pytest.raises(ValueError):
        convert_to_datetime(date_str)


def test_convert_to_datetime_none():
    # Проверка обработки None в качестве входных данных
    date_str = None
    with pytest.raises(TypeError):
        convert_to_datetime(date_str)
