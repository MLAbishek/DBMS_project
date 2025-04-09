import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Enhanced color scheme
COLORS = {
    "primary": "#1976D2",  # Rich Blue
    "secondary": "#388E3C",  # Forest Green
    "accent": "#FFA000",  # Gold
    "warning": "#D32F2F",  # Red
    "bg": "#F5F5F5",  # Light Gray
    "text": "#212121",  # Dark Gray
    "light_text": "#757575",  # Medium Gray
    "white": "#FFFFFF",  # White
}

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "abishek@123",
    "auth_plugin": "mysql_native_password",
}

# Database setup
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(buffered=True)

    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS banking_system")
    cursor.execute("USE banking_system")

    # Create tables
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(20),
        balance DECIMAL(10,2) DEFAULT 0.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS transactions (
        trans_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        type VARCHAR(50),
        amount DECIMAL(10,2),
        balance DECIMAL(10,2),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )"""
    )

    conn.commit()

except Error as e:
    messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
    exit(1)


class ModernBankingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Banking System")
        self.root.geometry("1200x800")

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.setup_styles()

        self.current_user = None
        self.setup_welcome_screen()

        # Add clock
        self.clock_label = ttk.Label(root, style="Clock.TLabel")
        self.clock_label.place(relx=1.0, y=10, anchor="ne", x=-10)
        self.update_clock()

    def setup_styles(self):
        # Configure custom styles
        self.style.configure("Main.TFrame", background=COLORS["bg"])
        self.style.configure(
            "Header.TLabel",
            font=("Helvetica", 24, "bold"),
            foreground=COLORS["primary"],
            background=COLORS["bg"],
        )
        self.style.configure(
            "SubHeader.TLabel",
            font=("Helvetica", 14),
            foreground=COLORS["light_text"],
            background=COLORS["bg"],
        )
        self.style.configure(
            "Clock.TLabel",
            font=("Helvetica", 12),
            foreground=COLORS["primary"],
            background=COLORS["bg"],
        )
        self.style.configure(
            "Card.TFrame", background=COLORS["white"], relief="raised", borderwidth=1
        )
        self.style.configure("Action.TButton", font=("Helvetica", 11), padding=10)

    def update_clock(self):
        time_string = datetime.now().strftime("%I:%M:%S %p")
        self.clock_label.config(text=time_string)
        self.root.after(1000, self.update_clock)

    def setup_welcome_screen(self):
        self.clear_window()

        # Main container
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Welcome text
        welcome_frame = ttk.Frame(main_frame, style="Main.TFrame")
        welcome_frame.place(relx=0.5, rely=0.3, anchor="center")

        ttk.Label(
            welcome_frame, text="Welcome to Modern Banking", style="Header.TLabel"
        ).pack()

        ttk.Label(
            welcome_frame,
            text="Your Secure Financial Partner",
            style="SubHeader.TLabel",
        ).pack(pady=10)

        # Buttons frame
        button_frame = ttk.Frame(welcome_frame, style="Main.TFrame")
        button_frame.pack(pady=40)

        ttk.Button(
            button_frame,
            text="Login",
            style="Action.TButton",
            command=self.show_login_screen,
            width=20,
        ).pack(pady=5)

        ttk.Button(
            button_frame,
            text="Create Account",
            style="Action.TButton",
            command=self.show_register_screen,
            width=20,
        ).pack(pady=5)

    def show_login_screen(self):
        self.clear_window()

        # Main container with card effect
        login_card = ttk.Frame(self.root, style="Card.TFrame")
        login_card.place(relx=0.5, rely=0.4, anchor="center")

        # Header
        ttk.Label(login_card, text="Login to Your Account", style="Header.TLabel").pack(
            pady=20, padx=40
        )

        # Login form
        form_frame = ttk.Frame(login_card)
        form_frame.pack(padx=40, pady=20)

        ttk.Label(form_frame, text="Username").pack(anchor="w")
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.pack(pady=(0, 10), fill="x")

        ttk.Label(form_frame, text="Password").pack(anchor="w")
        self.password_entry = ttk.Entry(form_frame, show="•", width=30)
        self.password_entry.pack(pady=(0, 20), fill="x")

        # Buttons
        ttk.Button(
            form_frame, text="Login", style="Action.TButton", command=self.login
        ).pack(fill="x", pady=5)

        ttk.Button(
            form_frame,
            text="Back",
            style="Action.TButton",
            command=self.setup_welcome_screen,
        ).pack(fill="x", pady=5)

    def setup_dashboard(self):
        self.clear_window()

        # Create main container
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Header with user info
        header_frame = ttk.Frame(main_frame, style="Card.TFrame")
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            header_frame,
            text=f"Welcome back, {self.current_user[2]}",
            style="Header.TLabel",
        ).pack(side="left", padx=20, pady=10)

        # Balance display
        balance_frame = ttk.LabelFrame(main_frame, text="Account Balance", padding=10)
        balance_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(
            balance_frame,
            text=f"Current Balance: ${self.current_user[5]:.2f}",
            font=("Helvetica", 12),
        ).pack()

        # Transaction frame
        trans_frame = ttk.LabelFrame(main_frame, text="Transactions", padding=10)
        trans_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Amount entry
        ttk.Label(trans_frame, text="Amount:").pack()
        self.amount_entry = ttk.Entry(trans_frame)
        self.amount_entry.pack(pady=5)

        # Buttons
        btn_frame = ttk.Frame(trans_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Deposit", command=self.deposit).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Withdraw", command=self.withdraw).pack(
            side="left", padx=5
        )

        # Transaction history
        ttk.Label(
            trans_frame, text="Transaction History", font=("Helvetica", 10, "bold")
        ).pack(pady=10)

        # Create treeview for transaction history
        self.trans_tree = ttk.Treeview(
            trans_frame,
            columns=("Type", "Amount", "Balance", "Date"),
            show="headings",
            height=10,
        )
        self.trans_tree.heading("Type", text="Type")
        self.trans_tree.heading("Amount", text="Amount")
        self.trans_tree.heading("Balance", text="Balance")
        self.trans_tree.heading("Date", text="Date")
        self.trans_tree.pack(pady=10, fill="both", expand=True)

        # Logout button
        ttk.Button(self.root, text="Logout", command=self.logout).pack(pady=20)

        self.refresh_transaction_history()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password),
        )
        user = cursor.fetchone()

        if user:
            self.current_user = user
            self.setup_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def show_register_screen(self):
        self.clear_window()

        register_frame = ttk.LabelFrame(
            self.root, text="Register New Account", padding=20
        )
        register_frame.place(relx=0.5, rely=0.4, anchor="center")

        fields = [
            ("Username:", "username"),
            ("Password:", "password"),
            ("Name:", "name"),
            ("Phone:", "phone"),
        ]

        self.register_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(register_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(register_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.register_entries[key] = entry

        ttk.Button(
            register_frame, text="Create Account", command=self.create_account
        ).grid(row=len(fields), column=0, columnspan=2, pady=20)
        ttk.Button(
            register_frame, text="Back to Login", command=self.show_login_screen
        ).grid(row=len(fields) + 1, column=0, columnspan=2)

    def create_account(self):
        try:
            username = self.register_entries["username"].get()
            password = self.register_entries["password"].get()
            name = self.register_entries["name"].get()
            phone = self.register_entries["phone"].get()

            cursor.execute(
                """
                INSERT INTO users (username, password, name, phone)
                VALUES (%s, %s, %s, %s)
            """,
                (username, password, name, phone),
            )
            conn.commit()

            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login_screen()
        except Error as e:
            if e.errno == 1062:  # MySQL duplicate entry error
                messagebox.showerror("Error", "Username already exists!")
            else:
                messagebox.showerror("Error", f"Database error: {e}")

    def deposit(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError

            new_balance = self.current_user[5] + amount

            cursor.execute(
                "UPDATE users SET balance = %s WHERE user_id = %s",
                (new_balance, self.current_user[0]),
            )
            try:
                cursor.execute(
                    """
                    INSERT INTO transactions (user_id, type, amount, balance)
                    VALUES (%s, 'deposit', %s, %s)
                """,
                    (self.current_user[0], amount, new_balance),
                )
                conn.commit()
            except Error as e:
                messagebox.showerror(
                    "Database Error", f"Failed to register transaction: {e}"
                )

            self.current_user = list(self.current_user)
            self.current_user[5] = new_balance

            self.refresh_transaction_history()
            self.amount_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"${amount:.2f} deposited successfully")
            self.setup_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive amount")

    def withdraw(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError
            if amount > self.current_user[5]:
                messagebox.showerror("Error", "Insufficient funds")
                return

            new_balance = self.current_user[5] - amount

            cursor.execute(
                "UPDATE users SET balance = %s WHERE user_id = %s",
                (new_balance, self.current_user[0]),
            )
            cursor.execute(
                """
                INSERT INTO transactions (user_id, type, amount, balance)
                VALUES (%s, 'withdrawal', %s, %s)
            """,
                (self.current_user[0], amount, new_balance),
            )
            conn.commit()

            self.current_user = list(self.current_user)
            self.current_user[5] = new_balance

            self.refresh_transaction_history()
            self.amount_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"${amount:.2f} withdrawn successfully")
            self.setup_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive amount")

    def refresh_transaction_history(self):
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        cursor.execute(
            """
            SELECT type, amount, balance, timestamp 
            FROM transactions 
            WHERE user_id = %s 
            ORDER BY timestamp DESC
        """,
            (self.current_user[0],),
        )

        for transaction in cursor.fetchall():
            self.trans_tree.insert("", "end", values=transaction)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def logout(self):
        self.current_user = None
        self.setup_welcome_screen()


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = ModernBankingSystem(root)
    root.mainloop()

    if conn.is_connected():
        cursor.close()
        conn.close()
