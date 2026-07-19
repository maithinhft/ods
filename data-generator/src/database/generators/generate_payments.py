from database.generators.generator import Generator
from datetime import datetime
import random
import logging

class Paygenerator(Generator):

    def __init__(self, conn):
        super().__init__(conn)
        self.conn = conn 
    
    def generate(self, order_id: int, payment_value: float):
        logging.basicConfig(level=logging.DEBUG)
        cur = self.conn.cursor()
        payment_list = ['credit_card', 'boleto', 'voucher', 'debit_card']

        payment_idx = random.randint(0, 3)
        payment_type = payment_list[payment_idx]
        try:
            cur.execute(
                """
                INSERT INTO order_payments(
                    order_id, payment_type, payment_value
                ) VALUES (%s, %s, %s)
                """,
                (order_id, payment_type, payment_value)
            )
            logging.info("Insert order record to order_payments table successful!")
        except Exception as e:
            logging.error(f"Error occur while insert order record to order_payments table! {e}")
        
        self.conn.commit()
        cur.close()