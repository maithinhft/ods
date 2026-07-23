from datetime import datetime, timedelta

from database.generators.generator import Generator
import random
import logging

class Revgenerator(Generator):

    def __init__(self, conn):
        super().__init__(conn)
        self.conn = conn

        # Use counter instead of SELECT max() every time
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(max(review_id), -1) FROM order_reviews")
        self._next_id = cur.fetchone()[0] + 1
        cur.close()
    
    def generate(self, 
                 order_id: int, 
                 delivered_date: datetime):
        cur = self.conn.cursor()

        review_score = random.randint(1, 5)
        review_id = self._next_id
        self._next_id += 1
        
        creation_offset_minutes = random.randint(5, 60)
        review_creation_date = delivered_date + timedelta(minutes=creation_offset_minutes)

        answer_offset_minutes = random.randint(5, 60)
        review_answer_timestamp = review_creation_date + timedelta(minutes=answer_offset_minutes)
        
        try:
            cur.execute(
                """
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
        except Exception as e:
            logging.error(f"Error inserting order_review record: {e}")
        
        cur.close()