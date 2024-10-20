import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from config import DB_CONFIG
from gui.add_transaction import AddTransactionWindow
from PIL import Image, ImageTk

class ViewTransactionsWindow:
    def __init__(self, parent, refresh_callback):
        self.parent = parent
        self.refresh_callback = refresh_callback

        # Set the style
        style = ttk.Style()
        style.theme_use('clam')  # You can use 'clam', 'alt', 'default', or 'classic'
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 14, 'bold'))
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 14))
        style.configure('TEntry', font=('Arial', 14))
        style.configure('Treeview', font=('Arial', 14), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 14, 'bold'))

        # Load icons
        self.filter_icon = self.load_icon("icons/filter.png", (20, 20))
        self.edit_icon = self.load_icon("icons/edit.png", (20, 20))
        self.delete_icon = self.load_icon("icons/delete.png", (20, 20))

        # Create a frame for the filter options
        filter_frame = ttk.LabelFrame(self.parent, text="Filter Options", padding="10 10 10 10")
        filter_frame.pack(fill=tk.X, expand=True)

        # Type Filter
        self.type_label = ttk.Label(filter_frame, text="Type:")
        self.type_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(filter_frame)
        self.type_var.set("all")  # default value
        self.type_option = ttk.OptionMenu(filter_frame, self.type_var, "all", "all", "income", "expense", command=self.update_category_options)
        self.type_option.grid(row=0, column=1, pady=5)

        # Category Filter
        self.category_label = ttk.Label(filter_frame, text="Category:")
        self.category_label.grid(row=0, column=2, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(filter_frame)
        self.category_option = ttk.OptionMenu(filter_frame, self.category_var, "all")
        self.category_option.grid(row=0, column=3, pady=5)

        self.update_category_options()

        # Start Date Filter
        self.start_date_label = ttk.Label(filter_frame, text="Start Date:")
        self.start_date_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_date_entry = DateEntry(filter_frame, date_pattern='dd/mm/yyyy', width=20)
        self.start_date_entry.grid(row=1, column=1, pady=5)

        # End Date Filter
        self.end_date_label = ttk.Label(filter_frame, text="End Date:")
        self.end_date_label.grid(row=1, column=2, sticky=tk.W, pady=5)
        self.end_date_entry = DateEntry(filter_frame, date_pattern='dd/mm/yyyy', width=20)
        self.end_date_entry.grid(row=1, column=3, pady=5)

        # Filter Button
        self.filter_button = ttk.Button(filter_frame, text="Filter", image=self.filter_icon, compound=tk.LEFT, command=self.apply_filter)
        self.filter_button.grid(row=2, columnspan=4, pady=10)

        # Create a frame for the transactions list
        transactions_frame = ttk.Frame(self.parent, padding="10 10 10 10")
        transactions_frame.pack(fill=tk.BOTH, expand=True)

        # Create a Treeview widget for displaying transactions
        self.transactions_tree = ttk.Treeview(transactions_frame, columns=("Title", "Amount", "Type", "Category", "Date"), show='headings')
        self.transactions_tree.heading("Title", text="Title", command=lambda: self.sort_data("Title"))
        self.transactions_tree.heading("Amount", text="Amount", command=lambda: self.sort_data("Amount"))
        self.transactions_tree.heading("Type", text="Type", command=lambda: self.sort_data("Type"))
        self.transactions_tree.heading("Category", text="Category", command=lambda: self.sort_data("Category"))
        self.transactions_tree.heading("Date", text="Date", command=lambda: self.sort_data("Date"))
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add Edit and Delete buttons
        buttons_frame = ttk.Frame(self.parent, padding="10 10 10 10")
        buttons_frame.pack(fill=tk.X, expand=True)
        edit_button = ttk.Button(buttons_frame, text="Edit", image=self.edit_icon, compound=tk.LEFT, command=self.edit_transaction)
        edit_button.pack(side=tk.LEFT, padx=5)
        delete_button = ttk.Button(buttons_frame, text="Delete", image=self.delete_icon, compound=tk.LEFT, command=self.delete_transaction)
        delete_button.pack(side=tk.LEFT, padx=5)

        # Load transactions
        self.load_transactions()

    def load_icon(self, path, size):
        image = Image.open(path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def load_transactions(self):
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT title, amount, type, category, date FROM transactions ORDER BY date DESC")
        transactions = cursor.fetchall()
        cursor.close()
        conn.close()

        for (title, amount, type, category, date) in transactions:
            self.transactions_tree.insert("", "end", values=(title, amount, type, category, date))

    def update_category_options(self, *args):
        menu = self.category_option["menu"]
        menu.delete(0, "end")

        if self.type_var.get() == "income":
            categories = ["all", "salary", "investment", "etc"]
        elif self.type_var.get() == "expense":
            categories = ["all", "food", "study", "work", "exercise", "leisure", "etc"]
        else:
            categories = ["all"]

        for category in categories:
            menu.add_command(label=category, command=lambda value=category: self.category_var.set(value))

        self.category_var.set(categories[0])

    def apply_filter(self):
        type_filter = self.type_var.get()
        category_filter = self.category_var.get()
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()

        # Validate that start date is not greater than end date
        if start_date > end_date:
            messagebox.showerror("Error", "Start date cannot be greater than end date.")
            return
        
        start_date = self.start_date_entry.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date_entry.get_date().strftime("%Y-%m-%d")

        query = "SELECT title, amount, type, category, date FROM transactions WHERE date BETWEEN %s AND %s"
        params = [start_date, end_date]

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

        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        for (title, amount, type, category, date) in transactions:
            self.transactions_tree.insert("", "end", values=(title, amount, type, category, date))

    def sort_data(self, column):
        data = [(self.transactions_tree.set(child, column), child) for child in self.transactions_tree.get_children('')]

        if column == "Amount":
            data.sort(key=lambda t: float(t[0]), reverse=False)
        else:
            data.sort(reverse=False)

        for index, (val, child) in enumerate(data):
            self.transactions_tree.move(child, '', index)

        self.transactions_tree.heading(column, command=lambda: self.sort_data_reverse(column))

    def sort_data_reverse(self, column):
        data = [(self.transactions_tree.set(child, column), child) for child in self.transactions_tree.get_children('')]

        if column == "Amount":
            data.sort(key=lambda t: float(t[0]), reverse=True)
        else:
            data.sort(reverse=True)

        for index, (val, child) in enumerate(data):
            self.transactions_tree.move(child, '', index)

        self.transactions_tree.heading(column, command=lambda: self.sort_data(column))

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
        type_var = tk.StringVar(edit_window)
        type_var.set(values[2])
        type_option = ttk.OptionMenu(edit_window, type_var, values[2], "income", "expense", command=lambda _: AddTransactionWindow.update_category_options(type_var, category_var, category_option))
        type_option.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(edit_window, text="Category").grid(row=3, column=0, padx=10, pady=5)
        category_var = tk.StringVar(edit_window)
        category_option = ttk.OptionMenu(edit_window, category_var, values[3])
        category_option.grid(row=3, column=1, padx=10, pady=5)

        AddTransactionWindow.update_category_options(type_var, category_var, category_option, initial_category=values[3])

        tk.Label(edit_window, text="Date").grid(row=4, column=0, padx=10, pady=5)
        date_entry = tk.Entry(edit_window)
        date_entry.grid(row=4, column=1, padx=10, pady=5)
        date_entry.insert(0, values[4])

        save_button = tk.Button(edit_window, text="Save", command=lambda: self.save_transaction(item_id, title_entry.get(), amount_entry.get(), type_var.get(), category_var.get(), date_entry.get(), edit_window))
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
        self.refresh_callback()

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
            self.refresh_callback()