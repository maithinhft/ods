import random
from database.generators.generator import Generator
import logging


class Cusgenerator(Generator):

    def __init__(self, conn):
        super().__init__(conn)
        self.conn = conn

        # Cache all geolocations in memory instead of OFFSET random LIMIT 1
        cur = conn.cursor()
        cur.execute("SELECT geolocation_city, geolocation_state FROM geolocation")
        self._geolocations = cur.fetchall()

        # Use counter instead of SELECT max() every time
        cur.execute("SELECT COALESCE(max(customer_id), -1) FROM customers")
        self._next_id = cur.fetchone()[0] + 1
        cur.close()
    
    def generate(self):
        cur = self.conn.cursor()
        customer_city, customer_state = random.choice(self._geolocations)
        customer_id = self._next_id
        self._next_id += 1

        try:
            cur.execute(
                "INSERT INTO customers(customer_id, customer_city, customer_state) VALUES (%s, %s, %s)",
                (customer_id, customer_city, customer_state)
            )
        except Exception as e:
            logging.error(f"Error inserting customer record: {e}")
        
        cur.close()
        self.conn.commit()