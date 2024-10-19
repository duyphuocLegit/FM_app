import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DB_CONFIG

class RegisterWindow:
    def __init__(self, master):
        self.master = master
        master.title("Register")
        master.geometry("400x250")

        # Set the style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 12, 'bold'))
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))
        style.configure('TEntry', font=('Arial', 12))

        # Handle window close event
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a frame for the registration form
        register_frame = ttk.Frame(master, padding="10 10 10 10")
        register_frame.pack(fill=tk.BOTH, expand=True)

        # Username
        self.username_label = ttk.Label(register_frame, text="Username:")
        self.username_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(register_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        # Password
        self.password_label = ttk.Label(register_frame, text="Password:")
        self.password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(register_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        # Confirm Password
        self.confirm_password_label = ttk.Label(register_frame, text="Confirm Password:")
        self.confirm_password_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confirm_password_entry = ttk.Entry(register_frame, width=30, show="*")
        self.confirm_password_entry.grid(row=2, column=1, pady=5)

        # Register Button
        self.register_button = ttk.Button(register_frame, text="Register", command=self.register)
        self.register_button.grid(row=3, columnspan=2, pady=10)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user:
            messagebox.showerror("Error", "Username already exists")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully")
            self.master.destroy()

        cursor.close()
        conn.close()

    def on_closing(self):
        self.master.destroy()