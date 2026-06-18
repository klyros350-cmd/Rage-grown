import telebot
from telebot import types
import os
import re
import sqlite3
from datetime import datetime
import json

# --- НАСТРОЙКИ ---
TOKEN = '8853179512:AAFdjo0jG7RWLbm4f0rmwXc6xreA7-zHvxA'
ADMIN_ID = 7301878856
MANAGER_LINK = "https://t.me/RageGrown"
SITE_URL = "http://микрозеленьиваново.рф/"
REVIEW_LINK = "https://yandex.ru/profile/-/CPbqfD9O"

# --- СОЗДАЕМ ПАПКИ ДЛЯ ДАННЫХ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, 'users.txt')
DB_PATH = os.path.join(DATA_DIR, 'microgreen_bot.db')

# Временное хранилище
user_orders = {}
temp_order_data = {}
user_discount = {}

bot = telebot.TeleBot(TOKEN)

# --- БАЗА ДАННЫХ ---
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            phone TEXT,
            address TEXT,
            order_data TEXT,
            total_amount INTEGER,
            status TEXT DEFAULT 'новый',
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_database()

# --- КАТАЛОГ ---
catalog = {
    "📦 НАБОР НОВИЧКА": {
        "price": 400,
        "taste": "✅ Горошек (сладкий)\n✅ Подсолнечник (семечки)\n✅ Редис (слабоострый)\n\n💡 Идеальный старт! 3 лотка по цене 2-х."
    },
    "🥗 НАБОР САЛАТНЫЙ": {
        "price": 420,
        "taste": "🌿 Руккола (ореховая)\n🌿 Мизуна (нежная)\n🌿 Горчица (пикантная)\n\n💡 Супер добавка к любому салату."
    },
    "🌱 Горох": {
        "price": 145,
        "taste": "🌱 Сладкий, хрустящий, вкус молодого горошка с грядки."
    },
    "🌱 Кольраби": {
        "price": 150,
        "taste": "🌱 Нежный вкус капусты, очень сочная."
    },
    "🌱 Горчица": {
        "price": 150,
        "taste": "🌱 Пикантная, острая, придает жгучую нотку."
    },
    "🌱 Подсолнечник": {
        "price": 145,
        "taste": "🌱 Сочный, маслянистый, вкус сырых семечек."
    },
    "🌱 Кресс-салат": {
        "price": 150,
        "taste": "🌱 Острый, напоминает хрен или васаби."
    },
    "🌱 Редис Чайна Роуз": {
        "price": 160,
        "taste": "🌱 Приятная острота, красивый розовый стебель."
    },
    "🌱 Руккола": {
        "price": 160,
        "taste": "🌱 Яркий горчично-ореховый вкус, пряная."
    },
    "🌱 Брокколи": {
        "price": 150,
        "taste": "🌱 Мягкий, нежный капустный вкус. Очень полезная!"
    },
    "🌱 Кориандр": {
        "price": 160,
        "taste": "🌱 Яркий вкус кинзы, но более нежный."
    },
    "🌱 Амарант красный": {
        "price": 180,
        "taste": "🌱 Землистый, свекольный вкус. Очень красивый цвет."
    },
    "🌱 Редис фиолетовый": {
        "price": 160,
        "taste": "🌱 Острый редисочный вкус и насыщенный фиолетовый цвет."
    },
    "🌱 Мизуна": {
        "price": 180,
        "taste": "🌱 Японская капуста, легкая горчинка."
    },
    "🌱 Мелисса": {
        "price": 200,
        "taste": "🌱 Освежающий лимонно-мятный вкус."
    },
    "🌱 Базилик фиолетовый": {
        "price": 200,
        "taste": "🌱 Пряный, гвоздичный аромат."
    },
    "🌱 Базилик зеленый": {
        "price": 200,
        "taste": "🌱 Свежий и сладковато-пряный классический вкус зеленого базилика."
    },
    "🌱 Щавель Лава": {
        "price": 250,
        "taste": "🌱 Кисловатый, освежающий вкус молодого щавеля."
    },
    "🌱 Маш (ростки 125-150 гр)": {
        "price": 300,
        "taste": "🌱 Нежные хрустящие ростки маша, популярны в азиатской кухне."
    },
}

