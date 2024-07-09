import json
from typing import Any, Dict, List

import pytest

from src.services import (beneficial_cashback_categories, invest_piggy_bank, person_to_person_search,
                          phone_number_search)


# Фикстура для имитации списка транзакций
@pytest.fixture
def mock_transactions() -> List[Dict[str, Any]]:
    return [
        {"description": "Оплата услуг +79991234567", "amount": 1500},
        {"description": "Перевод физическому лицу", "amount": 3000},
        {"description": "Покупка в магазине", "amount": 500},
    ]


# Тесты для проверки отсутствия ложных срабатываний
def test_no_false_positives_phone_search(mock_transactions: List[Dict[str, Any]]) -> None:
    mock_transactions.append({"description": "Оплата услуг 123456", "amount": 100})
    result = phone_number_search(mock_transactions)
    assert len(json.loads(result)) == 1, "Функция не должна включать транзакции без полноценных номеров телефонов"


def test_no_false_positives_person_search(mock_transactions: List[Dict[str, Any]]) -> None:
    mock_transactions.append({"description": "Перевод на счет физлица", "amount": 200})
    result = person_to_person_search(mock_transactions)
    assert (
        len(json.loads(result)) == 1
    ), "Функция не должна включать транзакции, не соответствующие точному шаблону поиска"


# Тест для функции beneficial_cashback_categories
def test_beneficial_cashback_categories(mock_transactions: List[Dict[str, Any]]) -> None:
    year = 2024
    month = 7
    result = beneficial_cashback_categories(year, month, mock_transactions)
    assert json.loads(result) == {"year": year, "month": month, "categories": ["category1", "category2", "category3"]}


# Тест для функции invest_piggy_bank
def test_invest_piggy_bank(mock_transactions: List[Dict[str, Any]]) -> None:
    month = 7
    rounding_limit = 10.0
    result = invest_piggy_bank(month, mock_transactions, rounding_limit)
    assert json.loads(result) == {"month": month, "rounding_limit": rounding_limit, "saved_amount": 1234.56}
