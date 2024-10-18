import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database.models import Transaction
from datetime import datetime

class AddTransactionWindow:
    def __init__(self, parent, refresh_charts_callback):
        self.parent = parent
        self.refresh_charts_callback = refresh_charts_callback

        # Title
        self.title_label = ttk.Label(self.parent, text="Title")
        self.title_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(self.parent, width=30)
        self.title_entry.grid(row=0, column=1, pady=5)

        # Amount
        self.amount_label = ttk.Label(self.parent, text="Amount")
        self.amount_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.amount_entry = ttk.Entry(self.parent, width=30)
        self.amount_entry.grid(row=1, column=1, pady=5)

        # Type
        self.type_label = ttk.Label(self.parent, text="Type")
        self.type_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(self.parent)
        self.type_var.set("income")  # default value
        self.type_option = ttk.OptionMenu(self.parent, self.type_var, "income", "income", "expense", command=lambda _: AddTransactionWindow.update_category_options(self.type_var, self.category_var, self.category_option))
        self.type_option.grid(row=2, column=1, pady=5)

        # Category
        self.category_label = ttk.Label(self.parent, text="Category")
        self.category_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(self.parent)
        self.category_option = ttk.OptionMenu(self.parent, self.category_var, "salary")
        self.category_option.grid(row=3, column=1, pady=5)

        AddTransactionWindow.update_category_options(self.type_var, self.category_var, self.category_option)

        # Date
        self.date_label = ttk.Label(self.parent, text="Date")
        self.date_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.date_entry = DateEntry(self.parent, date_pattern='dd/mm/yyyy', width=27)
        self.date_entry.grid(row=4, column=1, pady=5)

        # Save Button
        self.save_button = ttk.Button(self.parent, text="Save", command=self.save_transaction)
        self.save_button.grid(row=5, columnspan=2, pady=10)

    @staticmethod
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

    def save_transaction(self):
        title = self.title_entry.get()
        amount = self.amount_entry.get()
        type = self.type_var.get()
        category = self.category_var.get()
        date_str = self.date_entry.get()

        if not title or not amount or not type or not category or not date_str:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        try:
            date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in DD/MM/YYYY format")
            return

        transaction = Transaction(title, amount, type, category, date)
        transaction.save()
        messagebox.showinfo("Success", "Transaction saved successfully")
        self.clear_add_form()
        self.refresh_charts_callback()

    def clear_add_form(self):
        self.title_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.type_var.set("income")
        self.category_var.set("salary")
        self.date_entry.set_date(None)