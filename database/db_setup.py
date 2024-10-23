import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def initialize_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            cursor = conn.cursor()

            # Create the users table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
            """)

            # Create the transactions table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                type VARCHAR(50) NOT NULL,
                category VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)

            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully.")
        else:
            print("Failed to connect to the database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()
            print("Database connection closed.")
