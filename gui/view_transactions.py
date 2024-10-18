import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DB_CONFIG

class ViewTransactionsWindow:
    def __init__(self, parent, refresh_charts_callback):
        self.parent = parent
        self.refresh_charts_callback = refresh_charts_callback

        # Set the style
        style = ttk.Style()
        style.configure('Treeview', font=('Arial', 12), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

        # Create a frame for the transactions list
        transactions_frame = ttk.Frame(self.parent, padding="10 10 10 10")
        transactions_frame.pack(fill=tk.BOTH, expand=True)

        # Create a Treeview widget for displaying transactions
        self.transactions_tree = ttk.Treeview(transactions_frame, columns=("Title", "Amount", "Type", "Category", "Date"), show='headings')
        self.transactions_tree.heading("Title", text="Title")
        self.transactions_tree.heading("Amount", text="Amount")
        self.transactions_tree.heading("Type", text="Type")
        self.transactions_tree.heading("Category", text="Category")
        self.transactions_tree.heading("Date", text="Date")
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add Edit and Delete buttons
        buttons_frame = ttk.Frame(self.parent, padding="10 10 10 10")
        buttons_frame.pack(fill=tk.X, expand=True)
        edit_button = ttk.Button(buttons_frame, text="Edit", command=self.edit_transaction)
        edit_button.pack(side=tk.LEFT, padx=5)
        delete_button = ttk.Button(buttons_frame, text="Delete", command=self.delete_transaction)
        delete_button.pack(side=tk.LEFT, padx=5)

        # Load transactions
        self.load_transactions()

    def load_transactions(self):
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT title, amount, type, category, date FROM transactions")
        for (title, amount, type, category, date) in cursor:
            self.transactions_tree.insert("", "end", values=(title, amount, type, category, date))
        cursor.close()
        conn.close()

    def edit_transaction(self):
        selected_item = self.transactions_tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a transaction to edit.")
            return

        item = self.transactions_tree.item(selected_item)
        values = item['values']
        self.open_edit_window(values, selected_item)

    def open_edit_window(self, values, item_id):
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Transaction")

        tk.Label(edit_window, text="Title").grid(row=0, column=0, padx=10, pady=5)
        title_entry = tk.Entry(edit_window)
        title_entry.grid(row=0, column=1, padx=10, pady=5)
        title_entry.insert(0, values[0])

        tk.Label(edit_window, text="Amount").grid(row=1, column=0, padx=10, pady=5)
        amount_entry = tk.Entry(edit_window)
        amount_entry.grid(row=1, column=1, padx=10, pady=5)
        amount_entry.insert(0, values[1])

        tk.Label(edit_window, text="Type").grid(row=2, column=0, padx=10, pady=5)
        type_entry = tk.Entry(edit_window)
        type_entry.grid(row=2, column=1, padx=10, pady=5)
        type_entry.insert(0, values[2])

        tk.Label(edit_window, text="Category").grid(row=3, column=0, padx=10, pady=5)
        category_entry = tk.Entry(edit_window)
        category_entry.grid(row=3, column=1, padx=10, pady=5)
        category_entry.insert(0, values[3])

        tk.Label(edit_window, text="Date").grid(row=4, column=0, padx=10, pady=5)
        date_entry = tk.Entry(edit_window)
        date_entry.grid(row=4, column=1, padx=10, pady=5)
        date_entry.insert(0, values[4])

        save_button = tk.Button(edit_window, text="Save", command=lambda: self.save_transaction(item_id, title_entry.get(), amount_entry.get(), type_entry.get(), category_entry.get(), date_entry.get(), edit_window))
        save_button.grid(row=5, column=0, columnspan=2, pady=10)

    def save_transaction(self, item_id, title, amount, type, category, date, edit_window):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE transactions SET title=%s, amount=%s, type=%s, category=%s, date=%s WHERE title=%s", (title, amount, type, category, date, self.transactions_tree.item(item_id)['values'][0]))
        conn.commit()
        cursor.close()
        conn.close()

        self.transactions_tree.item(item_id, values=(title, amount, type, category, date))
        edit_window.destroy()
        messagebox.showinfo("Updated", "Transaction updated successfully.")
        self.refresh_charts_callback()

    def delete_transaction(self):
        selected_item = self.transactions_tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a transaction to delete.")
            return

        item = self.transactions_tree.item(selected_item)
        values = item['values']
        title = values[0]

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the transaction '{title}'?")
        if confirm:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE title = %s", (title,))
            conn.commit()
            cursor.close()
            conn.close()
            self.transactions_tree.delete(selected_item)
            messagebox.showinfo("Deleted", f"Transaction '{title}' deleted successfully.")
            self.refresh_charts_callback()