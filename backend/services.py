from datetime import datetime

from db.repositories import deals_history_repository, deals_repository, orders_repository, user_repository
from schemas.schemas import BaseDeals, BaseOrders, Deals, GetOrders, Orders, User, WalletsTokens


class UserService:
    @staticmethod
    async def create(data: User):
        return await user_repository.create(**data.model_dump())

    @staticmethod
    async def get_user(tg_id: int):
        user = await user_repository.get_user(tg_id=tg_id)

        return user


class OrderService:
    @staticmethod
    async def create(data: BaseOrders) -> Orders:
        date_format = "%d.%m.%Y %H:%M"
        data.start_date = datetime.strptime(data.start_date, date_format)
        data.end_date = datetime.strptime(data.end_date, date_format)

        return await orders_repository.create(**data.model_dump())

    @staticmethod
    async def get_order(**filters):
        order = await orders_repository.get_order(**filters)

        return GetOrders.model_validate(order)

    @staticmethod
    async def get_orders(**filters):
        orders = await orders_repository.get_orders(**filters)

        return [GetOrders.model_dump(order) for order in orders]

    @staticmethod
    async def get_order_with_deal_wallets_token(**filters) -> WalletsTokens:
        order_with_deal_data = await orders_repository.get_order_with_deal_wallets_token(**filters)
        if order_with_deal_data:
            order_with_deal = WalletsTokens(**order_with_deal_data)
            return order_with_deal

        return None


class DealService:
    @staticmethod
    async def create(data: BaseDeals) -> Deals:
        return await deals_repository.create(**data.model_dump())
