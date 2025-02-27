import json

from src.services import (
    analyze_cashback_categories,
    investment_bank,
    search_personal_transfers,
    search_phone_numbers,
    simple_search,
)


def test_analyze_cashback_categories() -> None:
    transactions = [
        {"Дата операции": "2024-02-10", "Категория": "Супермаркеты", "Кэшбэк": 50},
        {"Дата операции": "2024-02-15", "Категория": "Кафе", "Кэшбэк": 30},
        {"Дата операции": "2024-02-20", "Категория": "Супермаркеты", "Кэшбэк": 20},
    ]
    result = analyze_cashback_categories(transactions, 2024, 2)
    data = json.loads(result)
    assert data == {"Супермаркеты": 70, "Кафе": 30}


def test_investment_bank() -> None:
    transactions = [
        {"Дата операции": "2024-02-10", "Сумма операции": 133},
        {"Дата операции": "2024-02-15", "Сумма операции": 277},
    ]
    result = investment_bank("2024-02", transactions, 10)
    assert result == 10  # 140 - 133 + 280 - 277 = 10


def test_search_phone_numbers() -> None:
    transactions = [{"Описание": "Перевод на +79051234567"}, {"Описание": "Кафе Москва"}]
    result = search_phone_numbers(transactions)
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["Описание"] == "Перевод на +79051234567"


def test_search_personal_transfers() -> None:
    transactions = [
        {"Категория": "Переводы", "Описание": "Иванов И."},
        {"Категория": "Переводы", "Описание": "Петров П."},
        {"Категория": "Покупка", "Описание": "Кафе"},
    ]
    result = search_personal_transfers(transactions)
    data = json.loads(result)
    assert len(data) == 2


def test_simple_search() -> None:
    transactions = [
        {"Категория": "Кафе", "Описание": "Кофейня Starbucks"},
        {"Категория": "Супермаркеты", "Описание": "Пятерочка"},
    ]
    result = simple_search(transactions, "Кафе")
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["Категория"] == "Кафе"
