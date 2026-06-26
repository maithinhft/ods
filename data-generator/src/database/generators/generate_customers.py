import random
from database.generators.generator import Generator
import logging


class Cusgenerator(Generator):

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
            logging.info("Selected city and state of customer!")
        
        except Exception as e:
            logging.error(f"Error occur while select city and state of customer! {e}")
    
        customer_city, customer_state = cur.fetchone()

        try:
            cur.execute(
                f"""
                    SELECT max(customer_id) FROM customers;
                """
            )
            logging.info("Selected max customer_id of customers table!")
        
        except Exception as e:
            logging.error(f"Error occur while select max customer_id of customers table! {e}")
        
        customer_id = cur.fetchall()[0][0] + 1

        try:
            cur.execute(
                f"""
                    INSERT INTO customers(customer_id, customer_city, customer_state)
                    VALUES ({customer_id}, '{customer_city}', '{customer_state}')
                """
            )
            logging.info("Insert customer record to customers table!")
        except Exception as e:
            logging.error(f"Error occur while insert customer record to customers table! {e}")
        
        cur.close()
        self.conn.commit()