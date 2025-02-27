import json
import re
from typing import Any, Dict, List

import pandas as pd


def analyze_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> str:
    """
    Анализирует категории кешбэка за указанный месяц и год
    """
    df = pd.DataFrame(data)

    if df.empty:
        return json.dumps({}, ensure_ascii=False, indent=4)

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
    df_filtered = df[(df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)]

    if df_filtered.empty:
        return json.dumps({}, ensure_ascii=False, indent=4)

    cashback_summary = df_filtered.groupby("Категория")["Кэшбэк"].sum().to_dict()
    return json.dumps(cashback_summary, ensure_ascii=False, indent=4)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> Any:
    """
    Рассчитывает сумму, которую можно отложить в "Инвесткопилку" через округление трат
    """
    df = pd.DataFrame(transactions)

    if df.empty:
        return 0.0

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
    df_filtered = df[df["Дата операции"].dt.strftime("%Y-%m") == month]

    if df_filtered.empty:
        return 0.0

    df_filtered["Округленная сумма"] = ((df_filtered["Сумма операции"] + (limit - 1)) // limit) * limit
    df_filtered["Разница"] = df_filtered["Округленная сумма"] - df_filtered["Сумма операции"]

    return df_filtered["Разница"].sum()


def search_phone_numbers(transactions: List[Dict[str, Any]]) -> str:
    """
    Поиск телефонных номеров в описании транзакций.
    """
    phone_pattern = re.compile(r"\+?7[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")

    found_transactions = [transaction for transaction in transactions if phone_pattern.search(transaction["Описание"])]

    return json.dumps(found_transactions, ensure_ascii=False, indent=4)


def search_personal_transfers(transactions: List[Dict[str, Any]]) -> str:
    """
    Поиск переводов физическим лицам (Фамилия И.)
    """
    transfer_pattern = re.compile(r"[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.")

    found_transfers = [
        transaction
        for transaction in transactions
        if transaction["Категория"] == "Переводы" and transfer_pattern.search(transaction["Описание"])
    ]

    return json.dumps(found_transfers, ensure_ascii=False, indent=4)


def simple_search(transactions: List[Dict[str, Any]], query: str) -> str:
    """
    Простой поиск транзакций по категории или описанию.
    """
    query_lower = query.lower()

    found_transactions = [
        transaction
        for transaction in transactions
        if query_lower in transaction["Категория"].lower() or query_lower in transaction["Описание"].lower()
    ]

    return json.dumps(found_transactions, ensure_ascii=False, indent=4)
