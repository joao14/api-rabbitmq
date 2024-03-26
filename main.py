from fastapi import FastAPI, BackgroundTasks
from typing import List
from celery import Celery
from models.Carrito import Carrito
import json

app = FastAPI()

celery = Celery('tasks', broker='amqp://admin:admin@localhost:5672//',backend='rpc://')

@app.post("/add")
async def send_message_api(carrito: Carrito):
    # products_dict = [product.dict() for product in products]
    result = celery.send_task("tasks.send_carrito", args=[carrito.dict()], queue="carritos")
    return {"status": "Message sent to Celery for processing", "task_id": result.id}

