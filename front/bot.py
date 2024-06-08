import uuid
import requests
from datetime import datetime
import telebot
from telebot import types

bot = telebot.TeleBot("YOUR_BOT_TOKEN")

user_data = {}

def validate_date(date_text: str) -> bool:
    try:
        datetime.strptime(date_text, '%H-%D-%M-%Y')
        return True
    except ValueError:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Создать сделку", callback_data="create_deal"))
    markup.add(types.InlineKeyboardButton("Присоединиться к сделке", callback_data="join_deal"))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "create_deal":
        user_data[call.from_user.id] = {}
        bot.send_message(call.message.chat.id, "Введите адрес своего кошелька:")
        bot.register_next_step_handler(call.message, process_deal_c_wallet)
    elif call.data == "join_deal":
        bot.send_message(call.message.chat.id, "Введите ID сделки:")
        bot.register_next_step_handler(call.message, process_deal_id)
    elif call.data == "accept_deal":
        bot.send_message(call.message.chat.id, "Введите адрес своего кошелька:")
        bot.register_next_step_handler(call.message, process_deal_id)

def process_deal_c_wallet(message):
    user_data[message.from_user.id]['customer_wallet'] = message.text
    bot.send_message(message.chat.id, "Введите условия сделки:")
    bot.register_next_step_handler(message, process_deal_proofs)

def process_deal_conditions(message):
    user_data[message.from_user.id]['deal_conditions'] = message.text
    bot.send_message(message.chat.id, "Введите доказательства успешного завершения сделки:")
    bot.register_next_step_handler(message, process_deal_proofs)

def process_deal_proofs(message):
    user_data[message.from_user.id]['deal_proofs'] = message.text
    bot.send_message(message.chat.id, "Введите адрес токена:")
    bot.register_next_step_handler(message, process_deal_address)

def process_deal_address(message):
    user_data[message.from_user.id]['deal_address'] = message.text
    bot.send_message(message.chat.id, "Введите количество токенов:")
    bot.register_next_step_handler(message, process_deal_amount)

def process_deal_amount(message):
    user_data[message.from_user.id]['deal_amount'] = message.text
    bot.send_message(message.chat.id, "Введите дату начала сделки (в формате ГГГГ-ММ-ДД):")
    bot.register_next_step_handler(message, process_deal_start_date)

def process_deal_start_date(message):
    start_date = message.text
    if not validate_date(start_date):
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД:")
        bot.register_next_step_handler(message, process_deal_start_date)
    else:
        user_data[message.from_user.id]['deal_start_date'] = start_date
        bot.send_message(message.chat.id, "Введите дату завершения сделки (в формате ГГГГ-ММ-ДД):")
        bot.register_next_step_handler(message, process_deal_end_date)

def process_deal_end_date(message):
    end_date = message.text
    if not validate_date(end_date):
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД:")
        bot.register_next_step_handler(message, process_deal_end_date)
    else:
        start_date = user_data[message.from_user.id]['deal_start_date']
        if end_date < start_date:
            bot.send_message(message.chat.id, "Дата завершения сделки не может быть раньше даты начала. Пожалуйста, введите корректную дату завершения:")
            bot.register_next_step_handler(message, process_deal_end_date)
        else:
            user_data[message.from_user.id]['deal_end_date'] = end_date
            complete_customer_deal_creation(message)

def complete_customer_deal_creation(message):
    user_id = message.from_user.id
    deal_info = {
        "deal_id": str(uuid.uuid4()),
        "user_id": message.from_user.id,
        "customer_wallet": user_data[user_id]['customer_wallet'],
        "deal_conditions": user_data[user_id]['deal_conditions'],
        "deal_address": user_data[user_id]['deal_address'],
        "deal_amount": user_data[user_id]['deal_amount'],
        "deal_start_date": user_data[user_id]['deal_start_date'],
        "deal_end_date": user_data[user_id]['deal_end_date'],
    }

    response = requests.post('http://localhost:8000/...', json=deal_info)

    if response.status_code == 200:
        bot.send_message(message.chat.id, f'Сделка создана:\n{deal_info}')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка при создании сделки.')

def process_deal_id(message):
    deal_id = message.text
    response = requests.get(f'http://localhost:8000/.../{deal_id}')
    
    if response.status_code == 200:
        deal_info = response.json()
        bot.send_message(message.chat.id, f'Информация о сделке:\n{deal_info}')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Подтвердить условия сделки", callback_data="accept_deal"))
        markup.add(types.InlineKeyboardButton("Отменить сделку", callback_data="deny_deal"))
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Сделка с таким ID не найдена.')

def process_deal_e_wallet(message):
    user_data[message.from_user.id]['executor_wallet'] = message.text
    bot.register_next_step_handler(message, process_deal_proofs)
    complete_executor_deal_creation(message)

def complete_executor_deal_creation(message):
    user_id = message.from_user.id
    deal_info = {
        "user_id": message.from_user.id,
        "executor_wallet": user_data[user_id]['customer_wallet']
    }

    response = requests.post('http://localhost:8000/...', json=deal_info)

    if response.status_code == 200:
        bot.send_message(message.chat.id, f'Сделка создана:\n{deal_info}')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка при создании сделки.')

if __name__ == "__main__":
    bot.polling(none_stop=True)
