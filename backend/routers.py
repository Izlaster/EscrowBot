from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from schemas.schemas import BaseDeals, BaseOrders, Deals, GetOrders, GetUser, Orders, User
from services import DealService, OrderService, UserService

router = APIRouter(prefix="", tags=None)


@router.post("/create_user", response_model=GetUser, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    user = await UserService.get_user(tg_id=user.tg_id)
    if user is None:
        new_user = User(tg_id=user.tg_id, role=user.role)
        await UserService.create_user(new_user)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=GetUser.model_validate(new_user).model_dump())
    return JSONResponse(status_code=status.HTTP_200_OK, content=GetUser.model_validate(user).model_dump())


@router.post("/register_order", response_model=Orders, status_code=status.HTTP_201_CREATED)
async def create_new_order(new_order: BaseOrders):
    order = await OrderService.create(new_order)

    return order


@router.post("/register_deal", response_model=Deals, status_code=status.HTTP_201_CREATED)
async def create_new_deal(new_deal: BaseDeals):
    deal = await DealService.create(new_deal)

    return deal


@router.get("/order/{order_id}", response_model=Orders, status_code=status.HTTP_200_OK)
async def order(order_id: int):
    # Тут надо получать полную инфу. То есть сразу кто создатель и исполнитель
    order = await OrderService.get_order(order_id=order_id)

    return order


@router.get("/order_with_deal_wallets/{order_id}")
async def order_with_deal(order_id: int):
    order_with_deal = await OrderService.get_order_with_deal_wallets_token(order_id=order_id)

    return order_with_deal
