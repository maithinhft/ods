from datetime import datetime, timedelta

from database.generators.generator import Generator
import random
import logging

class Revgenerator(Generator):

    def __init__(self, conn):
        super().__init__(conn)

        self.conn = conn
    
    def generate(self, 
                 order_id: int, 
                 delivered_date: datetime):
        logging.basicConfig(level=logging.DEBUG)
        cur = self.conn.cursor()

        review_score = random.randint(1, 5)
        cur.execute(
            """
            SELECT max(review_id) FROM order_reviews;
            """
        )

        max_review_id = cur.fetchall()[0][0]
        if max_review_id is None:
            review_id = 0
        else:
            review_id = max_review_id + 1
        
        creation_offset_minutes = random.randint(5, 60)
        review_creation_date = delivered_date + timedelta(minutes=creation_offset_minutes)

        answer_offset_minutes = random.randint(5, 60)
        review_answer_timestamp = review_creation_date + timedelta(minutes=answer_offset_minutes)
        
        try:
            cur.execute(
                f"""
                INSERT INTO order_reviews(
                    review_id,
                    order_id,
                    review_score,
                    review_comment_title,
                    review_comment_message,
                    review_creation_date,
                    review_answer_timestamp
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (review_id, order_id, review_score, None, None, review_creation_date, review_answer_timestamp)
            )
            logging.info("Insert order record to order_reviews table successful!")
        except Exception as e:
            logging.error(f"Error occur while insert order record to order_reviews table! {e}")