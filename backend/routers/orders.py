import time
from fastapi import APIRouter, Depends, HTTPException
from db import SessionLocal
from auth.dependencies import check_admin_key, get_user_id_from_token
from utils.telegram import send_telegram_message
from models import OrderModel, OrderItemModel  # ← добавь OrderItemModel

router = APIRouter()


@router.post("/order")
def create_order(order: dict, user_id: int = Depends(get_user_id_from_token)):
    new_order = order.copy()
    new_order["id"] = int(time.time() * 1000)
    new_order["status"] = "new"
    new_order["created_at"] = int(time.time())

    items_text = "\n".join(
        [
            f"• {item['title']} x{item['quantity']} = {item['price'] * item['quantity']} ₽"
            for item in new_order.get("items", [])
        ]
    )

    msg = (
        "🧱 <b>Новый заказ!</b>\n\n"
        f"🆔 ID: <code>{new_order['id']}</code>\n"
        f"👤 Имя: <b>{new_order.get('name')}</b>\n"
        f"📞 Телефон: <b>{new_order.get('phone')}</b>\n"
        f"🏠 Адрес: <b>{new_order.get('address', '-')}</b>\n\n"
        f"📦 Товары:\n{items_text}\n\n"
        f"💰 Итого: <b>{new_order.get('total')} ₽</b>"
    )

    send_telegram_message(msg)

    db = SessionLocal()

    try:
        db_order = OrderModel(
            id=new_order["id"],
            name=new_order.get("name"),
            phone=new_order.get("phone"),
            status=new_order.get("status"),
            total=new_order.get("total"),
            created_at=new_order.get("created_at"),
            user_id=user_id   # ← ВОТ ТАК правильно
        )

        db.add(db_order)

        for item in new_order.get("items", []):
            db_item = OrderItemModel(
                order_id=new_order["id"],
                product_id=item["id"],
                quantity=item["quantity"],
                price=item["price"]
            )
            db.add(db_item)   # ← внутри цикла

        db.commit()

    finally:
        db.close()

    return {"status": "ok", "order_id": new_order["id"]}

@router.get("/orders")
def get_orders(_=Depends(check_admin_key)):
    db = SessionLocal()
    db_orders = db.query(OrderModel).all()
    db.close()

    return [
        {
            "id": o.id,
            "name": o.name,
            "phone": o.phone,
            "status": o.status,
            "total": o.total,
            "created_at": o.created_at,
        }
        for o in db_orders
    ]


@router.get("/my/orders")
def get_my_orders(user_id: int = Depends(get_user_id_from_token)):
    db = SessionLocal()
    try:
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
    finally:
        db.close()


@router.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status: dict, _=Depends(check_admin_key)):
    new_status = status.get("status")
    allowed = ["new", "confirmed", "shipped", "done"]
    if new_status not in allowed:
        return {"status": "error", "message": "Неверный статус"}

    db = SessionLocal()
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

    if not order:
        db.close()
        return {"status": "error", "message": "Заказ не найден"}

    order.status = new_status
    db.commit()
    db.close()

    return {"status": "ok", "message": "Статус обновлён"}


@router.get("/public/orders/{order_id}")
def get_public_order(order_id: int):
    db = SessionLocal()
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

    if not order:
        db.close()
        raise HTTPException(status_code=404, detail="Order not found")

    result = {
        "id": order.id,
        "status": order.status,
        "created_at": order.created_at,
        "total": order.total,
        "items": [],
    }

    db.close()
    return result
