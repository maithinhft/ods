from database.generators.generator import Generator
from datetime import datetime
import random
import logging

class Paygenerator(Generator):

    def __init__(self, conn):
        super().__init__(conn)
        self.conn = conn 
    
    def generate(self, order_id: int, payment_value: float):
        cur = self.conn.cursor()
        payment_list = ['credit_card', 'boleto', 'voucher', 'debit_card']

        payment_type = random.choice(payment_list)
        try:
            cur.execute(
                """
                INSERT INTO order_payments(
                    order_id, payment_type, payment_value
                ) VALUES (%s, %s, %s)
                """,
                (order_id, payment_type, payment_value)
            )
        except Exception as e:
            logging.error(f"Error inserting order_payment record: {e}")
        
        # No commit here — batched at Ordgenerator.generate() level
        cur.close()