from database.generators.generator import Generator
import logging
import random
import uuid

class Itegenerator(Generator):

    def __init__(self, conn):
        super().__init__(conn)

        self.conn = conn
    
    def generate(self, 
                 order_id: int) -> float:
        
        logging.basicConfig(level=logging.DEBUG)
        cur = self.conn.cursor()

        num_products = random.randint(1, 3)

        try:
            cur.execute(
                """
                SELECT max(product_id) FROM products;
                """
            )
            logging.info("Get max product_id in products table successful!")
        except Exception as e:
            logging.error(f"Error occur while get max product_id in products table! {e}")
        
        max_product_id = cur.fetchall()[0][0]
        product_id = random.randint(1, max_product_id)

        try:
            cur.execute(
                f"""
                SELECT product_price FROM products WHERE product_id = {product_id};
                """
            )
            logging.info("Get product_price in products table successful!")
        except Exception as e:
            logging.error(f"Error occur while get product_price in products table! {e}")
        
        product_price = cur.fetchall()[0][0]

        try:
            cur.execute(
                f"""
                SELECT max(seller_id) FROM sellers;
                """
            )
            logging.info("Get max seller_id in sellers table successful!")
        except Exception as e:
            logging.error(f"Error occur while get max seller_id in sellers table! {e}")
        
        max_seller_id = cur.fetchall()[0][0]

        seller_id = random.randint(0, max_seller_id)
        price = num_products * product_price
        freight_value = random.uniform(10, 25) * num_products
        order_item_id = uuid.uuid4()
        
        try:
            cur.execute(
                f"""
                INSERT INTO order_items(
                    order_item_id,
                    order_id,
                    product_id,
                    seller_id,
                    shipping_limit_date,
                    price,
                    freight_value
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (order_item_id, order_id, product_id, seller_id, None, price, freight_value)
            )
            logging.info("Insert order_item record to order_items table successful!")
        except Exception as e:
            logging.error(f"Error occur while insert order_item record to order_items table! {e}")
        
        self.conn.commit()
        cur.close()

        return price + freight_value
        