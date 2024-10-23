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
        cursor.execute("INSERT INTO transactions (title, amount, type, category, date, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                       (self.title, self.amount, self.type, self.category, self.date, self.user_id))
        conn.commit()
        cursor.close()
        conn.close()

    def update(self, original_title):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE transactions SET title=%s, amount=%s, type=%s, category=%s, date=%s WHERE title=%s AND user_id=%s", 
                       (self.title, self.amount, self.type, self.category, self.date, original_title, self.user_id))
        conn.commit()
        cursor.close()
        conn.close()

    def delete(self):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE title = %s AND user_id = %s", (self.title, self.user_id))
        conn.commit()
        cursor.close()
        conn.close()

def fetch_data(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT type, category, SUM(amount) 
    FROM transactions 
    WHERE user_id = %s
    GROUP BY type, category
    """, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def fetch_monthly_data(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT type, DATE_FORMAT(date, '%Y-%m') as month, SUM(amount) 
    FROM transactions 
    WHERE user_id = %s
    GROUP BY type, month
    """, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def update_financial_info(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Total Income
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income' AND user_id = %s", (user_id,))
    total_income = cursor.fetchone()[0] or 0

    # Total Expenses
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense' AND user_id = %s", (user_id,))
    total_expenses = cursor.fetchone()[0] or 0

    # Balance
    balance = total_income - total_expenses

    # Max Income
    cursor.execute("SELECT MAX(amount) FROM transactions WHERE type='income' AND user_id = %s", (user_id,))
    max_income = cursor.fetchone()[0] or 0

    # Max Expense
    cursor.execute("SELECT MAX(amount) FROM transactions WHERE type='expense' AND user_id = %s", (user_id,))
    max_expense = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "max_income": max_income,
        "max_expense": max_expense
}

def load_transactions(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT title, amount, type, category, date FROM transactions WHERE user_id = %s ORDER BY date DESC", (user_id,))
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return transactions

def apply_filter(user_id, type_filter, category_filter, start_date, end_date):
    query = "SELECT title, amount, type, category, date FROM transactions WHERE user_id = %s AND date BETWEEN %s AND %s"
    params = [user_id, start_date, end_date]

    if type_filter != "all":
        query += " AND type = %s"
        params.append(type_filter)

        if category_filter != "all":
            query += " AND category = %s"
            params.append(category_filter)

    query += " ORDER BY date DESC"

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return transactions

def update_category_options(type_var, category_var, category_option, initial_category=None):
    menu = category_option["menu"]
    menu.delete(0, "end")

    if type_var.get() == "income":
        categories = ["salary", "investment", "etc"]
    else:
        categories = ["food", "study", "work", "exercise", "leisure", "etc"]

    for category in categories:
        menu.add_command(label=category, command=lambda value=category: category_var.set(value))

    if initial_category:
        category_var.set(initial_category)
    else:
        category_var.set(categories[0])