# course_work1
# Приложение для анализа транзакции

## Описание:
Приложение для анализа транзакций, которые находятся в Excel-файле.
Приложение будет генерировать JSON-данные для веб-страниц, 
формировать Excel-отчеты, а также предоставлять другие сервисы

## Использование:
Для проверки работы модуля views.py вставьте в конце:
if __name__ == "__main__":
    test_datetime = "2021-12-25 12:30:00"
    print(generate_main_page_response(test_datetime))

## Тестирование
Проект включает модульные тесты для проверки корректности работы 
функций и методов. Для тестирования используется библиотека pytest 
и статический анализ типов — mypy.

## Запуск тестов
1. Для запуска тестов выполните следующую команду в терминале:
`pytest`
2. Если хотите увидеть вывод в процентах:
`pytest --cov --cov-report term-missing`

# Сервисы
## Поиск по телефонным номерам
1. Формат входных данных
transactions – список словарей с транзакциями
2. Поиск телефонных номеров
Формат номеров: +7 921 111-22-33, +7 (921) 111-22-33, 8 921 1112233, +79211112233 и другие.
3. Формат выхода
JSON со всеми транзакциями, где в описании найден номер телефона.
### Работа функции
1. Создай test_services.py и добавь туда:
`from services import search_phone_numbers

transactions = [
    {"Дата операции": "2024-02-10", "Описание": "Перевод другу +7 921 111-22-33", "Категория": "Переводы", "Сумма": 1500},
    {"Дата операции": "2024-02-12", "Описание": "Оплата Тинькофф Мобайл +7 995 555-55-55", "Категория": "Связь", "Сумма": 500},
    {"Дата операции": "2024-02-15", "Описание": "Супермаркет 'Пятерочка'", "Категория": "Продукты", "Сумма": 1200},
] # Тестовые транзакции

print("Результат поиска телефонов:")
print(search_phone_numbers(transactions)) # Запуск теста`
2. Программа должна вывести JSON с найденными транзакциями:
[
    {
        "Дата операции": "2024-02-10",
        "Описание": "Перевод другу +7 921 111-22-33",
        "Категория": "Переводы",
        "Сумма": 1500
    },
    {
        "Дата операции": "2024-02-12",
        "Описание": "Оплата Тинькофф Мобайл +7 995 555-55-55",
        "Категория": "Связь",
        "Сумма": 500
    }
]
