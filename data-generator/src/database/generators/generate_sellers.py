import random
from database.generators.generator import Generator
import logging


class Selgenerator(Generator):

    def __init__(self, conn):
        super().__init__(conn)

        self.conn = conn
    
    def generate(self):
        logging.basicConfig(level=logging.DEBUG)
        
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT count(*) FROM geolocation")
            logging.info("Selected number of geolocations!")
        
        except Exception as e:
            logging.error(f"Error occur while select number of geolocations! {e}")
        
        number_of_geolocations = cur.fetchall()[0][0]
        offset = random.randint(0, number_of_geolocations-1)

        try:
            cur.execute(
                f"""
                    SELECT geolocation_city, geolocation_state
                    FROM geolocation
                    OFFSET {offset}
                    LIMIT 1;
                """
            )
            logging.info("Selected city and state of seller!")
        
        except Exception as e:
            logging.error(f"Error occur while select city and state of seller! {e}")
    
        seller_city, seller_state = cur.fetchall()[0]

        try:
            cur.execute(
                f"""
                    SELECT max(seller_id) FROM sellers;
                """
            )
            logging.info("Selected max customer_id of sellers table!")
        
        except Exception as e:
            logging.error(f"Error occur while select max seller_id of sellers table! {e}")
        
        seller_id = cur.fetchall()[0][0] + 1

        try:
            cur.execute(
                f"""
                    INSERT INTO sellers(seller_id, seller_city, seller_state)
                    VALUES ({seller_id}, '{seller_city}', '{seller_state}')
                """
            )
            logging.info("Insert seller record to sellers table!")
        except Exception as e:
            logging.error(f"Error occur while insert seller record to sellers table! {e}")
        
        cur.close()
        self.conn.commit()