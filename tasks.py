from typing import Dict, List
from celery import Celery
from models.Producto import Producto
from models.Carrito import Carrito
from models.Venta import Venta
import redis
import json
celery = Celery('tasks', broker='amqp://admin:admin@localhost:5672/',backend='rpc://')

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@celery.task
def send_carrito(data:Dict):

    carrito = Carrito(numero=data['numero'], productos=data['productos'])

    products_seleccionados = []
    subtotal = 0.0
    productos = carrito.productos

    for producto in productos:

        product = Producto(name=producto.name, stock=producto.stock, price=producto.price)

        if product.stock > 0:
            products_seleccionados.append(product)
            subtotal += product.stock
        else:
            print("El producto %s no tiene stock para hacer la venta " % (product.name))


    venta = Venta(numero = carrito.numero ,productos = products_seleccionados, subtotal=subtotal, iva=0.15, total=( subtotal * 0.15) + subtotal )

    result = celery.send_task("tasks.send_ventas", args=[venta.dict()], queue="ventas")

    print("El id del resultado de envio a la cola de ventas es => %s"%(result.id))


@celery.task
def send_ventas(data:Dict):

    json_data = json.dumps(data)

    redis_client.set(data['numero'], json_data)

    print("La venta se ha generado correctamente :)")

