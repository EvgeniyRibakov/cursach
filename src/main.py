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
