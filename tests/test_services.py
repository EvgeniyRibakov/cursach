import json

import pytest

from src.services import (
    beneficial_cashback_categories,
    invest_piggy_bank,
    person_to_person_search,
    phone_number_search,
    simple_search,
)


# Фикстура для имитации списка транзакций
@pytest.fixture
def mock_transactions():
    return [
        {"description": "Оплата услуг +79991234567", "amount": 1500},
        {"description": "Перевод физическому лицу", "amount": 3000},
        {"description": "Покупка в магазине", "amount": 500},
        # Добавьте больше транзакций для тестирования различных сценариев
    ]


# Тест для функции phone_number_search
def test_phone_number_search(mock_transactions):
    result = phone_number_search(mock_transactions)
    assert json.loads(result) == [{"description": "Оплата услуг +79991234567", "amount": 1500}], \
        "Функция должна вернуть транзакции с номерами телефонов"


# Тест для функции person_to_person_search
def test_person_to_person_search(mock_transactions):
    result = person_to_person_search(mock_transactions)
    assert json.loads(result) == [{"description": "Перевод физическому лицу", "amount": 3000}], \
        "Функция должна вернуть транзакции с переводами физическим лицам"


# Тесты для проверки отсутствия ложных срабатываний
def test_no_false_positives_phone_search(mock_transactions):
    mock_transactions.append({"description": "Оплата услуг 123456", "amount": 100})
    result = phone_number_search(mock_transactions)
    assert len(json.loads(result)) == 1, \
        "Функция не должна включать транзакции без полноценных номеров телефонов"


def test_no_false_positives_person_search(mock_transactions):
    mock_transactions.append({"description": "Перевод на счет физлица", "amount": 200})
    result = person_to_person_search(mock_transactions)
    assert len(json.loads(result)) == 1, \
        "Функция не должна включать транзакции, не соответствующие точному шаблону поиска"


# Фикстура для тестовых данных транзакций
@pytest.fixture
def mock_transactions():
    return [
        {"date": "2024-07-08", "amount": 100, "category": "food", "description": "покупка в магазине"},
        {"date": "2024-07-09", "amount": 150, "category": "transport", "description": "+1234567890 такси"},
        {"date": "2024-07-10", "amount": 200, "category": "entertainment", "description": "перевод физическому лицу"},
    ]


# Тест для функции beneficial_cashback_categories
def test_beneficial_cashback_categories(mock_transactions):
    year = 2024
    month = 7
    result = beneficial_cashback_categories(year, month, mock_transactions)
    assert json.loads(result) == {"year": year, "month": month, "categories": ["category1", "category2", "category3"]}


# Тест для функции invest_piggy_bank
def test_invest_piggy_bank(mock_transactions):
    month = 7
    rounding_limit = 10.0
    result = invest_piggy_bank(month, mock_transactions, rounding_limit)
    assert json.loads(result) == {"month": month, "rounding_limit": rounding_limit, "saved_amount": 1234.56}


# Параметризированный тест для функции simple_search
@pytest.mark.parametrize(
    "query, expected",
    [
        ("покупка", [{"date": "2024-07-08", "amount": 100, "category": "food", "description": "покупка в магазине"}]),
        (
                "такси",
                [{"date": "2024-07-09", "amount": 150, "category": "transport", "description": "+1234567890 такси"}],
        ),
    ],
)
def test_simple_search(query, expected, mock_transactions):
    result = simple_search(query, mock_transactions)
    assert json.loads(result) == expected


# Тест для функции phone_number_search
def test_phone_number_search(mock_transactions):
    result = phone_number_search(mock_transactions)
    assert json.loads(result) == [
        {"date": "2024-07-09", "amount": 150, "category": "transport", "description": "+1234567890 такси"}
    ]


# Тест для функции person_to_person_search
def test_person_to_person_search(mock_transactions):
    result = person_to_person_search(mock_transactions)
    assert json.loads(result) == [
        {"date": "2024-07-10", "amount": 200, "category": "entertainment", "description": "перевод физическому лицу"}
    ]
