from fastapi import FastAPI
from database import get_all_products_as_dict

# Создаем экземпляр приложения
app = FastAPI(
    title="Wildberries Parser API",
    description="API для получения данных о товарах, спарсенных с Wildberries",
    version="1.0.0"
)

# Эндпоинт 1: Главная страница (проверка, что сервер жив)
@app.get("/")
def read_root():
    return {"message": "🚀 API работает! Перейди в /docs для документации."}

# Эндпоинт 2: Получить все товары из базы данных
@app.get("/products")
def get_products():
    """Возвращает список всех товаров из базы данных PostgreSQL"""
    products = get_all_products_as_dict()
    
    return {
        "total_items": len(products),
        "data": products
    }

# Эндпоинт 3: Получить только самые дешевые товары (бонус!)
@app.get("/products/cheap")
def get_cheap_products(max_price: float = 600.0):
    """Возвращает товары, цена которых ниже указанной (по умолчанию 600 руб)"""
    # Здесь мы могли бы сделать SQL-запрос с WHERE price <= max_price,
    # но для простоты отфильтруем уже полученный список
    all_products = get_all_products_as_dict()
    cheap_products = [p for p in all_products if p['price'] <= max_price]
    
    return {
        "max_price_filter": max_price,
        "total_items": len(cheap_products),
        "data": cheap_products
    }