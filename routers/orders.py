from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from .auth import get_current_user, get_user_exception
import sys
sys.path.append("..")

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={401: {"user": "Not authorized"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Order(BaseModel):
    order_details: str
    delivery_address: str
    price: int


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Orders).all()


@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Orders)\
        .filter(models.Orders.user_id == user.get("id"))\
        .all()


@router.get("/{order_id}")
async def read_order_by_id(order_id: int,
                           user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    order_model = db.query(models.Orders)\
        .filter(models.Orders.order_id == order_id)\
        .filter(models.Orders.user_id == user.get("id"))\
        .first()
    if order_model is not None:
        return order_model
    raise http_exception()


@router.post("/")
async def create_order(order: Order,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    order_model = models.Orders()
    order_model.order_details = order.order_details
    order_model.delivery_address = order.delivery_address
    order_model.price = order.price
    order_model.user_id = user.get("id")

    db.add(order_model)
    db.commit()

    return successful_response(201)


@router.put("/{order_id}")
async def update_order(order_id: int,
                       order: Order,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    order_model = db.query(models.Orders)\
        .filter(models.Orders.order_id == order_id)\
        .filter(models.Orders.user_id == user.get("id"))\
        .first()

    if order_model is None:
        raise http_exception()

    order_model.order_details = order.order_details
    order_model.delivery_address = order.delivery_address
    order_model.price = order.price

    db.add(order_model)
    db.commit()

    return successful_response(201)


@router.delete("/{order_id}")
async def delete_order(order_id: int,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    order_model = db.query(models.Orders)\
        .filter(models.Orders.order_id == order_id) \
        .filter(models.Orders.user_id == user.get("id")) \
        .first()

    if order_model is None:
        raise http_exception()

    db.query(models.Orders)\
        .filter(models.Orders.order_id == order_id)\
        .delete()

    db.commit()

    return successful_response(201)


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }


def http_exception():
    return HTTPException(status_code=404, detail="Order not found")

