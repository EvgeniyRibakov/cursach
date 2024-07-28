from unittest.mock import Mock, patch

from src.main import main


@patch("src.main.main_views")
@patch("src.main.main_reports")
@patch("src.main.main_services")
def test_main(mock_main_services: Mock, mock_main_reports: Mock, mock_main_views: Mock) -> None:
    # Вызываем главную функцию
    main()

    # Проверяем, что все три функции были вызваны
    mock_main_views.assert_called_once()
    mock_main_reports.assert_called_once()
    mock_main_services.assert_called_once()
