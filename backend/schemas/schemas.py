from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


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
    token_amount: float
    start_date: str
    end_date: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": 1,
                    "customer_wallet": "wallet",
                    "deal_conditions": "conditions",
                    "token_address": "address",
                    "token_amount": 100.00,
                    "start_date": "01.01.2022 12:00",
                    "end_date": "02.01.2022 12:00",
                }
            ]
        }
    }


class Orders(BaseOrders):
    order_id: UUID
    start_date: datetime
    end_date: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": 1,
                    "customer_wallet": "wallet",
                    "deal_conditions": "conditions",
                    "token_address": "address",
                    "token_amount": 100.00,
                    "start_date": "2022-01-01T12:00:00",
                    "end_date": "2022-01-02T12:00:00",
                    "order_id": "77f796d4-71df-4147-af32-06e481fb850e",
                }
            ]
        }
    }


class GetOrders(Orders):
    class Config:
        from_attributes = True


class BaseDeals(BaseModel):
    order_id: UUID
    executor_id: int
    executor_wallet: str


class Deals(BaseDeals):
    deal_id: UUID


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
