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

from checker import check_transfers
from contract import *

API_TOKEN = "6500720809:AAEvo7PhRABBy9BYShF3w-snSId0V5k60-Y"
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

OUR_CONTRACT = ""
OUR_TOKEN = ""
OUR_ADDRESS = ""
SEPOLIA_URL = ""
API_KEY = ""
PRIVATE_KEY = ""

user_data = {}


class OrderState(StatesGroup):
    customer_wallet = State()
    order_conditions = State()
    order_proofs = State()
    token_address = State()
    token_amount = State()
    start_date = State()
    end_date = State()


class DealState(StatesGroup):
    order_id = State()
    executor_wallet = State()


class DepositStates(StatesGroup):
    order_id = State()


def validate_date(date_text: str) -> bool:
    try:
        datetime.strptime(date_text, "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        return False


@dp.message(CommandStart())
async def start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Создать сделку"), types.KeyboardButton(text="Присоединиться к сделке"), types.KeyboardButton(text="Внести депозит в договор")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите действие")
    await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.message(F.text.lower() == "внести депозит в договор")
async def deposit_order(message: types.Message, state: FSMContext):
    await message.answer("Введите ID договора:")
    await state.set_state(DepositStates.order_id)

@dp.message(F.text.lower() == "обновить баланс")
async def refresh_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    contract_id = data["order_id"]
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://127.0.0.1:8000/order/{contract_id}", timeout=10) as response:
            if response.status == 200:
                data_response = await response.json()

                token_amount = data_response['token_amount']
                customer_wallet = data_response['customer_wallet']
                token_address = data_response['token_address']
                
                if token_amount == await check_transfers(API_KEY, customer_wallet, OUR_ADDRESS, token_address):
                    await message.answer("Баланс обновлен. Закидываю деньги в контракт.")
                    contract = ContractInteraction(OUR_ADDRESS, PRIVATE_KEY, OUR_CONTRACT, SEPOLIA_URL)
                    receipt = contract.createDeal(contract_id, 
                                                customer_wallet, "0x43d175438720C1f5D58f1465C1CD35b6F4d00Fc9", 
                                                token_address, token_amount * 10 ** 18)
                    tx_link = f"https://sepolia.etherscan.io/tx/{receipt}"
                    await message.answer(f'Ссылка на транзакцию: \n {tx_link}')
                else:
                    print(await check_transfers(SEPOLIA_URL, customer_wallet, OUR_ADDRESS, token_address))
                    await message.answer("Баланс не обновлен. Подождите и повторите попытку заново.")
            else:
                await message.answer("Произошла ошибка при обновлении данных. Пожалуйста, попробуйте снова.")

@dp.message(DepositStates.order_id)
async def process_contract_id(message: types.Message, state: FSMContext):
    contract_id = message.text

    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://127.0.0.1:8000/order/{contract_id}", timeout=10) as response:
            if response.status == 200:
                data_response = await response.json()
                await state.update_data(order_id=contract_id, data_response=data_response)
                await message.answer(f"Нужно внести депозит {data_response['token_amount']}")

                refresh_button = [[types.KeyboardButton(text="Обновить баланс")]]
                keyboard = types.ReplyKeyboardMarkup(keyboard=refresh_button, resize_keyboard=True, input_field_placeholder="Выберите действие")
                await message.answer("Выберите действие:", reply_markup=keyboard)
            else:
                await message.answer("Произошла ошибка при получении данных о договоре. Пожалуйста, попробуйте снова.")

@dp.message(F.text.lower() == "присоединиться к сделке")
async def join_deal(message: types.Message, state: FSMContext):
    await message.answer("Введите ID сделки:")
    await state.set_state(DealState.order_id)

@dp.message(DealState.order_id)
async def process_order_id(message: types.Message, state: FSMContext):
    await state.update_data(order_id=message.text)
    await message.answer("Введите адрес своего кошелька:")
    await state.set_state(DealState.executor_wallet)

