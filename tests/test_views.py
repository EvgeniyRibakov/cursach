import json
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.views import (
    calculate_cashback,
    card_data,
    cashback,
    filter_transactions_by_date,
    get_currency_rate,
    get_stock_currency,
    index_page,
    process_card_data,
    top_transactions,
    total_costs,
)


@pytest.fixture
def sample_operations() -> list[dict[str, str | float | None]]:
    return [
        {"Номер карты": "1234", "Сумма операции": -100.0, "Бонусы (включая кэшбэк)": 1.0},
        {"Номер карты": "5678", "Сумма операции": -200.0, "Бонусы (включая кэшбэк)": 2.0},
        {"Номер карты": None, "Сумма операции": -50.0, "Бонусы (включая кэшбэк)": 0.5},
    ]


@pytest.fixture
def sample_transactions() -> list[dict[str, str | float]]:
    return [
        {"Дата операции": "01.01.2022 12:00:00", "Сумма операции": -100.0},
        {"Дата операции": "02.01.2022 12:00:00", "Сумма операции": -200.0},
        {"Дата операции": "03.01.2022 12:00:00", "Сумма операции": -300.0},
    ]


def test_card_data(sample_operations: list[dict[str, str | float | None]]) -> None:
    result: list[dict[str, str | float | None]] = card_data(sample_operations)
    assert len(result) == 2
    assert result[0]["last_digits"] == "1234"
    assert result[0]["total_spent"] == 100.0
    assert result[0]["cashback"] == 1.0


def test_cashback() -> None:
    assert cashback(150) == 1
    assert cashback(250) == 2


def test_calculate_cashback() -> None:
    cards: list[dict[str, float]] = [{"total_spent": 100.0, "cashback": 0.0}, {"total_spent": -50.0, "cashback": 0.0}]
    result: list[dict[str, float]] = calculate_cashback(cards)
    assert result[0]["cashback"] == 1.0
    assert result[1]["cashback"] == 0.0


def test_filter_transactions_by_date(sample_transactions: list[dict[str, str | float]]) -> None:
    filter_date: datetime = datetime.strptime("02.01.2022 12:00:00", "%d.%m.%Y %H:%M:%S")
    result: list[dict[str, str | float]] = filter_transactions_by_date(sample_transactions, filter_date)
    assert len(result) == 1
    assert result[0]["Дата операции"] == "01.01.2022 12:00:00"


@patch("src.views.read_xlsx")
@patch("src.views.welcome_message")
@patch("src.views.write_json")
def test_index_page(
    mock_write_json: Mock,
    mock_welcome_message: Mock,
    mock_read_xlsx: Mock,
    sample_transactions: list[dict[str, str | float]],
) -> None:
    mock_welcome_message.return_value = "Welcome!"
    mock_read_xlsx.return_value = pd.DataFrame(sample_transactions)

    data_time: str = "2022-01-02 12:00:00"
    result: str = index_page(data_time, sample_transactions)

    result_dict: dict = json.loads(result)
    assert result_dict["greeting"] == "Welcome!"
    assert len(result_dict["cards"]) == 0


@patch("src.views.requests.get")
def test_get_currency_rate(mock_get: Mock) -> None:
    mock_response: Mock = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 74.0}}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    rate: float = get_currency_rate("USD")
    assert rate == 74.0


@patch("src.views.yf.Ticker")
def test_get_stock_currency(mock_ticker: Mock) -> None:
    mock_stock: Mock = Mock()
    mock_stock.history.return_value = pd.DataFrame({"High": [150.0]})
    mock_ticker.return_value = mock_stock

    price: float = get_stock_currency("AAPL")
    assert price == 150.0


def test_process_card_data(sample_operations: list[dict[str, str | float | None]]) -> None:
    result: list[dict[str, str | float | None]] = process_card_data(sample_operations)
    assert len(result) == 2
    assert result[0]["last_digits"] == "1234"
    assert result[0]["total_spent"] == 100.0
    assert result[0]["cashback"] == 1.0
    assert result[1]["last_digits"] == "5678"
    assert result[1]["total_spent"] == 200.0
    assert result[1]["cashback"] == 2.0


def test_total_costs(sample_transactions: list[dict[str, str | float]]) -> None:
    result: float = total_costs(sample_transactions)
    assert result == 600.0


def test_top_transactions(sample_transactions: list[dict[str, str | float]]) -> None:
    result: list[dict[str, str | float]] = top_transactions(sample_transactions)
    assert len(result) == 3
    assert result[0]["Сумма операции"] == -300.0


if __name__ == "__main__":
    pytest.main()
