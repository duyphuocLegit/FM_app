import tkinter as tk
from tkinter import ttk
from gui.add_transaction import AddTransactionWindow
from gui.view_transactions import ViewTransactionsWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mysql.connector
from config import DB_CONFIG
import pandas as pd
from PIL import Image, ImageTk
import numpy as np

class MainWindow:
    def __init__(self, master, user_id):
        self.master = master
        self.user_id = user_id
        master.title("Financial Management App")
        master.geometry("1900x1000")  # Set fixed window size

        # Set the style
        style = ttk.Style()
        style.theme_use('clam')  # You can use 'clam', 'alt', 'default', or 'classic'
        style.configure('TFrame', font=('Arial', 16))
        style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 16, 'bold'))
        style.configure('TLabel', font=('Arial', 16))
        style.configure('TEntry', font=('Arial', 16))

        # Handle window close event
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a notebook for tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Load and resize icons
        self.overview_icon = self.load_icon("icons/overview.png", (20, 20))
        self.view_icon = self.load_icon("icons/view.png", (20, 20))
        self.add_icon = self.load_icon("icons/add.png", (20, 20))

        # Create frames for each tab
        self.overview_frame = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.view_frame = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.add_frame = ttk.Frame(self.notebook, padding="10 10 10 10")

        # Add frames to notebook with icons
        self.notebook.add(self.overview_frame, text="Overview", image=self.overview_icon, compound=tk.LEFT)
        self.notebook.add(self.view_frame, text="View Transactions", image=self.view_icon, compound=tk.LEFT)
        self.notebook.add(self.add_frame, text="Add Transaction", image=self.add_icon, compound=tk.LEFT)

        # Initialize each tab
        self.init_overview_tab()
        self.init_view_tab()
        self.init_add_tab()

    def load_icon(self, path, size):
        image = Image.open(path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def init_overview_tab(self):
        # Financial Information Frame
        info_frame = ttk.LabelFrame(self.overview_frame, text="Financial Information", padding="10 10 10 10")
        info_frame.pack(fill=tk.X, expand=True, padx=10, pady=10)

        self.total_income_label = ttk.Label(info_frame, text="Total Income:")
        self.total_income_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.total_income_value = ttk.Label(info_frame, text="", font=('Arial', 16, 'bold'))
        self.total_income_value.grid(row=0, column=1, pady=5, padx=25)

        self.total_expenses_label = ttk.Label(info_frame, text="Total Expenses:")
        self.total_expenses_label.grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.total_expenses_value = ttk.Label(info_frame, text="", font=('Arial', 16, 'bold'))
        self.total_expenses_value.grid(row=0, column=3, pady=5, padx=25)

        self.balance_label = ttk.Label(info_frame, text="Balance:")
        self.balance_label.grid(row=0, column=4, sticky=tk.W, pady=5, padx=5)
        self.balance_value = ttk.Label(info_frame, text="", font=('Arial', 16, 'bold'))
        self.balance_value.grid(row=0, column=5, pady=5, padx=25)

        self.max_income_label = ttk.Label(info_frame, text="Max Income:")
        self.max_income_label.grid(row=0, column=6, sticky=tk.W, pady=5, padx=5)
        self.max_income_value = ttk.Label(info_frame, text="", font=('Arial', 16, 'bold'))
        self.max_income_value.grid(row=0, column=7, pady=5, padx=25)

        self.max_expense_label = ttk.Label(info_frame, text="Max Expense:")
        self.max_expense_label.grid(row=0, column=8, sticky=tk.W, pady=5, padx=5)
        self.max_expense_value = ttk.Label(info_frame, text="", font=('Arial', 16, 'bold'))
        self.max_expense_value.grid(row=0, column=9, pady=5, padx=25)

        # Canvas for Charts
        self.canvas_frame = ttk.LabelFrame(self.overview_frame, text="Charts", padding="10 10 10 10")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Show Charts on startup
        self.show_charts()

    def init_view_tab(self):
        ViewTransactionsWindow(self.view_frame, self.refresh_data, self.user_id)

    def init_add_tab(self):
        AddTransactionWindow(self.add_frame, self.refresh_data, self.user_id)

    def show_charts(self):
        data = self.fetch_data()
        income_data = [item for item in data if item[0] == 'income']
        expense_data = [item for item in data if item[0] == 'expense']

        income_labels = [item[1] for item in income_data]
        income_sizes = [item[2] for item in income_data]

        expense_labels = [item[1] for item in expense_data]
        expense_sizes = [item[2] for item in expense_data]

        monthly_data = self.fetch_monthly_data()
        df = pd.DataFrame(monthly_data, columns=['type', 'month', 'amount'])

        income_monthly_data = df[df['type'] == 'income']
        expense_monthly_data = df[df['type'] == 'expense']

        fig_income, ax_income = plt.subplots(figsize=(6, 4))
        fig_expense, ax_expense = plt.subplots(figsize=(6, 4))
        fig_bar, ax_bar = plt.subplots(figsize=(10, 6))

        # Pie Chart for Income
        ax_income.pie(income_sizes, labels=income_labels, autopct='%1.1f%%', startangle=160, colors=plt.cm.Paired.colors)
        ax_income.set_title('Income by Category')

        # Pie Chart for Expense
        ax_expense.pie(expense_sizes, labels=expense_labels, autopct='%1.1f%%', startangle=160, colors=plt.cm.Paired.colors)
        ax_expense.set_title('Expense by Category')

        # Bar Chart for Monthly Income vs Expense
        months = sorted(df['month'].unique())
        bar_width = 0.35
        index = np.arange(len(months))

        income_amounts = income_monthly_data.set_index('month')['amount'].reindex(months, fill_value=0).tolist()
        expense_amounts = expense_monthly_data.set_index('month')['amount'].reindex(months, fill_value=0).tolist()

        ax_bar.bar(index, income_amounts, bar_width, label='Income', color='green')
        ax_bar.bar(index + bar_width, expense_amounts, bar_width, label='Expense', color='red')

        ax_bar.set_xlabel('Month')
        ax_bar.set_ylabel('Amount')
        ax_bar.set_title('Monthly Income vs Expense')
        ax_bar.set_xticks(index + bar_width / 2)
        ax_bar.set_xticklabels(months)
        ax_bar.legend()
        ax_bar.grid(True)

        fig_income.tight_layout()
        fig_expense.tight_layout()
        fig_bar.tight_layout()

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Add Income Pie Chart
        canvas_income = FigureCanvasTkAgg(fig_income, master=self.canvas_frame)
        canvas_income.draw()
        canvas_income.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

        # Add Expense Pie Chart
        canvas_expense = FigureCanvasTkAgg(fig_expense, master=self.canvas_frame)
        canvas_expense.draw()
        canvas_expense.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

        # Add Bar Chart
        canvas_bar = FigureCanvasTkAgg(fig_bar, master=self.canvas_frame)
        canvas_bar.draw()
        canvas_bar.get_tk_widget().grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky='nsew')

        # Configure column weights
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(1, weight=3)

        # Update financial information
        self.update_financial_info()

    def fetch_data(self):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT type, category, SUM(amount) 
        FROM transactions 
        WHERE user_id = %s
        GROUP BY type, category
        """, (self.user_id,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def fetch_monthly_data(self):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT type, DATE_FORMAT(date, '%Y-%m') as month, SUM(amount) 
        FROM transactions 
        WHERE user_id = %s
        GROUP BY type, month
        """, (self.user_id,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def update_financial_info(self):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Total Income
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income' AND user_id = %s", (self.user_id,))
        total_income = cursor.fetchone()[0] or 0
        self.total_income_value.config(text=f"{total_income:.2f}")

        # Total Expenses
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense' AND user_id = %s", (self.user_id,))
        total_expenses = cursor.fetchone()[0] or 0
        self.total_expenses_value.config(text=f"{total_expenses:.2f}")

        # Balance
        balance = total_income - total_expenses
        self.balance_value.config(text=f"{balance:.2f}")

        # Max Income
        cursor.execute("SELECT MAX(amount) FROM transactions WHERE type='income' AND user_id = %s", (self.user_id,))
        max_income = cursor.fetchone()[0] or 0
        self.max_income_value.config(text=f"{max_income:.2f}")

        # Max Expense
        cursor.execute("SELECT MAX(amount) FROM transactions WHERE type='expense' AND user_id = %s", (self.user_id,))
        max_expense = cursor.fetchone()[0] or 0
        self.max_expense_value.config(text=f"{max_expense:.2f}")

        cursor.close()
        conn.close()

    def refresh_data(self):
        self.show_charts()

    def on_closing(self):
        self.master.quit()
        self.master.destroy()