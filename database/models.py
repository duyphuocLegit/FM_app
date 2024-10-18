import mysql.connector
from config import DB_CONFIG

class Transaction:
    def __init__(self, title, amount, type, category, date):
        self.title = title
        self.amount = amount
        self.type = type
        self.category = category
        self.date = date

    def save(self):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (title, amount, type, category, date) VALUES (%s, %s, %s, %s, %s)",
                       (self.title, self.amount, self.type, self.category, self.date))
        conn.commit()
        cursor.close()
        conn.close()