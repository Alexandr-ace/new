import psycopg2
from psycopg2 import Error

# Параметры подключения (те же, что в docker-compose.yml)
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "wb_products",
    "user": "parser_user",
    "password": "parser_password"
}

def create_table():
    """Создает таблицу products, если её нет"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            wb_id INTEGER UNIQUE,
            name TEXT,
            brand TEXT,
            supplier TEXT,
            size TEXT,
            price REAL,
            old_price REAL,
            rating REAL,
            feedbacks INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        print("✅ Таблица products создана (или уже существует)")
        
    except Error as e:
        print(f"❌ Ошибка при создании таблицы: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def save_product(product_data):
    """Сохраняет один товар в базу"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO products (wb_id, name, brand, supplier, size, price, old_price, rating, feedbacks)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (wb_id) DO UPDATE SET
            price = EXCLUDED.price,
            old_price = EXCLUDED.old_price,
            rating = EXCLUDED.rating,
            feedbacks = EXCLUDED.feedbacks;
        """
        
        cursor.execute(insert_query, (
            product_data['wb_id'],
            product_data['name'],
            product_data['brand'],
            product_data['supplier'],
            product_data['size'],
            product_data['price'],
            product_data['old_price'],
            product_data['rating'],
            product_data['feedbacks']
        ))
        
        connection.commit()
        
    except Error as e:
        print(f"❌ Ошибка при сохранении товара: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_all_products():
    """Получает все товары из базы"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        products = cursor.fetchall()
        
        return products
        
    except Error as e:
        print(f"❌ Ошибка при получении товаров: {e}")
        return []
    finally:
        if connection:
            cursor.close()
            connection.close()