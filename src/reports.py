import json
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional

import pandas as pd


def save_report_to_file(func: Callable) -> Callable:
    """
    Сохраняет отчеты в файл
    """
    @wraps(func)
    def wrapper(*args, filename: Optional[str] = None, **kwargs):  # type: ignore
        result = func(*args, **kwargs)

        if filename is None:
            filename = f"{func.__name__}.json"

        file_path = os.path.join("reports", filename)
        os.makedirs("reports", exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(result.astype(str).to_dict(orient="records"), file, ensure_ascii=False, indent=4)

        return result

    return wrapper


@save_report_to_file
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Траты по категории
    """
    date_converted = datetime.today() if date is None else datetime.strptime(date, "%Y-%m-%d")
    three_months_ago = date_converted - timedelta(days=90)
    filtered_data = transactions[
        (transactions["Категория"] == category) & (transactions["Дата операции"] >= three_months_ago)
    ]
    return filtered_data[["Дата операции", "Сумма платежа"]]


@save_report_to_file
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Траты по дням недели
    """
    date_converted = datetime.today() if date is None else datetime.strptime(date, "%Y-%m-%d")
    three_months_ago = date_converted - timedelta(days=90)
    transactions_filtered = transactions[transactions["Дата операции"] >= three_months_ago].copy()
    transactions_filtered["День недели"] = transactions_filtered["Дата операции"].dt.day_name()
    return transactions_filtered.groupby("День недели")["Сумма платежа"].mean().reset_index()


@save_report_to_file
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Траты в рабочий/выходной день
    """
    date_converted = datetime.today() if date is None else datetime.strptime(date, "%Y-%m-%d")
    three_months_ago = date_converted - timedelta(days=90)
    transactions_filtered = transactions[transactions["Дата операции"] >= three_months_ago].copy()
    transactions_filtered["Рабочий день"] = transactions_filtered["Дата операции"].dt.weekday < 5
    return transactions_filtered.groupby("Рабочий день")["Сумма платежа"].mean().reset_index()
