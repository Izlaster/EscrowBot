from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP, Integer, Numeric, String, Text, Uuid


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(length=20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(UTC))


class Orders(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_wallet: Mapped[str] = mapped_column(Text, nullable=False)
    deal_conditions: Mapped[str] = mapped_column(Text, nullable=False)
    deal_proofs: Mapped[str] = mapped_column(Text, nullable=False)
    commission: Mapped[float] = mapped_column(Numeric(precision=15, scale=14), nullable=False)
    token_address: Mapped[str] = mapped_column(Text, nullable=False)
    token_amount: Mapped[float] = mapped_column(Numeric(precision=15, scale=10), nullable=False)
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(UTC))

    deals = relationship("Deals", back_populates="orders")


class Deals(Base):
    __tablename__ = "deals"

    deal_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.order_id"), nullable=False)
    executor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    executor_wallet: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(UTC))

    orders = relationship("Orders", back_populates="deals", single_parent=True)
    deals_history = relationship("DealsHistory", back_populates="deals", single_parent=True)


class DealsHistory(Base):
    __tablename__ = "deals_history"

    history_deal_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deal_id: Mapped[int] = mapped_column(Integer, ForeignKey("deals.deal_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(length=20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(UTC))

    deals = relationship("Deals", back_populates="deals_history")
