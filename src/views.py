import json
import os
from datetime import datetime
from typing import Any, Dict, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")


SETTINGS_FILE = "user_settings.json"


def load_settings() -> Dict[str, Any]:
    """
    Загружает пользовательские настройки
    """
    with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Файл настроек должен содержать JSON-объект")
        return data


def get_exchange_rates(base_currency: str = "USD") -> Dict[str, float]:
    """
    Получение курсов валют
    """
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("conversion_rates", {})
        if isinstance(data, dict):
            return {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}
    return {}


def get_greeting(current_time: datetime) -> str:
    """
    Определение приветствия по времени суток
    """
    hour = current_time.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def process_transactions(transactions_df: DataFrame, date: datetime) -> Tuple[DataFrame, DataFrame]:
    """
    Обработка транзакций
    """
    start_date = date.replace(day=1)
    filtered_df = transactions_df[
        (transactions_df["Дата операции"] >= start_date) & (transactions_df["Дата операции"] <= date)
    ]

    cards_summary = (
        filtered_df.groupby("Номер карты")
        .agg(total_spent=("Сумма платежа", "sum"), cashback=("Кэшбэк", "sum"))
        .reset_index()
    )
    cards_summary["cashback"] = cards_summary["total_spent"] * 0.01

    top_transactions = filtered_df.nlargest(5, "Сумма платежа")[
        ["Дата операции", "Сумма платежа", "Категория", "Описание"]
    ]
    top_transactions["Дата операции"] = top_transactions["Дата операции"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return cards_summary, top_transactions


def generate_main_page_response(input_datetime_str: str) -> str:
    """
    Генерация JSON-ответа
    """
    input_datetime = datetime.strptime(input_datetime_str, "%Y-%m-%d %H:%M:%S")
    settings = load_settings()
    exchange_rates = get_exchange_rates()
    greeting = get_greeting(input_datetime)

    transactions_df = pd.read_excel(os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx"))
    transactions_df["Дата операции"] = pd.to_datetime(transactions_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    cards_summary, top_transactions = process_transactions(transactions_df, input_datetime)
    response = {
        "greeting": greeting,
        "cards": cards_summary.to_dict(orient="records"),
        "top_transactions": top_transactions.to_dict(orient="records"),
        "currency_rates": [
            {"currency": cur, "rate": exchange_rates.get(cur, "N/A")} for cur in settings["user_currencies"]
        ],
    }
    return json.dumps(response, ensure_ascii=False, indent=4)
