from pathlib import Path

import psycopg
from dotenv import load_dotenv
import os
import logging
from database.generators.generate_customers import Cusgenerator
from database.generators.generate_sellers import Selgenerator
from database.generators.generate_orders import Ordgenerator
from datetime import datetime, timedelta
import random
import time

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

conn = psycopg.connect(
        host=POSTGRES_HOST,
        port=5432,
        dbname=POSTGRES_DBNAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )



cur = conn.cursor()
if cur is not None:
    logging.info('Connected to postgres database !')

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 3, 1)
delta_date = timedelta(days=1)

customer_gen = Cusgenerator(conn=conn)
seller_gen = Selgenerator(conn=conn)
order_gen = Ordgenerator(conn=conn, start_date=start_date)

while True:
    num_customers = random.randint(0, 15)
    for _ in range(num_customers):
        customer_gen.generate()
    
    num_orders = random.randint(100, 500)
    for _ in range(num_orders):
        order_gen.generate()

    num_sellers = random.randint(0, 4)
    for _ in range(num_sellers):
        seller_gen.generate()
    
    order_gen.update_orders()

    start_date += delta_date
    order_gen.start_date = start_date
    
    logging.info(f"completed generate data day: {start_date}")
    
    time.sleep(10)
    if start_date == end_date:
        break

cur.close()
conn.close()