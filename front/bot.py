import asyncio
import logging
import sys
import uuid
from datetime import datetime

import requests
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = ""

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

OUR_TOKEN = ""

user_data = {}


class DealState(StatesGroup):
    waiting_for_customer_wallet = State()
    waiting_for_deal_conditions = State()
    waiting_for_deal_proofs = State()
    waiting_for_token_address = State()
    waiting_for_token_amount = State()
    waiting_for_deal_start_date = State()
    waiting_for_deal_end_date = State()
    waiting_for_executor_wallet = State()
    waiting_for_deal_id = State()


def validate_date(date_text: str) -> bool:
    try:
        datetime.strptime(date_text, "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        return False


@dp.message(CommandStart())
async def start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Создать сделку"), types.KeyboardButton(text="Присоединиться к сделке")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите действие")
    await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.message(F.text.lower() == "создать сделку")
async def create_deal(message: types.Message, state: FSMContext):
    user_data[message.from_user.id] = {}
    await message.answer("Введите адрес своего кошелька:")
    await state.set_state(DealState.waiting_for_customer_wallet)


@dp.message(F.text.lower() == "join_deal")
async def join_deal(message: types.Message):
    await message.answer("Введите ID сделки:")
    await DealState.waiting_for_deal_id.set()


@dp.message(F.text.lower() == "accept_deal")
async def accept_deal(message: types.Message):
    await message.answer("Введите адрес своего кошелька:")
    await DealState.waiting_for_executor_wallet.set()


@dp.message(DealState.waiting_for_customer_wallet)
async def process_deal_c_wallet(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["customer_wallet"] = message.text
    await message.answer("Введите условия сделки:")
    await state.set_state(DealState.waiting_for_deal_conditions)


@dp.message(DealState.waiting_for_deal_conditions)
async def process_deal_conditions(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["deal_conditions"] = message.text
    await message.answer("Введите доказательства успешного завершения сделки:")
    await state.set_state(DealState.waiting_for_deal_proofs)


@dp.message(DealState.waiting_for_deal_proofs)
async def process_deal_proofs(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["deal_proofs"] = message.text
    await message.answer("Введите адрес токена:")
    await state.set_state(DealState.waiting_for_token_address)


@dp.message(DealState.waiting_for_token_address)
async def process_token_address(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["token_address"] = message.text
    await message.answer("Введите количество токенов:")
    await state.set_state(DealState.waiting_for_token_amount)


@dp.message(DealState.waiting_for_token_amount)
async def process_token_amount(message: types.Message, state: FSMContext):
    if user_data[message.from_user.id]["token_address"] == OUR_TOKEN:
        user_data[message.from_user.id]["token_amount"] = float(message.text) + float(message.text) * 0.03
    else:
        user_data[message.from_user.id]["token_amount"] = float(message.text) + float(message.text) * 0.05
    await message.answer("Введите дату начала сделки (в формате ДД.ММ.ГГГГ Ч:М):")
    await state.set_state(DealState.waiting_for_deal_start_date)


@dp.message(DealState.waiting_for_deal_start_date)
async def process_deal_start_date(message: types.Message, state: FSMContext):
    start_date = message.text
    if not validate_date(start_date):
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ Ч:М")
        return
    user_data[message.from_user.id]["deal_start_date"] = start_date
    await message.answer("Введите дату завершения сделки (в формате ДД.ММ.ГГГГ Ч:М):")
    await state.set_state(DealState.waiting_for_deal_end_date)


@dp.message(DealState.waiting_for_deal_end_date)
async def process_deal_end_date(message: types.Message, state: FSMContext):
    end_date = message.text
    if not validate_date(end_date):
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ Ч:М")
        return
    start_date = user_data[message.from_user.id]["deal_start_date"]
    if end_date < start_date:
        await message.answer(
            "Дата завершения сделки не может быть раньше даты начала. Пожалуйста, введите корректную дату завершения:"
        )
        return
    user_data[message.from_user.id]["deal_end_date"] = end_date
    await complete_customer_deal_creation(message)
    await state.finish()


async def complete_customer_deal_creation(message: types.Message):
    user_id = message.from_user.id
    deal_info = {
        "deal_id": str(uuid.uuid4()),
        "user_id": user_id,
        "customer_wallet": user_data[user_id]["customer_wallet"],
        "deal_conditions": user_data[user_id]["deal_conditions"],
        "token_address": user_data[user_id]["token_address"],
        "token_amount": user_data[user_id]["token_amount"],
        "deal_start_date": user_data[user_id]["deal_start_date"],
        "deal_end_date": user_data[user_id]["deal_end_date"],
    }

    response = requests.post("http://localhost:8000/...", json=deal_info)

    if response.status_code == 200:
        await message.answer(f"Сделка создана:\n{deal_info}")
    else:
        await message.answer("Произошла ошибка при создании сделки.")


@dp.message(DealState.waiting_for_deal_id)
async def process_deal_id(message: types.Message, state: FSMContext):
    deal_id = message.text
    response = requests.get(f"http://localhost:8000/.../{deal_id}")

    if response.status_code == 200:
        deal_info = response.json()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Подтвердить условия сделки", callback_data="accept_deal"))
        markup.add(types.InlineKeyboardButton("Отменить сделку", callback_data="deny_deal"))
        await message.answer(f"Информация о сделке:\n{deal_info}")
        await message.answer("Выберите действие:", reply_markup=markup)
    else:
        await message.answer("Сделка с таким ID не найдена.")
    await state.finish()


@dp.message(DealState.waiting_for_executor_wallet)
async def process_deal_e_wallet(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["executor_wallet"] = message.text
    await complete_executor_deal_creation(message)
    await state.finish()


async def complete_executor_deal_creation(message: types.Message):
    user_id = message.from_user.id
    deal_info = {
        "user_id": user_id,
        "executor_wallet": user_data[user_id]["executor_wallet"],
    }

    response = requests.post("http://localhost:8000/...", json=deal_info)

    if response.status_code == 200:
        await message.answer(f"Сделка подтверждена:\n{deal_info}")
    else:
        await message.answer("Произошла ошибка при подтверждении сделки.")


async def main() -> None:
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
