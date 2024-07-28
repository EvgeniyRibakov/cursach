import json
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

from src.services import get_expenses, get_transactions, main_services


# Фикстура для имитации данных Excel
@pytest.fixture
def mock_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Описание": ["Оплата услуг", "Покупка в магазине", "Перевод физическому лицу"],
            "Категория": ["Коммунальные услуги", "Продукты", "Переводы"],
        }
    )


# Тест для успешного поиска
@patch("pandas.read_excel")
@patch("builtins.open", new_callable=mock_open)
def test_get_transactions_success(
    mock_open_instance: MagicMock, mock_read_excel: MagicMock, mock_data: pd.DataFrame
) -> None:
    mock_read_excel.return_value = mock_data

    search_term: str = "магазин"
    result: str = get_transactions(search_term)
    result_data = json.loads(result)

    assert len(result_data) == 1
    assert result_data[0]["Описание"] == "Покупка в магазине"
    assert result_data[0]["Категория"] == "Продукты"

    mock_open_instance().write.assert_called()

    # Проверка записи в файл
    written_data = "".join(call.args[0] for call in mock_open_instance().write.call_args_list)
    expected_data = json.dumps(
        [{"Описание": "Покупка в магазине", "Категория": "Продукты"}], indent=4, ensure_ascii=False
    )
    assert written_data.strip() == expected_data.strip()


# Тест для отсутствия совпадений
@patch("pandas.read_excel")
@patch("builtins.open", new_callable=mock_open)
def test_get_transactions_no_match(
    mock_open_instance: MagicMock, mock_read_excel: MagicMock, mock_data: pd.DataFrame
) -> None:
    mock_read_excel.return_value = mock_data

    search_term: str = "несуществующее слово"
    result: str = get_transactions(search_term)
    result_data = json.loads(result)

    assert len(result_data) == 1
    assert result_data[0]["message"] == "Слово не найдено ни в одной категории"

    mock_open_instance().write.assert_called()

    # Проверка записи в файл
    written_data = "".join(call.args[0] for call in mock_open_instance().write.call_args_list)
    expected_data = json.dumps([{"message": "Слово не найдено ни в одной категории"}], indent=4, ensure_ascii=False)
    assert written_data.strip() == expected_data.strip()


# Тест для отсутствующего файла
@patch("pandas.read_excel")
def test_get_transactions_file_not_found(mock_read_excel: MagicMock) -> None:
    mock_read_excel.side_effect = FileNotFoundError

    search_term: str = "магазин"
    result: str = get_transactions(search_term)
    result_data = json.loads(result)

    assert "error" in result_data
    assert result_data["error"] == "Файл ../data/operations.xls не найден."


# Тест для общего исключения
@patch("pandas.read_excel")
def test_get_transactions_exception(mock_read_excel: MagicMock) -> None:
    mock_read_excel.side_effect = Exception("Неизвестная ошибка")

    search_term: str = "магазин"
    result: str = get_transactions(search_term)
    result_data = json.loads(result)

    assert "error" in result_data
    assert "Произошла ошибка: Неизвестная ошибка" in result_data["error"]


# Фикстура для создания DataFrame с тестовыми данными
@pytest.fixture
def transactions_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Дата платежа": ["01.06.2023", "15.07.2023", "30.07.2023", "01.08.2023"],
            "Категория": ["продукты", "развлечения", "продукты", "коммунальные услуги"],
            "Сумма платежа": [100, 200, 150, 300],
        }
    )


# Тест с правильными данными и категорией, которая присутствует в транзакциях
def test_get_expenses_success(transactions_data: pd.DataFrame) -> None:
    report_date: str = "2023-08-31"
    category: str = "продукты"
    result: str = get_expenses(transactions_data, category, report_date)
    result_data = json.loads(result)

    assert result_data["category"] == category
    assert result_data["total_expenses"] == 250
    assert result_data["report_date"] == report_date


# Тест с категорией, которая отсутствует в транзакциях
def test_get_expenses_category_not_found(transactions_data: pd.DataFrame) -> None:
    report_date: str = "2023-08-31"
    category: str = "одежда"
    result: str = get_expenses(transactions_data, category, report_date)
    result_data = json.loads(result)

    assert result_data["category"] == category
    assert result_data["total_expenses"] == 0
    assert result_data["report_date"] == report_date


# Тест с пустым набором транзакций
def test_get_expenses_empty_transactions() -> None:
    transactions_data: pd.DataFrame = pd.DataFrame(columns=["Дата платежа", "Категория", "Сумма платежа"])
    report_date: str = "2023-08-31"
    category: str = "продукты"
    result: str = get_expenses(transactions_data, category, report_date)
    result_data = json.loads(result)

    assert result_data["category"] == category
    assert result_data["total_expenses"] == 0
    assert result_data["report_date"] == report_date


# Тест с указанием даты отчета и без указания даты отчета
def test_get_expenses_no_report_date(transactions_data: pd.DataFrame) -> None:
    category: str = "продукты"
    result: str = get_expenses(transactions_data, category)
    result_data = json.loads(result)

    assert result_data["category"] == category
    assert result_data["total_expenses"] == 0
    assert result_data["report_date"] == str(datetime.now().date())


# Фикстура для имитации данных Excel
@pytest.fixture
def mock_transactions_data() -> dict:
    return {
        "Дата платежа": ["01.06.2023", "15.07.2023", "30.07.2023", "01.08.2023"],
        "Категория": ["продукты", "развлечения", "продукты", "коммунальные услуги"],
        "Сумма платежа": [100, 200, 150, 300],
    }


@patch("builtins.input", side_effect=["Такси", "Супермаркет", "2021-12-31"])
@patch("src.services.get_transactions")
@patch("src.services.get_expenses")
@patch("src.services.read_xlsx")
def test_main_services(
    mock_read_xlsx: MagicMock,  # mock для функции чтения Excel
    mock_get_expenses: MagicMock,  # mock для функции получения расходов
    mock_get_transactions: MagicMock,  # mock для функции получения транзакций
    mock_transactions_data: dict,  # имитация данных транзакций
) -> None:
    # Задаем возвращаемое значение для функции read_xlsx
    mock_read_xlsx.return_value = pd.DataFrame(mock_transactions_data)  # Исправлено, убраны скобки

    # Задаем ожидаемые результаты для мока функций
    mock_get_transactions.return_value = json.dumps([{"Описание": "Поездка на такси", "Категория": "Транспорт"}])
    mock_get_expenses.return_value = json.dumps(
        {"category": "Супермаркет", "total_expenses": 200, "report_date": "2021-12-31"}
    )

    # Запускаем основную функцию
    main_services()

    # Проверяем, что функции были вызваны с ожидаемыми аргументами
    mock_get_transactions.assert_called_once_with("Такси")
    mock_get_expenses.assert_called_once_with(mock_read_xlsx.return_value, "Супермаркет", "2021-12-31")


if __name__ == "__main__":
    pytest.main()
