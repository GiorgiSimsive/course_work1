import os
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import save_report_to_file
from src.utils import get_exchange_rates, load_settings, process_transactions


def test_load_settings() -> None:
    mock_data = '{"user_currencies": ["USD", "EUR"]}'
    with patch("builtins.open", mock_open(read_data=mock_data)):
        settings = load_settings()
        assert settings == {"user_currencies": ["USD", "EUR"]}


@patch("requests.get")
def test_get_exchange_rates(mock_get) -> None:  # type: ignore
    mock_response = {"conversion_rates": {"USD": 1, "EUR": 0.85}}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response
    rates = get_exchange_rates()
    assert rates["USD"] == 1
    assert rates["EUR"] == 0.85


@pytest.fixture
def test_process_transactions() -> None:
    data = {
        "Дата операции": pd.to_datetime(["2024-02-01 10:00:00", "2024-02-15 12:30:00", "2024-02-20 14:00:00"]),
        "Номер карты": ["*1234", "*1234", "*5678"],
        "Сумма платежа": [100.0, 200.0, 300.0],
        "Кэшбэк": [1.0, 2.0, 3.0],
        "Категория": ["Продукты", "Развлечения", "Транспорт"],
        "Описание": ["Магазин", "Кино", "Такси"],
    }
    df = pd.DataFrame(data)
    cards_summary, top_transactions = process_transactions(df, pd.Timestamp("2024-02-25 12:30:00"))
    assert len(cards_summary) == 2
    assert len(top_transactions) >= 2


def test_save_report():  # type: ignore
    @save_report_to_file
    def sample_report():  # type: ignore
        return pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    filename = "test_report.json"
    sample_report(filename=filename)
    assert os.path.exists(os.path.join("reports", filename))
    os.remove(os.path.join("reports", filename))
