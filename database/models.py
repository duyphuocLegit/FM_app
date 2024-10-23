import mysql.connector
from config import DB_CONFIG

class Transaction:
    def __init__(self, title, amount, type, category, date, user_id):
        self.title = title
        self.user_id = user_id
        self.amount = amount
        self.type = type
        self.category = category
        self.date = date

    def save(self):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (title, user_id, amount, type, category, date) VALUES (%s, %s, %s, %s, %s, %s)",
                       (self.title, self.user_id, self.amount, self.type, self.category, self.date))
        conn.commit()
        cursor.close()
        conn.close()