# --- ФОТО ---
# Фото лежат в той же папке, что и bot.py
image_filenames = {
    "🌱 Горох": "goroh.jpg",
    "🌱 Кольраби": "kolrabi.jpg",
    "🌱 Горчица": "gorchica.jpg",
    "🌱 Подсолнечник": "podsolnechnik.jpg",
    "🌱 Кресс-салат": "kress.jpg",
    "🌱 Редис Чайна Роуз": "redis_rose.jpg",
    "🌱 Руккола": "rukola.jpg",
    "🌱 Брокколи": "brokoli.jpg",
    "🌱 Кориандр": "koriandr.jpg",
    "🌱 Амарант красный": "photo.jpg",
    "🌱 Редис фиолетовый": "redis_fiolet.jpg",
    "🌱 Мизуна": "mizuna.jpg",
    "🌱 Мелисса": "melissa.jpg",
    "🌱 Базилик фиолетовый": "bazilik.jpg",
    "🌱 Базилик зеленый": "bazilik_zel2.jpg",
    "🌱 Щавель Лава": "shavel.jpg",
    "🌱 Маш (ростки 125-150 гр)": "mash.jpg",
}

def get_photo_path(filename):
    return os.path.join(BASE_DIR, filename)

# --- ПРОМОКОДЫ ---
promocodes = {
    "МИКРО2025": 10,
    "НОВИЧОК": 15,
    "ЗЕЛЕНЬ": 5
}

# --- СОХРАНЕНИЕ КЛИЕНТОВ ---
def save_user(user_id):
    users = set()
    try:
        with open(USERS_FILE, "r") as f:
            for line in f:
                users.add(line.strip())
    except FileNotFoundError:
        pass
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(str(user_id) + "\n")

# --- ВАЛИДАЦИЯ ТЕЛЕФОНА ---
def validate_phone(phone):
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    pattern = r'^(\+7|8|7)?[0-9]{10}$'
    return re.match(pattern, phone_clean) is not None

