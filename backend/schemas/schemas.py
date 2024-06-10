from datetime import datetime

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
    deal_proofs: str
    token_address: str
    token_amount: float
    commission: float
    start_date: str
    end_date: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": 1,
                    "customer_wallet": "wallet",
                    "deal_proofs": "deal_proofs",
                    "deal_conditions": "conditions",
                    "token_address": "address",
                    "token_amount": 100.00,
                    "commission": 0.12,
                    "start_date": "01.01.2022 12:00",
                    "end_date": "02.01.2022 12:00",
                }
            ]
        }
    }


class Orders(BaseOrders):
    order_id: int
    start_date: datetime
    end_date: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": 1,
                    "customer_wallet": "wallet",
                    "deal_conditions": "conditions",
                    "deal_proofs": "deal_proofs",
                    "token_address": "address",
                    "token_amount": 100.00,
                    "commission": 0.12,
                    "start_date": "2022-01-01T12:00:00",
                    "end_date": "2022-01-02T12:00:00",
                    "order_id": "77f796d4-71df-4147-af32-06e481fb850e",
                }
            ]
        }
    }


class WalletsTokens(BaseModel):
    customer_wallet: str
    executor_wallet: str
    token_address: str
    token_amount: float
    commission: float

    class Config:
        orm_mode = True


class GetOrders(Orders):
    class Config:
        from_attributes = True


class BaseDeals(BaseModel):
    order_id: int
    executor_id: int
    executor_wallet: str


class Deals(BaseDeals):
    deal_id: int


class GetDeals(Deals):
    class Config:
        from_attributes = True


class DealsHistory(BaseModel):
    history_deal_id: int
    deal_id: int
    status: str


class GetDealsHistory(DealsHistory):
    class Config:
        from_attributes = True
