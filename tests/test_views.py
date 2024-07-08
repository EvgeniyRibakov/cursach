from datetime import datetime

import pytest
from unittest.mock import patch, MagicMock
from src.views import card_data, cashback, calculate_cashback, get_utils, index_page, filter_transactions_by_date


# Фикстура для тестовых данных операций
@pytest.fixture
def mock_operations():
    return [
        {"Номер карты": "1234567890123456", "Бонусы (включая кэшбэк)": 10, "Сумма операции": -1000},
        {"Номер карты": "1234567890123456", "Бонусы (включая кэшбэк)": 5, "Сумма операции": -500},
        {"Номер карты": "1234567890123456", "Сумма операции": -300},
        {"Номер карты": None, "Сумма операции": -200},
    ]


# Тест для функции get_utils
def test_get_utils():
    # Мокирование импортируемых функций
    with patch('src.utils.read_xlsx', return_value=MagicMock()) as mock_read_xlsx:
        with patch('src.utils.welcome_message', return_value=MagicMock()) as mock_welcome_message:
            with patch('src.utils.write_json', return_value=MagicMock()) as mock_write_json:
                read_xlsx, welcome_message, write_json = get_utils()
                # Проверка, что возвращаемые значения являются мокированными функциями
                assert read_xlsx == mock_read_xlsx
                assert welcome_message == mock_welcome_message
                assert write_json == mock_write_json


# Тест для функции calculate_cashback
def test_calculate_cashback():
    # Подготовка данных для теста
    test_cards = [
        {'total_spent': 1000, 'cashback': None},
        {'total_spent': -100, 'cashback': None},
        {'total_spent': 0, 'cashback': None}
    ]
    expected_results = [
        {'total_spent': 1000, 'cashback': 10},
        {'total_spent': -100, 'cashback': 0},
        {'total_spent': 0, 'cashback': 0}
    ]

    # Мокирование логгера
    with patch('src.views.logger') as mock_logger:
        # Вызов функции для тестирования
        results = calculate_cashback(test_cards)
        # Проверка результатов
        assert results == expected_results
        # Проверка вызовов логгера
        assert mock_logger.info.call_count == 3
        mock_logger.info.assert_any_call("Успешно! Результат - 10")
        mock_logger.info.assert_any_call("Отрицательная сумма трат, кэшбэк установлен в 0")


# Тест для функции card_data
def test_card_data(mock_operations):
    result = card_data(mock_operations)
    assert result == [{"last_digits": "3456", "total_spent": 1800.0, "cashback": 15.0}]


# Тест для функции filter_transactions_by_date
def test_filter_transactions_by_date():
    transactions = [
        {"Дата операции": "01.01.2020 12:00:00", "сумма": 100},
        {"Дата операции": "01.01.2021 12:00:00", "сумма": 200}
    ]
    filter_date = datetime(2020, 12, 31, 23, 59, 59)

    with patch('src.views.logger') as mock_logger:
        filtered = filter_transactions_by_date(transactions, filter_date)
        assert len(filtered) == 1
        assert filtered[0]["сумма"] == 100
        mock_logger.debug.assert_called_with(
            "Отфильтрованные транзакции: [{'Дата операции': '01.01.2020 12:00:00', 'сумма': 100}]")


# Тест для функции index_page
def test_index_page():
    data_time = "2020-01-01 12:00:00"
    transactions = [
        {"Дата операции": "01.01.2020 12:00:00", "сумма": 100}
    ]

    with patch('src.views.logger') as mock_logger, \
            patch('src.views.welcome_message', return_value="Приветствие"), \
            patch('src.views.filter_transactions_by_date', return_value=transactions), \
            patch('src.views.card_data', return_value=[{"total_spent": 100, "cashback": None}]), \
            patch('src.views.calculate_cashback', return_value=[{"total_spent": 100, "cashback": 1}]), \
            patch('src.views.write_json', return_value=None) as mock_write_json:
        result = index_page(data_time, transactions)
        assert "Приветствие" in result
        assert '"cashback": 1' in result
        mock_logger.info.assert_called_with("Запуск главной страницы")
        mock_write_json.assert_called_with("index_page.json",
                                           {"greeting": "Приветствие", "cards": [{"total_spent": 100, "cashback": 1}]})


def test_calculate_cashback():
    # Тестовые данные
    cards = [
        {'total_spent': 1000, 'cashback': 0},
        {'total_spent': 500, 'cashback': 0},
        {'total_spent': 100, 'cashback': 0}
    ]

    # Ожидаемые результаты
    expected_cashbacks = [10, 5, 1]

    # Вызов тестируемой функции
    calculate_cashback(cards)

    # Проверка результатов
    for card, expected_cashback in zip(cards, expected_cashbacks):
        assert card['cashback'] == expected_cashback, f"Ошибка в карте с total_spent: {card['total_spent']}"


def test_calculate_cashback_with_no_spending():
    # Карта без трат
    cards = [{'total_spent': 0, 'cashback': 0}]

    # Вызов тестируемой функции
    calculate_cashback(cards)

    # Проверка, что кэшбэк равен 0
    assert cards[0]['cashback'] == 0, "Кэшбэк должен быть 0 для карты без трат"


def test_calculate_cashback_with_negative_spending():
    # Карта с отрицательной суммой трат (что не должно произойти)
    cards = [{'total_spent': -100, 'cashback': 0}]

    # Вызов тестируемой функции
    calculate_cashback(cards)

    # Проверка, что кэшбэк не был рассчитан
    assert cards[0]['cashback'] == 0, "Не должно быть кэшбэка для карты с отрицательной суммой трат"


# Тест на проверку, что функция возвращает целое число
def test_cashback_returns_int():
    assert isinstance(cashback(1000), int), "Результат должен быть целым числом"


# Тест на проверку корректности расчета кэшбэка
def test_cashback_calculation():
    assert cashback(1000) == 10, "Кэшбэк для 1000 должен быть 10"


# Тест на проверку, что кэшбэк не округляется вверх
def test_cashback_no_round_up():
    assert cashback(1999) == 19, "Кэшбэк для 1999 должен быть 19, без округления вверх"


# Тест на проверку работы функции с нулевым значением
def test_cashback_zero():
    assert cashback(0) == 0, "Кэшбэк для 0 должен быть 0"


# Тест на проверку работы функции с отрицательным значением
def test_cashback_negative():
    assert cashback(-1000) == -10, "Кэшбэк для -1000 должен быть -10"


# Тест на проверку, что функция не возвращает отрицательный кэшбэк для положительных сумм
def test_cashback_positive_input():
    assert cashback(999) >= 0, "Кэшбэк не должен быть отрицательным для положительных сумм"


# Параметризованный тест для проверки различных значений
@pytest.mark.parametrize("input_value, expected_output", [
    (100, 1),
    (500, 5),
    (1000, 10),
    (0, 0),
    (-100, -1),
    (999, 9),
    (1001, 10)
])
def test_cashback_parametrized(input_value, expected_output):
    assert cashback(input_value) == expected_output, f"Кэшбэк для {input_value} должен быть {expected_output}"


# Тест для функции cashback
def test_cashback():
    assert cashback(1000) == 10