# --- СОХРАНЕНИЕ ЗАКАЗА В БД ---
def save_order_to_db(user_id, user_name, phone, address, cart, total):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    order_json = json.dumps(cart, ensure_ascii=False)
    cursor.execute('''
        INSERT INTO orders (user_id, user_name, phone, address, order_data, total_amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'новый', ?)
    ''', (user_id, user_name, phone, address, order_json, total, datetime.now()))
    conn.commit()
    conn.close()

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def start_message(message):
    save_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_order = types.KeyboardButton("🛍 Оформить заказ")
    btn_catalog = types.KeyboardButton("📸 Описание")
    btn_price = types.KeyboardButton("💰 Прайс-лист")
    btn_storage = types.KeyboardButton("❄️ Как хранить")
    btn_recipes = types.KeyboardButton("🍽 Рецепты")
    btn_manager = types.KeyboardButton("👤 Менеджер")
    btn_cart = types.KeyboardButton("🛒 Корзина")
    btn_promo = types.KeyboardButton("🎟 Промокод")
    markup.add(btn_order, btn_catalog, btn_price, btn_recipes, btn_storage, btn_manager, btn_cart, btn_promo)
    
    welcome_text = (
        f"🌸 Привет, {message.from_user.first_name}! 🌸\n\n"
        "🌿 Добро пожаловать в **RageGrown** — свежая микрозелень в Иваново!\n"
        "🌱 Мы выращиваем с душой и доставляем с любовью ❤️\n\n"
        f"🌐 Наш сайт: {SITE_URL}\n"
        f"👤 Менеджер: {MANAGER_LINK}\n\n"
        "👇 Нажми **🛍 Оформить заказ**, чтобы собрать корзину!\n"
        "🎁 Не забудь про промокоды!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

# --- СТАТИСТИКА ---
@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM orders WHERE status != 'отклонен'")
    orders_count, total_revenue = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'новый'")
    new_orders = cursor.fetchone()[0]
    conn.close()
    
    text = "📊 **СТАТИСТИКА БОТА** 📊\n\n"
    text += f"👥 Всего клиентов: {len(users)}\n"
    text += f"📦 Всего заказов: {orders_count or 0}\n"
    text += f"🆕 Новых заказов: {new_orders}\n"
    text += f"💰 Общая выручка: {total_revenue or 0} ₽\n"
    text += f"🌱 Товаров в каталоге: {len(catalog)}"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# --- РАССЫЛКА ---
@bot.message_handler(commands=['send'])
def send_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text_to_send = message.text[5:].strip()
    if not text_to_send:
        bot.send_message(message.chat.id, "❌ Пример: `/send Скидки 20%!`", parse_mode='Markdown')
        return
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        bot.send_message(message.chat.id, "❌ Нет подписчиков.")
        return
    count = 0
    for user_id in users:
        try:
            bot.send_message(user_id, f"📢 **НОВОСТИ ФЕРМЫ** 🌿\n\n{text_to_send}", parse_mode='Markdown')
            count += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ Отправлено: {count} людям! 🎉")

# --- ПРОМОКОД ---
@bot.message_handler(func=lambda message: message.text == "🎟 Промокод" or message.text == "/promo")
def ask_promo(message):
    msg = bot.send_message(message.chat.id, "🎟 Введите промокод:")
    bot.register_next_step_handler(msg, apply_promo)

def apply_promo(message):
    promo = message.text.upper().strip()
    if promo in promocodes:
        discount = promocodes[promo]
        bot.send_message(message.chat.id, f"✅ Промокод активирован! 🎉 Скидка {discount}%")
        user_discount[message.chat.id] = discount
    else:
        bot.send_message(message.chat.id, "❌ Неверный промокод. Попробуйте еще раз.")

# --- ПРАЙС-ЛИСТ ---
@bot.message_handler(func=lambda message: message.text == "💰 Прайс-лист")
def price_list(message):
    save_user(message.chat.id)
    text = "🌱 **НАШ ПРАЙС-ЛИСТ** 🌱\n\n"
    text += "🎁 **ВЫГОДНЫЕ НАБОРЫ:**\n"
    text += "▫️ **📦 НАБОР НОВИЧКА — 400 ₽**\n"
    text += "   ✅ Горошек (сладкий)\n"
    text += "   ✅ Подсолнечник (семечки)\n"
    text += "   ✅ Редис (слабоострый)\n"
    text += "   💡 *Идеальный старт! 3 лотка по цене 2-х.*\n\n"
    text += "▫️ **🥗 НАБОР САЛАТНЫЙ — 420 ₽**\n"
    text += "   🌿 Руккола (ореховая)\n"
    text += "   🌿 Мизуна (нежная)\n"
    text += "   🌿 Горчица (пикантная)\n"
    text += "   💡 *Супер добавка к любому салату.*\n\n"
    text += "🥗 **ПОШТУЧНО:**\n"
    for name, data in catalog.items():
        if "НАБОР" not in name:
            text += f"▫️ {name} — {data['price']} ₽\n"
    text += "\n🚚 **Доставка:** 250 ₽ (от 1500 ₽ — бесплатно)\n"
    text += "🎟 Промокоды дают скидку до 15%!\n\n"
    text += "👉 Нажми **📸 Описание**, чтобы узнать вкус каждой культуры"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# --- КОРЗИНА ---
@bot.message_handler(func=lambda message: message.text == "🛒 Корзина")
def show_cart(message):
    cart = user_orders.get(message.chat.id, [])
    if not cart:
        bot.send_message(message.chat.id, "🛒 Корзина пуста 😕\n\nДобавьте товары через **🛍 Оформить заказ**")
        return
    text = "🛒 **Ваша корзина:** 🛒\n\n"
    total = 0
    for i, item in enumerate(cart, 1):
        text += f"{i}. {item['product']} x{item['quantity']} = {item['total']} ₽\n"
        total += item['total']
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i, item in enumerate(cart):
        btn = types.InlineKeyboardButton(
            f"❌ Удалить",
            callback_data=f"remove_{i}"
        )
        markup.add(btn)
    btn_clear = types.InlineKeyboardButton("🗑 Очистить всё", callback_data="clear_cart")
    btn_checkout = types.InlineKeyboardButton("✅ Оформить", callback_data="checkout_from_cart")
    markup.add(btn_clear, btn_checkout)
    text += f"\n💰 **Итого: {total} ₽**"
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

# --- ЗАКАЗ ---
@bot.message_handler(func=lambda message: message.text == "🛍 Оформить заказ")
def start_order(message):
    user_orders[message.chat.id] = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    for item in catalog.keys():
        buttons.append(types.KeyboardButton(item))
    markup.add(*buttons)
    markup.add(types.KeyboardButton("❌ Отмена"))
    msg = bot.send_message(message.chat.id, "🛒 **Режим заказа** 🛒\n\nВыбери, что добавить в корзину:", reply_markup=markup, parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_product_step)

def process_product_step(message):
    if message.text == "❌ Отмена":
        start_message(message)
        return
    product_name = message.text
    if product_name not in catalog:
        msg = bot.send_message(message.chat.id, "❌ Выбери кнопку из меню.")
        bot.register_next_step_handler(msg, process_product_step)
        return
    item_data = catalog[product_name]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    buttons = []
    for i in range(1, 21):
        buttons.append(types.KeyboardButton(str(i)))
    markup.add(*buttons)
    markup.add(types.KeyboardButton("❌ Отмена"))

    if "НАБОР" in product_name:
        description = f"🍱 **{product_name}**\n💰 **Цена:** {item_data['price']} ₽\n\n"
        description += "📦 **В состав набора входит:**\n"
        if product_name == "📦 НАБОР НОВИЧКА":
            description += "✅ Горошек (сладкий)\n"
            description += "✅ Подсолнечник (семечки)\n"
            description += "✅ Редис (слабоострый)\n"
            description += "\n💡 *Идеальный старт! 3 лотка по цене 2-х.*\n"
        elif product_name == "🥗 НАБОР САЛАТНЫЙ":
            description += "🌿 Руккола (ореховая)\n"
            description += "🌿 Мизуна (нежная)\n"
            description += "🌿 Горчица (пикантная)\n"
            description += "\n💡 *Супер добавка к любому салату.*\n"
        description += f"\n👇 **Сколько штук добавить в корзину?**"
        msg = bot.send_message(message.chat.id, description, reply_markup=markup, parse_mode='Markdown')
    else:
        caption_text = (f"🍱 **{product_name}**\n"
                        f"💰 **Цена:** {item_data['price']} ₽\n\n"
                        f"👇 **Сколько штук добавить в корзину?**")
        
        if product_name in image_filenames:
            try:
                photo_path = get_photo_path(image_filenames[product_name])
                if os.path.exists(photo_path):
                    with open(photo_path, 'rb') as photo:
                        msg = bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=markup, parse_mode='Markdown')
                else:
                    msg = bot.send_message(message.chat.id, caption_text, reply_markup=markup, parse_mode='Markdown')
            except Exception as e:
                print(f"Ошибка с фото: {e}")
                msg = bot.send_message(message.chat.id, caption_text, reply_markup=markup, parse_mode='Markdown')
        else:
            msg = bot.send_message(message.chat.id, caption_text, reply_markup=markup, parse_mode='Markdown')
            
    bot.register_next_step_handler(msg, process_quantity_step, product_name)

