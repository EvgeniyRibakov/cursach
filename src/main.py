# import pandas as pd
# from reports import category_expenses_report, weekday_expenses_report, weekday_vs_weekend_expenses_report
#
# # Пример данных
# data = [
#     {"date": "2023-01-01", "category": "food", "amount": 100.0},
#     {"date": "2023-01-02", "category": "transport", "amount": 50.0},
#     {"date": "2023-01-03", "category": "food", "amount": 30.0},
#     {"date": "2023-01-04", "category": "food", "amount": 20.0},
#     {"date": "2023-01-05", "category": "entertainment", "amount": 200.0},
# ]
#
# # Преобразуем данные в DataFrame
# df = pd.DataFrame(data)
# df['date'] = pd.to_datetime(df['date'])
#
# # Вызов функций
# category_expenses_response = category_expenses_report(df, "food", "2023-01-01")
# weekday_expenses_response = weekday_expenses_report(df)
# weekday_vs_weekend_expenses_response = weekday_vs_weekend_expenses_report(df, "2023-01-01")
#
# print("Category Expenses Response:", category_expenses_response)
# print("Weekday Expenses Response:", weekday_expenses_response)
# print("Weekday vs Weekend Expenses Response:", weekday_vs_weekend_expenses_response)

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
