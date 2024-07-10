# Проект 1. Приложение для анализа банковских операций

*Приложение для анализа транзакций, которые находятся в Excel-файле. Приложение генерирует JSON-данные для веб-страниц, формирует Excel-отчеты, а также предоставляет другие сервисы.*

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

## Описание

Этот проект предназначен для обработки и фильтрации транзакций, включая функции загрузки данных из файлов Excel,
фильтрации транзакций по дате и расчета кешбэка. Также проект предоставляет отчеты по тратам на основе категорий, дней
недели и различия между рабочими и выходными днями.

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

## Использование

Пример использования функций проекта:

### Загрузка данных из файла Excel

```python
from src.utils import read_xlsx

data = read_xlsx('path_to_your_file.xlsx')
print(data)  
```

### Фильтрация транзакций по дате
```python
from src.views import filter_transactions_by_date

transactions = [
    {'Дата операции': '05.01.2018 15:28:22'},
    {'Дата операции': '04.01.2018 15:00:41'},
    {'Дата операции': '01.01.2018 12:49:53'},
]
date_str = "2018-01-04 15:00:00"
filtered_transactions = filter_transactions_by_date(transactions, date_str)
print(filtered_transactions)
```
### Расчет кешбэка
```python
from src.views import cashback

total_sum = 5000
cashback_amount = cashback(total_sum)
print(f"Total cashback: {cashback_amount}")
```
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
### Тестирование

Для запуска тестов выполните следующую команду:
*pytest*

### Команда проекта

Евгений Рыбаков — Backend developer

### Лицензия
Этот проект лицензирован на условиях MIT License.