def process_quantity_step(message, product_name):
    if message.text == "❌ Отмена":
        start_message(message)
        return
    try:
        quantity = int(message.text)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Выбери число.")
        bot.register_next_step_handler(msg, process_quantity_step, product_name)
        return
    
    price = catalog[product_name]['price']
    total_price = price * quantity
    user_orders[message.chat.id].append({
        "product": product_name,
        "quantity": quantity,
        "total": total_price
    })
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_yes = types.KeyboardButton("✅ Да, добавить еще")
    btn_no = types.KeyboardButton("🚖 Нет, оформить заказ")
    markup.add(btn_yes, btn_no)
    msg = bot.send_message(message.chat.id, f"✅ Добавил: {product_name} ({quantity} шт.) 🎉\n\nЧто-то еще?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_continue_step)

def process_continue_step(message):
    if message.text == "✅ Да, добавить еще":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for item in catalog.keys():
            buttons.append(types.KeyboardButton(item))
        markup.add(*buttons)
        markup.add(types.KeyboardButton("❌ Отмена"))
        msg = bot.send_message(message.chat.id, "🛒 Выбирай следующую культуру:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_product_step)
    elif message.text == "🚖 Нет, оформить заказ":
        msg = bot.send_message(message.chat.id, "📞 Введите ваш номер телефона 📞\n\nНапример: +79991234567", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_phone_step)
    else:
        msg = bot.send_message(message.chat.id, "❌ Нажми Да или Нет.")
        bot.register_next_step_handler(msg, process_continue_step)

def process_phone_step(message):
    phone = message.text
    if not validate_phone(phone):
        msg = bot.send_message(message.chat.id, "❌ Неверный формат. Введите номер как +79991234567 или 89991234567")
        bot.register_next_step_handler(msg, process_phone_step)
        return
    msg = bot.send_message(message.chat.id, "📍 Введите адрес доставки 📍\n\nУкажите улицу, дом, квартиру:")
    bot.register_next_step_handler(msg, process_address_step, phone)

def process_address_step(message, phone):
    address = message.text
    finish_order(message, phone, address)

def finish_order(message, phone, address):
    cart = user_orders.get(message.chat.id, [])
    if not cart:
        bot.send_message(message.chat.id, "🛒 Корзина пуста.")
        start_message(message)
        return
    
    text = "📋 **Проверьте заказ:** 📋\n\n"
    final_sum = 0
    total_items = 0
    for item in cart:
        text += f"🌱 {item['product']} x {item['quantity']} шт = {item['total']} ₽\n"
        final_sum += item['total']
        total_items += item['quantity']
    
    discount = user_discount.get(message.chat.id, 0)
    if discount > 0:
        discount_amount = final_sum * discount // 100
        final_sum -= discount_amount
        text += f"🎟 Скидка {discount}%: -{discount_amount} ₽\n"
    
    delivery_cost = 250
    if final_sum >= 1500:
        delivery_cost = 0
        delivery_text = "БЕСПЛАТНО 🎉"
    else:
        delivery_text = f"{delivery_cost} ₽"
    
    gift_text = ""
    if total_items >= 10:
        gifts = total_items // 10
        gift_text = f"\n🎁 Подарков: {gifts} шт."
    
    total_with_delivery = final_sum + delivery_cost
    text += f"\n💳 Товары: {final_sum} ₽{gift_text}"
    text += f"\n🚚 Доставка: {delivery_text}"
    text += f"\n💰 **ИТОГО: {total_with_delivery} ₽**"
    text += f"\n📞 Телефон: {phone}"
    text += f"\n📍 Адрес: {address}"
    text += "\n\n✅ **Всё верно?**"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_yes = types.InlineKeyboardButton("✅ Да, отправить", callback_data="confirm_order")
    btn_no = types.InlineKeyboardButton("✏️ Редактировать", callback_data="edit_order")
    markup.add(btn_yes, btn_no)
    
    temp_order_data[message.chat.id] = {
        'phone': phone,
        'address': address,
        'total': total_with_delivery,
        'cart': cart,
        'discount': discount
    }
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

# --- ОБРАБОТКА КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data == "confirm_order":
            chat_id = call.message.chat.id
            order_data = temp_order_data.get(chat_id)
            cart = user_orders.get(chat_id, [])
            if not order_data or not cart:
                bot.answer_callback_query(call.id, "❌ Ошибка: заказ не найден")
                return
            
            save_order_to_db(chat_id, call.message.chat.first_name, order_data['phone'], order_data['address'], cart, order_data['total'])
            
            text_client = "✅ **Ваш заказ отправлен!** ✅\n\n"
            for item in cart:
                text_client += f"🌱 {item['product']} x {item['quantity']} шт = {item['total']} ₽\n"
            text_client += f"\n💰 Итого: {order_data['total']} ₽"
            if order_data.get('discount', 0) > 0:
                text_client += f"\n🎟 Скидка: {order_data['discount']}%"
            text_client += "\n\n⏳ Ждите звонка менеджера... 📞"
            bot.send_message(chat_id, text_client, parse_mode='Markdown')
            
            text_admin = f"🔔 **НОВЫЙ ЗАКАЗ!** 🔔\n\n"
            text_admin += f"👤 Клиент: {call.message.chat.first_name}\n"
            if call.message.chat.username:
                text_admin += f"📱 Username: @{call.message.chat.username}\n"
            text_admin += f"📞 Телефон: {order_data['phone']}\n"
            text_admin += f"📍 Адрес: {order_data['address']}\n\n"
            text_admin += "📦 **Состав заказа:**\n"
            for item in cart:
                text_admin += f"  🌱 {item['product']} x {item['quantity']} шт = {item['total']} ₽\n"
            text_admin += f"\n💰 **ИТОГО: {order_data['total']} ₽**"
            if order_data.get('discount', 0) > 0:
                text_admin += f"\n🎟 Скидка: {order_data['discount']}%"
            text_admin += f"\n🕐 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            markup_admin = types.InlineKeyboardMarkup(row_width=2)
            btn_accept = types.InlineKeyboardButton("✅ Принять заказ", callback_data=f"accept_{chat_id}")
            btn_decline = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_{chat_id}")
            btn_info = types.InlineKeyboardButton("📞 Связаться", url=f"tg://user?id={chat_id}")
            markup_admin.add(btn_accept, btn_decline)
            markup_admin.add(btn_info)
            
            bot.send_message(ADMIN_ID, text_admin, reply_markup=markup_admin, parse_mode='Markdown')
            
            user_orders[chat_id] = []
            temp_order_data.pop(chat_id, None)
            user_discount.pop(chat_id, None)
            bot.edit_message_text("✅ Заказ подтвержден! Спасибо! 🌿", chat_id, call.message.message_id)
            
        elif call.data == "edit_order":
            bot.edit_message_text("✏️ Редактирование отменено. Начните заказ заново.",
                                  call.message.chat.id, call.message.message_id)
            start_message(call.message)
            
        elif call.data.startswith("remove_"):
            index = int(call.data.split("_")[1])
            chat_id = call.message.chat.id
            if chat_id in user_orders and 0 <= index < len(user_orders[chat_id]):
                removed = user_orders[chat_id].pop(index)
                bot.answer_callback_query(call.id, f"❌ Удален: {removed['product']}")
                show_cart(call.message)
                
        elif call.data == "clear_cart":
            chat_id = call.message.chat.id
            user_orders[chat_id] = []
            bot.answer_callback_query(call.id, "🗑 Корзина очищена")
            bot.edit_message_text("🛒 Корзина пуста", call.message.chat.id, call.message.message_id)
            
        elif call.data == "checkout_from_cart":
            msg = bot.send_message(call.message.chat.id, "📞 Введите номер телефона:", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_phone_step)
            
        elif call.data.startswith("accept_"):
            client_id = int(call.data.split("_")[1])
            bot.send_message(client_id, "🎉 **Ваш заказ ПРИНЯТ!** 🎉\n\nМенеджер свяжется с вами в ближайшее время. 🚚")
            bot.send_message(client_id, 
                "🌱 *RageGrown* — свежая микрозелень в Иваново\n\n"
                "🌐 Наш сайт: http://микрозеленьиваново.рф/\n"
                "👤 Менеджер: @RageGrown\n\n"
                "⭐ Если всё понравилось — оставьте отзыв, это очень важно для нас!\n"
                "https://yandex.ru/profile/-/CPbqfD9O",
                parse_mode='Markdown')
            new_text = call.message.text + "\n\n✅ **СТАТУС: ПРИНЯТ** ✅"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text, reply_markup=None)
            bot.answer_callback_query(call.id, "✅ Заказ принят!")
            
        elif call.data.startswith("decline_"):
            client_id = int(call.data.split("_")[1])
            bot.send_message(client_id, "❌ **Ваш заказ ОТКЛОНЕН.** ❌\n\nСвяжитесь с менеджером для уточнения деталей: @RageGrown")
            new_text = call.message.text + "\n\n❌ **СТАТУС: ОТКЛОНЕН** ❌"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text, reply_markup=None)
            bot.answer_callback_query(call.id, "❌ Заказ отклонен")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.answer_callback_query(call.id, f"❌ Ошибка")

