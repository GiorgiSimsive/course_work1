import json
from unittest.mock import mock_open, patch

import pandas as pd

from src.views import (generate_main_page_response, get_exchange_rates, get_greeting, load_settings,
                       process_transactions)


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


def test_get_greeting() -> None:
    assert get_greeting(pd.Timestamp("2024-02-26 06:00:00")) == "Доброе утро"
    assert get_greeting(pd.Timestamp("2024-02-26 13:00:00")) == "Добрый день"
    assert get_greeting(pd.Timestamp("2024-02-26 19:00:00")) == "Добрый вечер"
    assert get_greeting(pd.Timestamp("2024-02-26 02:00:00")) == "Доброй ночи"


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


@patch("src.views.load_settings", return_value={"user_currencies": ["USD", "EUR"]})
@patch("src.views.get_exchange_rates", return_value={"USD": 1, "EUR": 0.85})
@patch("pandas.read_excel")
def test_generate_main_page_response(mock_read_excel, mock_get_rates, mock_load_settings) -> None:  # type: ignore
    data = {
        "Дата операции": pd.to_datetime(["2021-12-01 10:00:00", "2021-12-15 12:30:00", "2021-12-20 14:00:00"]),
        "Номер карты": ["*1234", "*1234", "*5678"],
        "Сумма платежа": [100.0, 200.0, 300.0],
        "Кэшбэк": [1.0, 2.0, 3.0],
        "Категория": ["Продукты", "Развлечения", "Транспорт"],
        "Описание": ["Магазин", "Кино", "Такси"],
    }
    mock_read_excel.return_value = pd.DataFrame(data)
    response_json = generate_main_page_response("2021-12-15 12:30:00")
    response = json.loads(response_json)
    assert response["greeting"] == "Добрый день"
    assert len(response["cards"]) > 0
    assert len(response["top_transactions"]) > 0
