import psycopg2
from psycopg2 import Error
import os

# Параметры подключения (те же, что в docker-compose.yml)
DB_HOST = os.getenv("DB_HOST", "localhost")

DB_CONFIG = {
    "host": DB_HOST, 
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


def get_all_products_as_dict():
    """Получает все товары из базы и возвращает их в виде списка словарей"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Забираем все поля
        cursor.execute("""
            SELECT id, wb_id, name, brand, supplier, size, price, old_price, rating, feedbacks, created_at 
            FROM products 
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        # Получаем названия колонок из описания курсора
        col_names = [desc[0] for desc in cursor.description]
        
        # Превращаем каждый кортеж (row) в словарь, где ключи - это названия колонок
        products_list = []
        for row in rows:
            product_dict = dict(zip(col_names, row))
            
            # Преобразуем datetime в строку, чтобы JSON мог это переварить
            if product_dict.get('created_at'):
                product_dict['created_at'] = product_dict['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                
            products_list.append(product_dict)
            
        return products_list
        
    except Error as e:
        print(f"❌ Ошибка при получении товаров: {e}")
        return []
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()