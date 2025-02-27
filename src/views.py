import json
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from src.utils import get_exchange_rates, load_settings, process_transactions

load_dotenv()


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


if __name__ == "__main__":
    test_datetime = "2021-12-25 12:30:00"
    print(generate_main_page_response(test_datetime))
