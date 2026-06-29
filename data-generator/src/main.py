from pathlib import Path

import mysql.connector

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
POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT'))

MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT'))
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

psql_conn = psycopg.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    dbname=POSTGRES_DBNAME,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)

mysql_conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)


psql_cur = psql_conn.cursor()
if psql_cur is not None:
    logging.info('Connected to postgres database !')

mysql_cur = mysql_conn.cursor()
if mysql_cur is not None:
    logging.info('Connected to mysql database !')

start_date = datetime(2026, 1, 6)
end_date = datetime(2026, 3, 1)
delta_date = timedelta(days=1)

customer_gen = Cusgenerator(conn=psql_conn)
seller_gen = Selgenerator(conn=psql_conn)
order_gen = Ordgenerator(
    psql_conn=psql_conn, mysql_conn=mysql_conn, start_date=start_date)

while True:
    num_customers = random.randint(0, 100)
    for _ in range(num_customers):
        customer_gen.generate()

    num_orders = random.randint(10000, 50000)
    for _ in range(num_orders):
        order_gen.generate()

    num_sellers = random.randint(0, 30)
    for _ in range(num_sellers):
        seller_gen.generate()

    order_gen.update_orders()

    start_date += delta_date
    order_gen.start_date = start_date

    logging.info(f"completed generate data day: {start_date}")

    time.sleep(10)
    if start_date == end_date:
        break

psql_cur.close()
psql_conn.close()

mysql_cur.close()
mysql_conn.close()
