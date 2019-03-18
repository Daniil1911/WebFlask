from flask import Flask
from config import Configuration
import sqlite3


app = Flask(__name__)
app.config.from_object(Configuration)

class DB:
    def __init__(self):
        conn = sqlite3.connect('123.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()

db = DB()

