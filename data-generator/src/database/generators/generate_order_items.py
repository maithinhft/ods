from database.generators.generator import Generator
import logging
import random
import uuid

class Itegenerator(Generator):

    def __init__(self, psql_conn, mysql_conn):
        super().__init__(mysql_conn) 
        self.psql_conn = psql_conn
        self.mysql_conn = mysql_conn
    
    def generate(self, order_id: int) -> float:
        logging.basicConfig(level=logging.DEBUG)
        psql_cur = self.psql_conn.cursor()
        mysql_cur = self.mysql_conn.cursor()

        num_products = random.randint(1, 3)

        try:
            psql_cur.execute("SELECT max(product_id) FROM products;")
            logging.info("Get max product_id in products table successful!")
        except Exception as e:
            logging.error(f"Error occur while get max product_id in products table! {e}")
        max_product_id = psql_cur.fetchall()[0][0]
        product_id = random.randint(1, max_product_id)

        try:
            psql_cur.execute(f"SELECT product_price FROM products WHERE product_id = {product_id};")
            logging.info("Get product_price in products table successful!")
        except Exception as e:
            logging.error(f"Error occur while get product_price in products table! {e}")
        product_price = psql_cur.fetchall()[0][0]

        try:
            psql_cur.execute("SELECT max(seller_id) FROM sellers;")
            logging.info("Get max seller_id in sellers table successful!")
        except Exception as e:
            logging.error(f"Error occur while get max seller_id in sellers table! {e}")
        max_seller_id = psql_cur.fetchall()[0][0]

        seller_id = random.randint(0, max_seller_id)
        price = num_products * product_price
        freight_value = random.uniform(10, 25) * num_products
        order_item_id = str(uuid.uuid4())
        
        try:
            mysql_cur.execute(
                """
                INSERT INTO order_items(
                    order_item_id, order_id, product_id,
                    seller_id, shipping_limit_date, price, freight_value
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (order_item_id, order_id, product_id, seller_id, None, price, freight_value)
            )
            logging.info("Insert order_item record to order_items table successful!")
        except Exception as e:
            logging.error(f"Error occur while insert order_item record to order_items table! {e}")
        
        self.mysql_conn.commit()
        psql_cur.close()
        mysql_cur.close()

        return price + freight_value