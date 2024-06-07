from datetime import UTC, datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP, Integer, String, Text


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(length=20), nullable=False)
    created_at: Mapped[datetime.timestamp] = mapped_column(TIMESTAMP, default=datetime.now(UTC))

    wallets: Mapped[list["Wallets"]] = relationship("Wallets", back_populates="users")


class Wallets(Base):
    __tablename__ = "wallets"

    wallet_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.tg_id"), nullable=False)
    address_wallet: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime.timestamp] = mapped_column(TIMESTAMP, default=datetime.now(UTC))
    is_deleted: Mapped[bool] = mapped_column(TIMESTAMP, nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="wallets")
