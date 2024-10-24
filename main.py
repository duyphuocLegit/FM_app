import tkinter as tk
from gui.main_window import MainWindow
from gui.login_window import LoginWindow
from database.db_setup import initialize_db

def main():
    initialize_db()
    root = tk.Tk()
    login_window = LoginWindow(root, on_login_success=lambda user_id: open_main_window(root, user_id))
    root.mainloop()

def open_main_window(root, user_id):
    root.destroy()
    main_root = tk.Tk()
    main_root.state('zoomed')  # Maximize the window
    MainWindow(main_root, user_id)
    main_root.protocol("WM_DELETE_WINDOW", main_root.quit)  # Ensure the app quits completely
    main_root.mainloop()

if __name__ == "__main__":
    main()