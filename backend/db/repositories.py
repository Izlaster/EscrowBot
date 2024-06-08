from collections.abc import Callable, Sequence
from contextlib import _AsyncGeneratorContextManager
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .connections import db_helper
from .models import Deals, DealsHistory, Orders, Users


class UserRepository:
    def __init__(self, db_session: Callable[[], _AsyncGeneratorContextManager[AsyncSession]]) -> None:
        self._session_factory = db_session

    async def create(self, tg_id: int, role: str = "user"):
        async with self._session_factory() as session:
            instance = Users(tg_id=tg_id, role=role)
            session.add(instance)

            return instance

    async def get_user(self, tg_id: int) -> Users | None:
        async with self._session_factory() as session:
            filters = [Users.tg_id == tg_id]
            query = select(Users).where(*filters)

            results = await session.execute(query)
            user = results.scalar_one_or_none()
            return user


class OrdersRepository:
    def __init__(self, db_session: Callable[[], _AsyncGeneratorContextManager[AsyncSession]]) -> None:
        self._session_factory = db_session

    async def create(
        self,
        customer_id: int,
        customer_wallet: str,
        deal_conditions: str,
        token_address: str,
        token_amount: int,
        start_date: datetime,
        end_date: datetime,
    ):
        async with self._session_factory() as session:
            instatnce = Orders(
                customer_id=customer_id,
                customer_wallet=customer_wallet,
                deal_conditions=deal_conditions,
                token_address=token_address,
                token_amount=token_amount,
                start_date=start_date,
                end_date=end_date,
            )
            session.add(instatnce)

            return instatnce

    async def get_order(self, **filters) -> Orders:
        async with self._session_factory() as session:
            query = select(Orders).filter_by(**filters)

            results = await session.execute(query)

            return results.scalar_one_or_none()

    async def get_orders(self, **filters) -> Sequence[Orders | None]:
        async with self._session_factory() as session:
            query = select(Orders).filter_by(**filters)

            results = await session.execute(query)

            return results.scalars().all()


class DealsRepository:
    def __init__(self, db_session: Callable[[], _AsyncGeneratorContextManager[AsyncSession]]) -> None:
        self._session_factory = db_session

    async def create(self, order_id: UUID, executor_id: int, executor_wallet: str):
        async with self._session_factory() as session:
            instance = Deals(order_id=order_id, executor_id=executor_id, executor_wallet=executor_wallet)
            session.add(instance)

            return instance

    async def get_deals(self, **filters) -> Sequence[Deals | None]:
        async with self._session_factory() as session:
            query = select(Deals).filter_by(**filters)

            results = await session.execute(query)

            return results.scalars().all()


class DealsHisotryRepository:
    def __init__(self, db_session: Callable[[], _AsyncGeneratorContextManager[AsyncSession]]) -> None:
        self._session_factory = db_session

    async def create(self, deal_id: UUID, status: str) -> DealsHistory:
        async with self._session_factory() as session:
            instance = DealsHistory(deal_id=deal_id, status=status)
            session.add(instance)

            return instance

    async def get_deal_history(self, **filters) -> Sequence[DealsHistory | None]:
        async with self._session_factory() as session:
            query = select(DealsHistory).filter_by(**filters)

            results = await session.execute(query)

            return results.scalars().all()


user_repository = UserRepository(db_session=db_helper.get_db_session)
orders_repository = OrdersRepository(db_session=db_helper.get_db_session)
deals_repository = DealsRepository(db_session=db_helper.get_db_session)
deals_history_repository = DealsHisotryRepository(db_session=db_helper.get_db_session)