# --- ОСТАЛЬНЫЕ КНОПКИ МЕНЮ ---
@bot.message_handler(func=lambda message: message.text == "📸 Описание")
def show_catalog_menu(message):
    save_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    for item in catalog.keys():
        buttons.append(types.KeyboardButton(f"📖 {item}"))
    markup.add(*buttons)
    markup.add(types.KeyboardButton("🔙 В главное меню"))
    bot.send_message(message.chat.id, "🌿 **Выберите культуру** 🌿\n\nНажми на название, чтобы узнать подробности:", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "❄️ Как хранить")
def storage_info(message):
    save_user(message.chat.id)
    text = ("❄️ **Как правильно хранить микрозелень?** ❄️\n\n"
            "1️⃣ **Где?**\nТолько в холодильнике! (Оптимально +2..+6°C)\n\n"
            "2️⃣ **В чем?**\nВ закрытом контейнере, чтобы зелень не вяла от сухого воздуха\n\n"
            "3️⃣ **Как долго?**\nСрезанная зелень живет 5-7 дней. В лотке (растущая) — до 14 дней\n\n"
            "🚿 **Надо ли мыть?**\nМы выращиваем без земли, поэтому зелень чистая. Но перед едой рекомендуем слегка ополоснуть.\n\n"
            "💡 **Совет:** Не храните зелень рядом с фруктами — они выделяют газ, ускоряющий порчу!")
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🍽 Рецепты")
def recipes_info(message):
    save_user(message.chat.id)
    text = ("🍽 **Вкусные идеи с микрозеленью** 🍽\n\n"
            "🥪 **Тост с авокадо:**\n"
            "Хлеб + Творожный сыр + Авокадо + **Микрозелень Редиса**\n\n"
            "🍳 **Утренний омлет:**\n"
            "Яйца + Помидоры + Сверху посыпать **Горошком**\n\n"
            "🥗 **Летний салат:**\n"
            "Огурцы + Редис + Сметана + **Руккола и Горчица**\n\n"
            "🥤 **Витаминный смузи:**\n"
            "Банан + Яблоко + Вода + **Подсолнечник**\n\n"
            "🍜 **Азиатский суп:**\n"
            "Лапша + Бульон + Овощи + **Ростки маша**")
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "👤 Менеджер")
def manager_contact(message):
    save_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("💬 Написать менеджеру", url=MANAGER_LINK)
    btn_site = types.InlineKeyboardButton("🌐 Наш сайт", url=SITE_URL)
    btn_review = types.InlineKeyboardButton("⭐ Оставить отзыв", url=REVIEW_LINK)
    markup.add(btn)
    markup.add(btn_site, btn_review)
    bot.send_message(message.chat.id, "👤 **Связь с нами** 👤\n\nМы на связи с 9:00 до 21:00!", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🔙 В главное меню")
def back_to_main(message):
    start_message(message)

# --- ОПИСАНИЕ С ФОТО ---
@bot.message_handler(func=lambda message: message.text.startswith("📖 "))
def show_description(message):
    save_user(message.chat.id)
    product_name = message.text[2:]
    if product_name in catalog:
        item = catalog[product_name]
        description = (f"🌱 **{product_name}**\n\n"
                       f"📝 **Описание:**\n{item['taste']}\n\n"
                       f"💰 **Цена:** {item['price']} ₽")
        if product_name in image_filenames:
            try:
                photo_path = get_photo_path(image_filenames[product_name])
                if os.path.exists(photo_path):
                    with open(photo_path, 'rb') as photo:
                        bot.send_photo(message.chat.id, photo, caption=description, parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, description, parse_mode='Markdown')
            except Exception as e:
                print(f"Ошибка с фото: {e}")
                bot.send_message(message.chat.id, description, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, description, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ Культура не найдена")

@bot.message_handler(func=lambda message: True)
def handle_other_text(message):
    save_user(message.chat.id)
    bot.send_message(message.chat.id, "🤔 Используйте кнопки меню 👇")

# --- ЗАПУСК БОТА ---
if __name__ == '__main__':
    print("🌿 БОТ ЗАПУЩЕН! 🌿")
    print(f"👤 ID администратора: {ADMIN_ID}")
    print(f"📦 Товаров в каталоге: {len(catalog)}")
    print(f"📁 Папка с ботом: {BASE_DIR}")
    
    photos_count = 0
    for name, filename in image_filenames.items():
        photo_path = get_photo_path(filename)
        if os.path.exists(photo_path):
            photos_count += 1
            print(f"✅ {filename} - найдено")
        else:
            print(f"❌ {filename} - НЕТ")
    
    print(f"📸 Всего фото: {photos_count} из {len(image_filenames)}")
    print("🤖 Бот готов к работе!")
    
    bot.infinity_polling()
