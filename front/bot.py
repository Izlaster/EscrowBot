import asyncio
import logging
import sys
import uuid
from datetime import datetime

import aiohttp
import requests
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "6140886246:AAGrNXZRfvnZ8Km80wNM6f1Nnnp3zcOkw2I"

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

OUR_TOKEN = ""

user_data = {}


class DealState(StatesGroup):
    customer_wallet = State()
    deal_conditions = State()
    deal_proofs = State()
    token_address = State()
    token_amount = State()
    start_date = State()
    end_date = State()
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
    await state.set_state(DealState.customer_wallet)


@dp.message(F.text.lower() == "join_deal")
async def join_deal(message: types.Message):
    await message.answer("Введите ID сделки:")
    await DealState.waiting_for_deal_id.set()


@dp.message(F.text.lower() == "accept_deal")
async def accept_deal(message: types.Message):
    await message.answer("Введите адрес своего кошелька:")
    await DealState.waiting_for_executor_wallet.set()


@dp.message(DealState.customer_wallet)
async def process_deal_c_wallet(message: types.Message, state: FSMContext):
    await state.update_data(customer_wallet=message.text)
    await message.answer("Введите условия сделки:")
    await state.set_state(DealState.deal_conditions)


@dp.message(DealState.deal_conditions)
async def process_deal_conditions(message: types.Message, state: FSMContext):
    await state.update_data(deal_conditions=message.text)
    await message.answer("Введите доказательства успешного завершения сделки:")
    await state.set_state(DealState.deal_proofs)


@dp.message(DealState.deal_proofs)
async def process_deal_proofs(message: types.Message, state: FSMContext):
    await state.update_data(deal_proofs=message.text)
    await message.answer("Введите адрес токена:")
    await state.set_state(DealState.token_address)


@dp.message(DealState.token_address)
async def process_token_address(message: types.Message, state: FSMContext):
    await state.update_data(token_address=message.text)
    await message.answer("Введите количество токенов:")
    await state.set_state(DealState.token_amount)


@dp.message(DealState.token_amount)
async def process_token_amount(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data["token_address"] == OUR_TOKEN:
        await state.update_data(token_amount=float(message.text) + float(message.text) * 0.03)
    else:
        await state.update_data(token_amount=float(message.text) + float(message.text) * 0.05)
    await message.answer("Введите дату начала сделки (в формате ДД.ММ.ГГГГ Ч:М):")
    await state.set_state(DealState.start_date)


@dp.message(DealState.start_date)
async def process_deal_start_date(message: types.Message, state: FSMContext):
    start_date = message.text
    if not validate_date(start_date):
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ Ч:М")
        return
    await state.update_data(start_date=message.text)
    await message.answer("Введите дату завершения сделки (в формате ДД.ММ.ГГГГ Ч:М):")
    await state.set_state(DealState.end_date)


@dp.message(DealState.end_date)
async def process_deal_end_date(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    end_date = message.text
    if not validate_date(end_date):
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ Ч:М")
        return
    start_date = user_data["start_date"]
    if end_date < start_date:
        await message.answer(
            "Дата завершения сделки не может быть раньше даты начала. Пожалуйста, введите корректную дату завершения:"
        )
        return

    # Формирование сделки
    user_id = message.from_user.id
    deal_info = {
        "customer_id": user_id,
        "customer_wallet": user_data["customer_wallet"],
        "deal_conditions": user_data["deal_conditions"],
        "token_address": user_data["token_address"],
        "token_amount": user_data["token_amount"],
        "start_date": user_data["start_date"],
        "end_date": end_date,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("http://127.0.0.1:8000/register_order", json=deal_info, timeout=10) as response:
            if response.status == 201:
                data_response = await response.text()
                await message.answer(f"Сделка успешно создана:\n{data_response}")
            else:
                await message.answer("Произошла ошибка при создании сделки.")
    # response = requests.post("http://127.0.0.1:8000/register_order", json=deal_info, timeout=10)

    await state.clear()


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
