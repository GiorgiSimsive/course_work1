import pandas as pd
import pytest

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday


@pytest.fixture
def sample_transactions():  # type: ignore
    return pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2024-11-01", "2024-11-02", "2024-11-05", "2024-11-06"]),
            "Сумма платежа": [1000, 2000, 1500, 2500],
            "Категория": ["Продукты", "Транспорт", "Продукты", "Развлечения"],
        }
    )


def test_spending_by_category(sample_transactions):  # type: ignore
    result = spending_by_category(sample_transactions, "Продукты", date="2025-01-01")
    assert not result.empty, "Фильтрация вернула пустой DataFrame"


def test_spending_by_weekday(sample_transactions):  # type: ignore
    result = spending_by_weekday(sample_transactions)
    assert "День недели" in result.columns
    assert "Сумма платежа" in result.columns


def test_spending_by_workday(sample_transactions):  # type: ignore
    result = spending_by_workday(sample_transactions)
    assert "Рабочий день" in result.columns
    assert "Сумма платежа" in result.columns
