from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from routers import auth, orders


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(orders.router)

