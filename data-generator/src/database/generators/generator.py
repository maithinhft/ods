from psycopg import Connection
import psycopg

class Generator:

    def __init__(self, conn: Connection):
        self.conn = conn

    def generate(self) -> None:
        pass