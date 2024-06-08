from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TIMESTAMP, Integer, String, Text, Uuid


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(length=20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(UTC))


class Orders(Base):
    __tablename__ = "orders"

    order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_wallet: Mapped[str] = mapped_column(Text, nullable=False)
    deal_conditions: Mapped[str] = mapped_column(Text, nullable=False)
    # deal_proofs: Mapped[str] = mapped_column(Text, nullable=False)
    token_address: Mapped[str] = mapped_column(Text, nullable=False)
    token_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(UTC))

    # deals: Mapped["Deals"] = relationship(back_populates="orders")


class Deals(Base):
    __tablename__ = "deals"

    deal_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("orders.order_id"), nullable=False)
    executor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    executor_wallet: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(UTC))

    # orders: Mapped["Orders"] = relationship(back_populates="deals", single_parent=True)


class DealsHistory(Base):
    __tablename__ = "deals_history"

    history_deal_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    deal_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), default=uuid4)
    status: Mapped[str] = mapped_column(String(length=20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(UTC))