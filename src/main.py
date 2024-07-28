from src.reports import main_reports
from src.services import main_services
from src.views import main_views


def main() -> None:
    """
    Главная функция для запуска всей программы.
    """
    main_views()
    main_reports()
    main_services()


if __name__ == "__main__":
    main()
