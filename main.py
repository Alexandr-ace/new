from curl_cffi import requests
import json
import time
from database import create_table, save_product 

url = ""

raw_cookie_string = "ВСТАВЬ_СЮДА_СВОИ_AKTUALNYE_COOKIE_ИЗ_БРАУЗЕРА"

cookies_dict = {}
if raw_cookie_string and "ВСТАВЬ_СЮДА" not in raw_cookie_string:
    for item in raw_cookie_string.split(';'):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies_dict[key.strip()] = value.strip()

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.wildberries.ru/",
}

create_table()
print("Отправляем запрос через curl_cffi с правильными куки...")
time.sleep(2)

response = requests.get(url, headers=headers, cookies=cookies_dict, impersonate="chrome120")

print(f"Код ответа: {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        print("✅ Успех! JSON получен и распарсен.")
        
        products = data.get("products", [])
        total = data.get("total", 0)
        
        if products:
            print(f"🎉 Найдено товаров: {len(products)} (всего по запросу: {total})")
            print("=" * 60)
            
            # Выводим первые 10 товаров
            for i, product in enumerate(products[:10], 1):
                name = product.get("name", "Без названия")
                brand = product.get("brand", "") or "Без бренда"
                supplier = product.get("supplier", "Неизвестно")
                rating = product.get("rating", 0)
                feedbacks = product.get("feedbacks", 0)
                
                # Цены берем из первого доступного размера
                sizes = product.get("sizes", [])
                if sizes:
                    first_size = sizes[0]
                    size_name = first_size.get("name", "н/д")
                    price_dict = first_size.get("price", {})
                    
                    # Цены в копейках, делим на 100
                    price_kopecks = price_dict.get("product", 0)
                    old_price_kopecks = price_dict.get("basic", 0)
                    
                    price_rub = price_kopecks / 100 if price_kopecks else 0
                    old_price_rub = old_price_kopecks / 100 if old_price_kopecks else 0
                else:
                    size_name = "н/д"
                    price_rub = 0
                    old_price_rub = 0

                # НОВОЕ: Сохраняем в базу
                product_data = {
                    'wb_id': product.get('id'),
                    'name': name,
                    'brand': brand,
                    'supplier': supplier,
                    'size': size_name,
                    'price': price_rub,
                    'old_price': old_price_rub,
                    'rating': rating,
                    'feedbacks': feedbacks
                }
                
                save_product(product_data)
                print(f"✅ Товар {i} сохранен в БД")
                
                print(f"\n{i}. {brand} — {name}")
                print(f"   Поставщик: {supplier}")
                print(f"   Размер: {size_name}")
                print(f"   Цена: {price_rub} ₽ (было: {old_price_rub} ₽)")
                print(f"   Рейтинг: {rating} ⭐ ({feedbacks} отзывов)")
            
            print("\n" + "=" * 60)
            print(f"Показано первых 10 товаров из {len(products)}")
            print("🎊 ПОЗДРАВЛЯЮ! Твой парсер работает идеально!")
            
        else:
            print("❌ Список товаров пуст.")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            
    except json.JSONDecodeError:
        print("❌ Пришел не JSON.")
        print(response.text[:300])
else:
    print(f"❌ Ошибка {response.status_code}.")
    