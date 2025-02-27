import json
from unittest.mock import patch

import pandas as pd

from src.views import generate_main_page_response, get_greeting


def test_get_greeting() -> None:
    assert get_greeting(pd.Timestamp("2024-02-26 06:00:00")) == "Доброе утро"
    assert get_greeting(pd.Timestamp("2024-02-26 13:00:00")) == "Добрый день"
    assert get_greeting(pd.Timestamp("2024-02-26 19:00:00")) == "Добрый вечер"
    assert get_greeting(pd.Timestamp("2024-02-26 02:00:00")) == "Доброй ночи"


@patch("src.views.load_settings", return_value={"user_currencies": ["USD", "EUR"]})
@patch("src.utils.get_exchange_rates", return_value={"USD": 1, "EUR": 0.85})
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