@dp.message(DealState.executor_wallet)
async def process_executor_wallet(message: types.Message, state: FSMContext):
    # Формирование сделки
    user_id = message.from_user.id
    user_data = await state.get_data()
    deal_info = {
        "order_id": user_data["order_id"],
        "executor_id": user_id,
        "executor_wallet": message.text,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("http://127.0.0.1:8000/register_deal", json=deal_info, timeout=10) as response:
            if response.status == 201:
                data_response = await response.text()
                await message.answer(f"Договор успешно подписан:\n{data_response}")
            else:
                await message.answer("Произошла ошибка при создании сделки.")
    # response = requests.post("http://127.0.0.1:8000/register_deal", json=deal_info, timeout=10)

        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://127.0.0.1:8000/order/{user_data['order_id']}", timeout=10) as response:
                if response.status == 200:
                    data_response = await response.json()
                    await bot.send_message(data_response["customer_id"], "Вашу сделку подтвердил исполнитель.")
                    await message.answer(f"Оповестили заказчика об подтверждении сделки.")
                else:
                    print("Произошла ошибка при опповещении заказчика.")

    await state.clear()


@dp.message(F.text.lower() == "создать сделку")
async def create_order(message: types.Message, state: FSMContext):
    await message.answer("Введите адрес своего кошелька:")
    await state.set_state(OrderState.customer_wallet)

@dp.message(OrderState.customer_wallet)
async def process_order_c_wallet(message: types.Message, state: FSMContext):
    await state.update_data(customer_wallet=message.text)
    await message.answer("Введите условия сделки:")
    await state.set_state(OrderState.order_conditions)

@dp.message(OrderState.order_conditions)
async def process_order_conditions(message: types.Message, state: FSMContext):
    await state.update_data(order_conditions=message.text)
    await message.answer("Введите доказательства успешного завершения сделки:")
    await state.set_state(OrderState.order_proofs)


@dp.message(OrderState.order_proofs)
async def process_order_proofs(message: types.Message, state: FSMContext):
    await state.update_data(order_proofs=message.text)
    await message.answer("Введите адрес токена:")
    await state.set_state(OrderState.token_address)

@dp.message(OrderState.token_address)
async def process_token_address(message: types.Message, state: FSMContext):
    await state.update_data(token_address=message.text)
    await message.answer("Введите количество токенов:")
    await state.set_state(OrderState.token_amount)

@dp.message(OrderState.token_amount)
async def process_token_amount(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data["token_address"] == OUR_TOKEN:
        await state.update_data(token_amount=float(message.text) + float(message.text) * 0.03)
    else:
        await state.update_data(token_amount=float(message.text) + float(message.text) * 0.05)
    await message.answer("Введите дату начала сделки (в формате ДД.ММ.ГГГГ Ч:М):")
    await state.set_state(OrderState.start_date)

@dp.message(OrderState.start_date)
async def process_order_start_date(message: types.Message, state: FSMContext):
    start_date = message.text
    if not validate_date(start_date):
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ Ч:М")
        return
    await state.update_data(start_date=message.text)
    await message.answer("Введите дату завершения сделки (в формате ДД.ММ.ГГГГ Ч:М):")
    await state.set_state(OrderState.end_date)

@dp.message(OrderState.end_date)
async def process_order_end_date(message: types.Message, state: FSMContext):
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
    order_info = {
        "customer_id": user_id,
        "customer_wallet": user_data["customer_wallet"],
        "deal_conditions": user_data["order_conditions"],
        "token_address": user_data["token_address"],
        "token_amount": user_data["token_amount"],
        "start_date": user_data["start_date"],
        "end_date": end_date,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("http://127.0.0.1:8000/register_order", json=order_info, timeout=10) as response:
            if response.status == 201:
                data_response = await response.text()
                await message.answer(f"Сделка успешно создана:\n{data_response}")
            else:
                await message.answer("Произошла ошибка при создании сделки.")
    # response = requests.post("http://127.0.0.1:8000/register_order", json=order_info, timeout=10)

    await state.clear()


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
