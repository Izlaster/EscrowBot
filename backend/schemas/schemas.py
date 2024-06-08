from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class User(BaseModel):
    tg_id: int
    role: str = Field(default="user")


class GetUser(User):
    class Config:
        from_attributes = True


class BaseOrders(BaseModel):
    customer_id: int
    customer_wallet: str
    deal_conditions: str
    token_address: str
    token_amount: int
    start_date: str
    end_date: str


class Orders(BaseOrders):
    order_id: UUID
    start_date: datetime
    end_date: datetime


class GetOrders(Orders):
    class Config:
        from_attributes = True


class Deals(BaseModel):
    deal_id: UUID
    order_id: UUID
    executor_id: int
    executor_wallet: str


class GetDeals(Deals):
    class Config:
        from_attributes = True


class DealsHistory(BaseModel):
    history_deal_id: UUID
    deal_id: UUID
    status: str


class GetDealsHistory(DealsHistory):
    class Config:
        from_attributes = True
