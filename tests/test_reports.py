import json
import logging
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import (
    category_expenses_report,
    weekday_expenses_report,
    weekday_vs_weekend_expenses_report,
)

# Настройка логирования для тестирования
logging.basicConfig(level=logging.DEBUG)


# Фикстура для создания тестового DataFrame
@pytest.fixture
def sample_df():
    data = {
        "date": [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)],
        "category": ["food", "transport", "food"],
        "amount": [100, 50, 200],
    }
    return pd.DataFrame(data)


# Тест для функции category_expenses_report
@patch("src.reports.reports_logger")
def test_category_expenses_report(mock_logger, sample_df):
    start_date = "2020-01-01"
    category = "food"
    expected_result = {"category": category, "total_expenses": 300, "period": "2020-01-01 to 2020-03-31"}
    result = category_expenses_report(sample_df, category, start_date)
    assert json.loads(result) == expected_result
    mock_logger.debug.assert_called()


# Тест для функции weekday_expenses_report
@patch("src.reports.reports_logger")
def test_weekday_expenses_report(mock_logger, sample_df):
    start_date = "2020-01-01"
    expected_result = {"expenses_by_weekday": {"Wednesday": 100, "Thursday": 50, "Friday": 200}}
    result = weekday_expenses_report(sample_df, start_date)
    assert json.loads(result) == expected_result
    mock_logger.debug.assert_called()


# Тест для функции weekday_vs_weekend_expenses_report
@patch("src.reports.reports_logger")
def test_weekday_vs_weekend_expenses_report(mock_logger, sample_df):
    start_date = "2020-01-01"
    expected_result = {"weekday_expenses": 350, "weekend_expenses": 0, "period": "2020-01-01 to 2020-03-31"}
    result = weekday_vs_weekend_expenses_report(sample_df, start_date)
    assert json.loads(result) == expected_result
    mock_logger.debug.assert_called()
