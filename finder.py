from gspread import service_account
import json


# формирование словаря из таблиц
def data_updater():
    gc = service_account(filename="configs/pidor-of-the-day-5880592e7067.json")

    sheet_urls = [
        "https://docs.google.com/spreadsheets/d/1p4xQXqozQugy3NaHut3TUY6COqvzCgYb2AEMV1Cx6Zc/edit?pli=1&gid=1677852760#gid=1677852760",
        "https://docs.google.com/spreadsheets/d/1zc7Fm5wKWpcrZwG1EArIU8RHiM0gNPwE5hppvP8B5XE/edit?gid=1733893965#gid=1733893965",
        "https://docs.google.com/spreadsheets/d/1WqHRERVNTglOTQnYPf-tJg51InoGaPoKpDcgFxs9b0I/edit?gid=1246518664#gid=1246518664"
    ]

    full_data = {}

    for url in sheet_urls:
        sh = gc.open_by_url(url)
        worksheet = sh.sheet1
        values = worksheet.get_all_records()
        for row in values:
            model = row.get("Модель")
            article = row.get("Артикул товара")
            if model and article:
                key = f'{article}__{model}'
                full_data[key] = row

    # Сохраняем в файл
    with open("local_data/products.json", "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)


## поиск данных в словаре по артикулу или названию
# def find_product(query: str) -> dict | None:
#     with open("local_data/products.json", "r", encoding="utf-8") as f:
#         products_db = json.load(f)
#     return products_db.get(query.strip().lower())