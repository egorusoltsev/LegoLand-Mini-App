import time
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from auth.dependencies import check_admin_key, get_optional_user_id, get_user_id_from_token, order_rate_limit
from db import get_db
from models import OrderItemModel, OrderModel
from utils.telegram import send_telegram_message

router = APIRouter()


class OrderItemCreate(BaseModel):
    id: int
    title: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    price: int = Field(ge=0)


class OrderCreate(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    address: Optional[str] = ""
    delivery_method: str = Field(default="contact")
    items: List[OrderItemCreate] = Field(min_length=1)

    @field_validator("name", "phone")
    @classmethod
    def non_empty_string(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty")
        return cleaned


@router.post("/order")
def create_order(order: OrderCreate, user_id: Optional[int] = Depends(get_optional_user_id), _=Depends(order_rate_limit), db=Depends(get_db)):
    payload = order.model_dump()
    payload["id"] = str(uuid.uuid4())
    payload["status"] = "new"
    payload["created_at"] = int(time.time())
    payload["total"] = sum(item["price"] * item["quantity"] for item in payload["items"])

    items_text = "\n".join(
        [
            f"• {item['title']} x{item['quantity']} = {item['price'] * item['quantity']} ₽"
            for item in payload.get("items", [])
        ]
    )
    msg = (
        "🧱 <b>Новый заказ!</b>\n\n"
        f"🆔 ID: <code>{payload['id']}</code>\n"
        f"👤 Имя: <b>{payload.get('name')}</b>\n"
        f"📞 Телефон: <b>{payload.get('phone')}</b>\n"
        f"🏠 Адрес: <b>{payload.get('address') or '-'}</b>\n\n"
        f"📦 Товары:\n{items_text}\n\n"
        f"💰 Итого: <b>{payload.get('total')} ₽</b>"
    )
    send_telegram_message(msg)

    db_order = OrderModel(
        id=payload["id"],
        name=payload["name"],
        phone=payload["phone"],
        address=payload.get("address"),
        status=payload["status"],
        total=payload["total"],
        created_at=payload["created_at"],
        user_id=user_id,
    )
    db.add(db_order)

    for item in payload["items"]:
        db.add(
            OrderItemModel(
                order_id=payload["id"],
                product_id=item["id"],
                title=item["title"],
                quantity=item["quantity"],
                price=item["price"],
            )
        )

    db.commit()
    return {"status": "ok", "order_id": payload["id"]}


@router.get("/orders")
def get_orders(limit: int = 100, offset: int = 0, _=Depends(check_admin_key), db=Depends(get_db)):
    db_orders = db.query(OrderModel).order_by(OrderModel.created_at.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": o.id,
            "name": o.name,
            "phone": o.phone,
            "address": o.address,
            "status": o.status,
            "total": o.total,
            "created_at": o.created_at,
        }
        for o in db_orders
    ]


@router.get("/my/orders")
def get_my_orders(user_id: int = Depends(get_user_id_from_token), db=Depends(get_db)):
    orders = (
        db.query(OrderModel)
        .filter(OrderModel.user_id == user_id)
        .order_by(OrderModel.created_at.desc())
        .all()
    )

    return {
        "orders": [
            {
                "id": o.id,
                "status": o.status,
                "total": o.total,
                "created_at": o.created_at,
            }
            for o in orders
        ]
    }


@router.patch("/orders/{order_id}/status")
def update_order_status(order_id: str, status: dict, _=Depends(check_admin_key), db=Depends(get_db)):
    new_status = status.get("status")
    allowed = ["new", "confirmed", "shipped", "done"]
    if new_status not in allowed:
        return {"status": "error", "message": "Неверный статус"}

    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        return {"status": "error", "message": "Заказ не найден"}

    order.status = new_status
    db.commit()
    return {"status": "ok", "message": "Статус обновлён"}


@router.get("/public/orders/{order_id}")
def get_public_order(order_id: str, db=Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
    return {
        "id": order.id,
        "status": order.status,
        "created_at": order.created_at,
        "total": order.total,
        "items": [
            {
                "id": item.product_id,
                "title": item.title,
                "price": item.price,
                "quantity": item.quantity,
            }
            for item in items
        ],
    }
