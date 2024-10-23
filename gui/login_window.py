import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DB_CONFIG
from gui.register_window import RegisterWindow
from gui.main_window import MainWindow

class LoginWindow:
    def __init__(self, master, on_login_success):
        self.master = master
        self.on_login_success = on_login_success
        master.title("Login")
        master.geometry("400x250")

        # Set the style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 14, 'bold'))
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 14))
        style.configure('TEntry', font=('Arial', 14))

        # Handle window close event
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a frame for the login form
        login_frame = ttk.Frame(master, padding="10 10 10 10")
        login_frame.pack(fill=tk.BOTH, expand=True)

        # Username
        self.username_label = ttk.Label(login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        # Password
        self.password_label = ttk.Label(login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        # Login Button
        self.login_button = ttk.Button(login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2, pady=10)

        # Register Button
        self.register_button = ttk.Button(login_frame, text="Register", command=self.open_register_window)
        self.register_button.grid(row=3, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Both fields are required")
            return

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            self.on_login_success(user[0])
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_register_window(self):
        register_root = tk.Toplevel(self.master)
        RegisterWindow(register_root)

    def on_closing(self):
        self.master.quit()
        self.master.destroy()