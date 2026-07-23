import random
from database.generators.generator import Generator
import logging


class Selgenerator(Generator):

    def __init__(self, conn):
        super().__init__(conn)
        self.conn = conn

        # Cache all geolocations in memory instead of OFFSET random LIMIT 1
        cur = conn.cursor()
        cur.execute("SELECT geolocation_city, geolocation_state FROM geolocation")
        self._geolocations = cur.fetchall()

        # Use counter instead of SELECT max() every time
        cur.execute("SELECT COALESCE(max(seller_id), -1) FROM sellers")
        self._next_id = cur.fetchone()[0] + 1
        cur.close()
    
    def generate(self):
        cur = self.conn.cursor()
        seller_city, seller_state = random.choice(self._geolocations)
        seller_id = self._next_id
        self._next_id += 1

        try:
            cur.execute(
                "INSERT INTO sellers(seller_id, seller_city, seller_state) VALUES (%s, %s, %s)",
                (seller_id, seller_city, seller_state)
            )
        except Exception as e:
            logging.error(f"Error inserting seller record: {e}")
        
        cur.close()
        self.conn.commit()