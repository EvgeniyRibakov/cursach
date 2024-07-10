# Проект 1. Приложение для анализа банковских операций

*Приложение для анализа транзакций, которые находятся в Excel-файле. Приложение генерирует JSON-данные для веб-страниц, формирует Excel-отчеты, а также предоставляет другие сервисы.*

## Установка

Для установки и настройки окружения выполните следующие шаги:

1. Клонируйте репозиторий:
    ```sh
    git clone https://github.com/EvgeniyRibakov/cursach
    cd cursach
    ```

2. Создайте виртуальное окружение и активируйте его:
    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # Для Windows
    ```

3. Установите необходимые зависимости:
    ```sh
    pip install -r requirements.txt
    ```

## Главная

В JSON-файл выводятся данные в формате:

Приветствие в формате — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи» в зависимости от текущего
времени.

По каждой карте:

    последние 4 цифры карты;
    общая сумма расходов;
    кешбэк (1 рубль на каждые 100 рублей).

Топ-5 транзакций по сумме платежа.
Курс валют.
Стоимость акций из S&P500.

## Сервисы
Простой поиск
Пользователь передает строку для поиска, возвращается JSON-ответ со всеми транзакциями, содержащими запрос в описании
или категории.

```python
def simple_search(query: str, transactions: List[Dict[str, Any]]) -> str:
    """
    Функция для сервиса «Простой поиск».

    :param query: Запрос для поиска
    :param transactions: Список транзакций в формате списка словарей
    :return: JSON-ответ
    """
    services_logger.debug(f"Запуск функции simple_search с параметром: query={query}")
    filtered_transactions = [t for t in transactions if query.lower() in t.get("description", "").lower()]
    services_logger.debug(f"Результат функции simple_search: {filtered_transactions}")
    return json.dumps(filtered_transactions)
```

## Отчеты

### Отчет по тратам по категории
```python
from src.reports import category_expenses_report
import pandas as pd

data = [
    {"date": "2023-01-01", "category": "food", "amount": 100.0},
    {"date": "2023-01-02", "category": "food", "amount": 50.0},
]
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

report = category_expenses_report(df, "food", "2023-01-01")
print(report)
```
### Отчет по тратам по дням недели
```python
from src.reports import weekday_expenses_report
import pandas as pd

data = [
    {"date": "2023-01-01", "amount": 100.0},
    {"date": "2023-01-02", "amount": 50.0},
]
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

report = weekday_expenses_report(df)
print(report)
```
### Отчет по тратам в рабочие и выходные дни
```python
from src.reports import weekday_vs_weekend_expenses_report
import pandas as pd

data = [
    {"date": "2023-01-01", "amount": 100.0},
    {"date": "2023-01-02", "amount": 50.0},
]
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

report = weekday_vs_weekend_expenses_report(df, "2023-01-01")
print(report)
```

## Использование

Пример использования функций проекта:

### Главная страница объединяющая весь код

```python
from src.utils import read_xlsx
from src.views import index_page, logger


def main() -> None:
    """
    Главная функция для запуска всей программы.
    """
    logger.info("Запуск веб-страниц")
    transactions = read_xlsx("../data/operations.xls")
    logger.debug(f"Загруженные транзакции: {transactions}")
    user_data = input("Введите текущую дату и время в формате YYYY-MM-DD HH:MM:SS: ")
    logger.debug(f"Введенные данные: {user_data}")
    result = index_page(user_data, transactions)
    print(result)


if __name__ == "__main__":
    main()
```

### Тестирование

Для запуска тестов выполните следующую команду:
*pytest*

### Команда проекта

Евгений Рыбаков — Backend developer

### Лицензия
Этот проект лицензирован на условиях MIT License.
