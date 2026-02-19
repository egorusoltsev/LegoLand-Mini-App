from sqlalchemy import Column, Integer, String, BigInteger, Boolean
from db import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    status = Column(String)
    total = Column(Integer)
    created_at = Column(BigInteger)
    user_id = Column(BigInteger, nullable=True)


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Integer)
    image = Column(String)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)


class AuthSessionModel(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    telegram_id = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger)
    used = Column(Boolean, default=False)
