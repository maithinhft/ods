from database.generators.generator import Generator
from database.generators.generate_order_reviews import Revgenerator
from database.generators.generate_payments import Paygenerator
from database.generators.generate_order_items import Itegenerator
from psycopg import Connection as PsqlConnection
from mysql.connector.connection import MySQLConnection
from datetime import datetime, timedelta
import random
import logging

class Ordgenerator(Generator):

    def __init__(self, 
                 psql_conn: PsqlConnection,
                 mysql_conn: MySQLConnection,
                 start_date: datetime):
        super().__init__(psql_conn)

        self.start_date = start_date
        self.psql_conn = psql_conn
        self.mysql_conn = mysql_conn
        
        self.generate_order_reviews = Revgenerator(conn=mysql_conn)
        self.generate_order_payments = Paygenerator(conn=mysql_conn)
        self.generate_order_items = Itegenerator(psql_conn=psql_conn, mysql_conn=mysql_conn)

        # Cache max_customer_id and use order_id counter
        self._refresh_customer_cache()
        self._init_order_counter()

    def _refresh_customer_cache(self):
        """Refresh cached max_customer_id from Postgres. Call after generating customers each day."""
        psql_cur = self.psql_conn.cursor()
        psql_cur.execute("SELECT COALESCE(max(customer_id), 0) FROM customers")
        self._max_customer_id = psql_cur.fetchone()[0]
        psql_cur.close()

    def _init_order_counter(self):
        """Initialize order_id counter from MySQL."""
        mysql_cur = self.mysql_conn.cursor()
        mysql_cur.execute("SELECT COALESCE(max(order_id), -1) FROM orders")
        self._next_order_id = mysql_cur.fetchone()[0] + 1
        mysql_cur.close()

    def _generate_random_timestamp(self) -> datetime:
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return self.start_date + delta

    def generate(self):
        mysql_cur = self.mysql_conn.cursor()
        
        order_id = self._next_order_id
        self._next_order_id += 1
        
        customer_id = random.randint(0, self._max_customer_id)
        
        order_status = 'created'
        order_purchase_timestamp = self._generate_random_timestamp()
        order_approved_at = None
        order_delivered_carrier_date = None
        order_delivered_customer_date = None
        order_estimated_delivery_date = None

        try:
            mysql_cur.execute(
                """
                INSERT INTO stg_orders(
                    order_id, customer_id, order_status, order_purchase_timestamp,
                    order_approved_at, order_delivered_carrier_date,
                    order_delivered_customer_date, order_estimated_delivery_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (order_id, customer_id, order_status, order_purchase_timestamp, 
                 order_approved_at, order_delivered_carrier_date, 
                 order_delivered_customer_date, order_estimated_delivery_date)
            )
        except Exception as e:
            logging.error(f"Error inserting stg_orders record: {e}")

        try:
            mysql_cur.execute(
                """
                INSERT INTO orders(
                    order_id, customer_id, order_status, order_purchase_timestamp,
                    order_approved_at, order_delivered_carrier_date,
                    order_delivered_customer_date, order_estimated_delivery_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (order_id, customer_id, order_status, order_purchase_timestamp, 
                 order_approved_at, order_delivered_carrier_date, 
                 order_delivered_customer_date, order_estimated_delivery_date)
            )
        except Exception as e:
            logging.error(f"Error inserting orders record: {e}")
        
        num_order_items = random.randint(1, 3)
        payment_value = 0
        
        for _ in range(num_order_items):
            payment_value += self.generate_order_items.generate(order_id=order_id)
        
        self.generate_order_payments.generate(order_id=order_id, payment_value=payment_value)
        
        # Single commit per order (covers order + items + payment)
        self.mysql_conn.commit()
        mysql_cur.close()

    def update_orders(self) -> None:
        mysql_cur = self.mysql_conn.cursor()

        try:
            mysql_cur.execute(
                """
                UPDATE stg_orders
                SET 
                    order_approved_at = CASE WHEN order_status = 'created' THEN %s ELSE order_approved_at END,
                    order_delivered_carrier_date = CASE WHEN order_status = 'processing' THEN %s ELSE order_delivered_carrier_date END,
                    order_delivered_customer_date = CASE WHEN order_status = 'shipped' THEN %s ELSE order_delivered_customer_date END,
                    order_status = CASE
                            WHEN RAND() < 0.03 THEN 'canceled'
                            WHEN order_status = 'shipped' THEN 'delivered'
                            WHEN order_status = 'processing' THEN 'shipped'
                            WHEN order_status = 'invoiced' THEN 'processing'
                            WHEN order_status = 'approved' THEN 'invoiced'
                            WHEN order_status = 'created' THEN 'approved'
                            ELSE order_status
                        END
                WHERE order_purchase_timestamp < %s
                """,
                (self._generate_random_timestamp(), 
                 self._generate_random_timestamp(), 
                 self._generate_random_timestamp(), 
                 self.start_date)                  
            )
        except Exception as e:
            logging.error(f"Error updating stg_orders: {e}")
        
        try:
            mysql_cur.execute(
                """
                UPDATE orders o
                JOIN stg_orders so ON o.order_id = so.order_id
                SET 
                    o.order_status = so.order_status,
                    o.order_purchase_timestamp = so.order_purchase_timestamp,
                    o.order_approved_at = so.order_approved_at,
                    o.order_delivered_carrier_date = so.order_delivered_carrier_date,
                    o.order_delivered_customer_date = so.order_delivered_customer_date
                WHERE so.order_purchase_timestamp < %s
                """,
                (self.start_date,)
            )
        except Exception as e:
            logging.error(f"Error updating orders: {e}")

        try:
            mysql_cur.execute(
                """
                SELECT order_id, order_delivered_customer_date
                FROM stg_orders
                WHERE order_status = 'delivered'
                AND order_purchase_timestamp < %s
                """,
                (self.start_date,)
            )
        except Exception as e:
            logging.error(f"Error selecting delivered orders: {e}")
        
        orders_ready_for_review = mysql_cur.fetchall()

        for order_id, delivered_date in orders_ready_for_review:
            if order_id is not None and delivered_date is not None:
                self.generate_order_reviews.generate(order_id=order_id, delivered_date=delivered_date)

        try:
            mysql_cur.execute(
                """
                DELETE FROM stg_orders
                WHERE (order_status = 'canceled' OR order_status = 'delivered') 
                AND order_purchase_timestamp < %s
                """,
                (self.start_date,)
            )
        except Exception as e:
            logging.error(f"Error deleting completed stg_orders: {e}")
        
        self.mysql_conn.commit()
        mysql_cur.close()