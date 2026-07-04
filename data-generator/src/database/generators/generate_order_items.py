from database.generators.generator import Generator
import logging
import random
import uuid

class Itegenerator(Generator):

    def __init__(self, psql_conn, mysql_conn):
        super().__init__(mysql_conn) 
        self.psql_conn = psql_conn
        self.mysql_conn = mysql_conn
        self.refresh_reference_data()

    def refresh_reference_data(self):
        """Load product catalog and max seller_id from Postgres once.
        Call this after generating new sellers each day."""
        cur = self.psql_conn.cursor()
        cur.execute("SELECT product_id, product_price FROM products")
        self._products = cur.fetchall()
        cur.execute("SELECT COALESCE(max(seller_id), 0) FROM sellers")
        self._max_seller_id = cur.fetchone()[0]
        cur.close()
    
    def generate(self, order_id: int) -> float:
        mysql_cur = self.mysql_conn.cursor()

        num_products = random.randint(1, 3)
        product_id, product_price = random.choice(self._products)
        seller_id = random.randint(0, self._max_seller_id)
        price = num_products * float(product_price)
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
        except Exception as e:
            logging.error(f"Error inserting order_item record: {e}")
        
        # No commit here — batched at Ordgenerator.generate() level
        mysql_cur.close()

        return price + freight_value