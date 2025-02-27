import json
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

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


def save_report(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения отчета в JSON-файл.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            result = func(*args, **kwargs)

            if filename is None:
                default_name = f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                default_name = filename

            with open(default_name, "w", encoding="utf-8") as file:
                if isinstance(result, pd.DataFrame):
                    result = result.to_dict(orient="records")
                json.dump(result, file, ensure_ascii=False, indent=4)

            print(f"Отчет сохранен в {default_name}")
            return result

        return wrapper

    return decorator
