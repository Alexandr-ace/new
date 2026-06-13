import telebot
import requests
import os

# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ BOTFATHER
BOT_TOKEN = "ВСТАВЬ_СВОЙ_ТОКЕН"

bot = telebot.TeleBot(BOT_TOKEN)

# Адрес твоего локального API (так как бот запущен на твоем Маке, он стучится в localhost)
# Если бы бот был внутри Docker, адрес был бы "http://api:8000"
API_URL = "http://127.0.0.1:8000"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Реакция на команду /start"""
    welcome_text = (
        "👋 Привет! Я бот для мониторинга цен на Wildberries.\n\n"
        "Доступные команды:\n"
        "/cheap <цена> — показать товары дешевле указанной суммы (например: /cheap 500)\n"
        "/all — показать последние 5 добавленных товаров"
    )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['cheap'])
def show_cheap_products(message):
    """Реакция на команду /cheap"""
    try:
        # Разбираем команду. Если пользователь написал "/cheap 600", берем 600
        parts = message.text.split()
        max_price = parts[1] if len(parts) > 1 else "500" # По умолчанию 500
        
        # Делаем запрос к НАШЕМУ ЖЕ FastAPI!
        response = requests.get(f"{API_URL}/products/cheap?max_price={max_price}")
        data = response.json()
        
        products = data.get("data", [])
        
        if not products:
            bot.send_message(message.chat.id, f"😕 Товаров дешевле {max_price} ₽ не найдено.")
            return
            
        # Формируем красивое сообщение
        result_text = f"🔥 Найдено товаров дешевле {max_price} ₽: {data['total_items']}\n\n"
        
        # Показываем максимум 3 товара, чтобы не спамить в чат
        for p in products[:3]:
            result_text += (
                f"🧦 *{p['name']}*\n"
                f"🏷 Бренд: {p['brand'] or 'Нет'}\n"
                f"💰 Цена: *{p['price']} ₽* (было {p['old_price']} ₽)\n"
                f"🏢 Поставщик: {p['supplier']}\n"
                f"⭐ Рейтинг: {p['rating']} ({p['feedbacks']} отз.)\n\n"
                
            )
            
        bot.send_message(message.chat.id, result_text, parse_mode="Markdown")
        
    except requests.exceptions.ConnectionError:
        bot.send_message(message.chat.id, "❌ Ошибка: Не могу подключиться к API. Убедись, что FastAPI запущен.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {e}")

@bot.message_handler(commands=['all'])
def show_all_products(message):
    """Реакция на команду /all"""
    try:
        response = requests.get(f"{API_URL}/products")
        data = response.json()
        products = data.get("data", [])[:5] # Берем только 5 последних
        
        result_text = "📦 Последние 5 товаров в базе:\n\n"
        for p in products:
            result_text += f"• {p['name']} — {p['price']} ₽\n"
            
        bot.send_message(message.chat.id, result_text)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

print("🤖 Бот запущен и ожидает сообщений...")
# Запускаем бота в режиме постоянного опроса серверов Telegram
bot.polling(none_stop=True)