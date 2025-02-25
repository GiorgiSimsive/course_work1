import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

# Загружаем пользовательские настройки
SETTINGS_FILE = "user_settings.json"


def load_settings():
    with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# Получение курсов валют
def get_exchange_rates(base_currency="USD"):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("conversion_rates", {})
    else:
        return {}


# Определение приветствия по времени суток
def get_greeting(current_time):
    hour = current_time.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


# Обработка транзакций
def process_transactions(transactions_df, date):
    start_date = date.replace(day=1)
    # Отладочный вывод для проверки дат
    print(f"\nФильтруем данные от {start_date} до {date}")
    print(transactions_df[["Дата операции"]].head())  # Смотрим, какие даты в данных
    print("Диапазон дат в DataFrame:", transactions_df["Дата операции"].min(), "-",
          transactions_df["Дата операции"].max())

    filtered_df = transactions_df[
        (transactions_df["Дата операции"] >= start_date) & (transactions_df["Дата операции"] <= date)]
    # Проверяем, не пуст ли DataFrame после фильтрации
    print("\nОтфильтрованные данные:")
    print(filtered_df.head())
    # Группировка по последним 4 цифрам карты
    cards_summary = filtered_df.groupby("Номер карты").agg(
        total_spent=("Сумма платежа", "sum"),
        cashback=("Кэшбэк", "sum")
    ).reset_index()
    cards_summary["cashback"] = cards_summary["total_spent"] * 0.01  # 1% кешбэка

    # Топ-5 транзакций по сумме платежа
    top_transactions = filtered_df.nlargest(5, "Сумма платежа")[
        ["Дата операции", "Сумма платежа", "Категория", "Описание"]]

    return cards_summary, top_transactions


# Генерация JSON-ответа
def generate_main_page_response(input_datetime_str):
    input_datetime = datetime.strptime(input_datetime_str, "%Y-%m-%d %H:%M:%S")
    settings = load_settings()
    exchange_rates = get_exchange_rates()
    greeting = get_greeting(input_datetime)

    # Чтение данных из Excel
    transactions_df = pd.read_excel(os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx"))
    transactions_df["Дата операции"] = pd.to_datetime(transactions_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    print("Типы данных в DataFrame:")
    print(transactions_df.dtypes)  # Проверяем типы данных
    print("\nПервые строки DataFrame:")
    print(transactions_df.head())  # Смотрим, что загружено
    print("\nНазвания колонок:")
    print(transactions_df.columns)  # Проверяем названия колонок
    cards_summary, top_transactions = process_transactions(transactions_df, input_datetime)
    print("\nОтфильтрованные транзакции:")
    print(cards_summary)  # Проверяем, есть ли данные после фильтрации
    response = {
        "greeting": greeting,
        "cards": cards_summary.to_dict(orient="records"),
        "top_transactions": top_transactions.to_dict(orient="records"),
        "currency_rates": [{"currency": cur, "rate": exchange_rates.get(cur, "N/A")} for cur in
                           settings["user_currencies"]]
    }

    return json.dumps(response, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    test_datetime = "2025-02-25 12:30:00"
    print(generate_main_page_response(test_datetime))