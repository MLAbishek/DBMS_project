import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from ttkthemes import ThemedTk
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import re
import hashlib

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


def create_db_connection():
    """Create a database connection and return connection and cursor objects"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)
        return conn, cursor
    except Error as e:
        messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
        return None, None


# Database setup
try:
    conn, cursor = create_db_connection()
    if conn and cursor:
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
            notes VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )"""
        )

        conn.commit()
        cursor.close()
        conn.close()
    else:
        messagebox.showerror("Database Error", "Failed to initialize database")
        exit(1)

except Error as e:
    messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
    exit(1)


class ModernBankingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Banking System")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)  # Set minimum window size

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

        # New styles
        self.style.configure(
            "Balance.TLabel",
            font=("Helvetica", 16, "bold"),
            foreground=COLORS["secondary"],
            background=COLORS["bg"],
        )
        self.style.configure(
            "TransactionHeader.TLabel",
            font=("Helvetica", 12, "bold"),
            foreground=COLORS["primary"],
            background=COLORS["bg"],
        )
        self.style.configure(
            "Deposit.TButton",
            background=COLORS["secondary"],
            foreground=COLORS["white"],
        )
        self.style.configure(
            "Withdraw.TButton", background=COLORS["accent"], foreground=COLORS["white"]
        )

    def update_clock(self):
        time_string = datetime.now().strftime("%I:%M:%S %p")
        date_string = datetime.now().strftime("%B %d, %Y")
        self.clock_label.config(text=f"{date_string} | {time_string}")
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
        login_card.place(relx=0.5, rely=0.4, anchor="center", width=400)

        # Header
        ttk.Label(login_card, text="Login to Your Account", style="Header.TLabel").pack(
            pady=20, padx=40
        )

        # Login form
        form_frame = ttk.Frame(login_card)
        form_frame.pack(padx=40, pady=20, fill="x")

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

        # Bind enter key to login
        self.username_entry.bind("<Return>", lambda event: self.login())
        self.password_entry.bind("<Return>", lambda event: self.login())

    def setup_dashboard(self):
        self.clear_window()

        # Create main container
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Header with user info
        header_frame = ttk.Frame(main_frame, style="Card.TFrame")
        header_frame.pack(fill="x", padx=20, pady=10)

        # Left side - User info
        user_info_frame = ttk.Frame(header_frame)
        user_info_frame.pack(side="left", padx=20, pady=10)

        ttk.Label(
            user_info_frame,
            text=f"Welcome back, {self.current_user[2]}",
            style="Header.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            user_info_frame,
            text=f"Account ID: {self.current_user[0]} | Member since: {self.current_user[6].strftime('%B %d, %Y')}",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(5, 0))

        # Right side - Logout button
        ttk.Button(
            header_frame, text="Logout", style="Action.TButton", command=self.logout
        ).pack(side="right", padx=20, pady=10)

        # Create a notebook for different sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Create frames for different tabs
        account_tab = ttk.Frame(notebook, style="Main.TFrame")
        transactions_tab = ttk.Frame(notebook, style="Main.TFrame")

        notebook.add(account_tab, text="Account Overview")
        notebook.add(transactions_tab, text="Transaction History")

        # ----- Account Overview Tab -----
        # Balance display with card effect
        balance_frame = ttk.Frame(account_tab, style="Card.TFrame")
        balance_frame.pack(pady=20, padx=20, fill="x")

        ttk.Label(
            balance_frame, text="Current Balance", font=("Helvetica", 14), padding=10
        ).pack(anchor="w", padx=20, pady=(20, 0))

        ttk.Label(
            balance_frame,
            text=f"${self.current_user[5]:.2f}",
            style="Balance.TLabel",
            padding=10,
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # Transaction frame
        trans_frame = ttk.LabelFrame(account_tab, text="Quick Transaction", padding=20)
        trans_frame.pack(pady=20, padx=20, fill="x")

        # Transaction form
        form_frame = ttk.Frame(trans_frame)
        form_frame.pack(fill="x", expand=True)

        # Grid layout for transaction form
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Amount entry
        ttk.Label(form_frame, text="Amount ($):").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, sticky="ew", pady=5)

        # Notes entry
        ttk.Label(form_frame, text="Notes (optional):").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.notes_entry = ttk.Entry(form_frame)
        self.notes_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # Buttons
        btn_frame = ttk.Frame(trans_frame)
        btn_frame.pack(pady=20, fill="x")

        deposit_btn = ttk.Button(
            btn_frame,
            text="Deposit",
            command=self.deposit,
            style="Action.TButton",
            width=15,
        )
        deposit_btn.pack(side="left", padx=5)

        withdraw_btn = ttk.Button(
            btn_frame,
            text="Withdraw",
            command=self.withdraw,
            style="Action.TButton",
            width=15,
        )
        withdraw_btn.pack(side="left", padx=5)

        # Add Transfer button
        transfer_btn = ttk.Button(
            btn_frame,
            text="Transfer",
            command=self.show_transfer_screen,
            style="Action.TButton",
            width=15,
        )
        transfer_btn.pack(side="left", padx=5)

        # Recent transactions in Account tab
        recent_frame = ttk.LabelFrame(
            account_tab, text="Recent Transactions", padding=10
        )
        recent_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Create treeview for recent transactions
        self.recent_tree = ttk.Treeview(
            recent_frame,
            columns=("Type", "Amount", "Balance", "Notes", "Date"),
            show="headings",
            height=5,
        )
        self.recent_tree.heading("Type", text="Type")
        self.recent_tree.heading("Amount", text="Amount")
        self.recent_tree.heading("Balance", text="Balance")
        self.recent_tree.heading("Notes", text="Notes")
        self.recent_tree.heading("Date", text="Date")

        # Configure column widths
        self.recent_tree.column("Type", width=100)
        self.recent_tree.column("Amount", width=100)
        self.recent_tree.column("Balance", width=100)
        self.recent_tree.column("Notes", width=200)
        self.recent_tree.column("Date", width=150)

        # Add scrollbar
        recent_scroll = ttk.Scrollbar(
            recent_frame, orient="vertical", command=self.recent_tree.yview
        )
        self.recent_tree.configure(yscrollcommand=recent_scroll.set)

        # Pack treeview and scrollbar
        self.recent_tree.pack(side="left", fill="both", expand=True)
        recent_scroll.pack(side="right", fill="y")

        # ----- Transactions History Tab -----
        # Search frame
        search_frame = ttk.Frame(transactions_tab)
        search_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(search_frame, text="Search", command=self.search_transactions).pack(
            side="left", padx=5
        )

        ttk.Button(
            search_frame,
            text="Show All",
            command=lambda: self.refresh_transaction_history(self.trans_tree),
        ).pack(side="left", padx=5)

        # Transaction history full list
        ttk.Label(
            transactions_tab,
            text="Transaction History",
            style="TransactionHeader.TLabel",
        ).pack(pady=(20, 10), padx=20, anchor="w")

        # Create frame for treeview and scrollbar
        tree_frame = ttk.Frame(transactions_tab)
        tree_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Create treeview for transaction history
        self.trans_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Type", "Amount", "Balance", "Notes", "Date"),
            show="headings",
            height=15,
        )

        # Configure headings
        self.trans_tree.heading("ID", text="ID")
        self.trans_tree.heading("Type", text="Type")
        self.trans_tree.heading("Amount", text="Amount")
        self.trans_tree.heading("Balance", text="Balance")
        self.trans_tree.heading("Notes", text="Notes")
        self.trans_tree.heading("Date", text="Date & Time")

        # Configure column widths
        self.trans_tree.column("ID", width=50)
        self.trans_tree.column("Type", width=100)
        self.trans_tree.column("Amount", width=100)
        self.trans_tree.column("Balance", width=100)
        self.trans_tree.column("Notes", width=200)
        self.trans_tree.column("Date", width=150)

        # Add scrollbar
        trans_scroll = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.trans_tree.yview
        )
        self.trans_tree.configure(yscrollcommand=trans_scroll.set)

        # Pack treeview and scrollbar
        self.trans_tree.pack(side="left", fill="both", expand=True)
        trans_scroll.pack(side="right", fill="y")

        # Add export button
        ttk.Button(
            transactions_tab,
            text="Export Transactions",
            command=self.export_transactions,
        ).pack(pady=10)

        # Load transaction data
        self.refresh_transaction_history(self.trans_tree)
        self.refresh_transaction_history(self.recent_tree, limit=5)

        # Add tooltips
        self.create_tooltip(deposit_btn, "Add funds to your account")
        self.create_tooltip(withdraw_btn, "Withdraw funds from your account")

    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25

            # Create a toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")

            label = ttk.Label(
                self.tooltip,
                text=text,
                background="#FFFFDD",
                relief="solid",
                borderwidth=1,
                padding=5,
            )
            label.pack()

        def hide_tooltip(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        try:
            # Re-establish connection to handle potential timeouts
            conn, cursor = create_db_connection()
            cursor.execute("USE banking_system")

            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password),
            )
            user = cursor.fetchone()

            if user:
                self.current_user = list(user)  # Convert to list for mutability
                self.setup_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials")

            cursor.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Login failed: {e}")

    def show_register_screen(self):
        self.clear_window()

        register_card = ttk.Frame(self.root, style="Card.TFrame")
        register_card.place(relx=0.5, rely=0.4, anchor="center", width=500)

        ttk.Label(register_card, text="Create New Account", style="Header.TLabel").pack(
            pady=20, padx=40
        )

        form_frame = ttk.Frame(register_card)
        form_frame.pack(padx=40, pady=20, fill="x")

        fields = [
            ("Username:", "username", ""),
            ("Password:", "password", "•"),
            ("Confirm Password:", "confirm_password", "•"),
            ("Full Name:", "name", ""),
            ("Phone Number:", "phone", ""),
        ]

        self.register_entries = {}
        for i, (label, key, show) in enumerate(fields):
            ttk.Label(form_frame, text=label).pack(anchor="w")
            entry = ttk.Entry(form_frame)
            if show:
                entry.configure(show=show)
            entry.pack(pady=(0, 10), fill="x")
            self.register_entries[key] = entry

        ttk.Button(
            form_frame,
            text="Create Account",
            style="Action.TButton",
            command=self.create_account,
        ).pack(fill="x", pady=5)

        ttk.Button(
            form_frame,
            text="Back",
            style="Action.TButton",
            command=self.setup_welcome_screen,
        ).pack(fill="x", pady=5)

    def create_account(self):
        try:
            username = self.register_entries["username"].get()
            password = self.register_entries["password"].get()
            confirm_password = self.register_entries["confirm_password"].get()
            name = self.register_entries["name"].get()
            phone = self.register_entries["phone"].get()

            # Validate inputs
            if not username or not password or not name:
                messagebox.showerror(
                    "Error", "Username, password and name are required!"
                )
                return

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                return

            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters!")
                return

            if phone and not re.match(r"^\d{10}$", phone):
                messagebox.showerror("Error", "Phone number must be 10 digits!")
                return

            # Re-establish connection to handle potential timeouts
            conn, cursor = create_db_connection()
            cursor.execute("USE banking_system")

            cursor.execute(
                """
                INSERT INTO users (username, password, name, phone)
                VALUES (%s, %s, %s, %s)
            """,
                (username, password, name, phone),
            )
            conn.commit()

            cursor.close()
            conn.close()

            messagebox.showinfo(
                "Success", "Account created successfully! You can now login."
            )
            self.show_login_screen()
        except Error as e:
            if e.errno == 1062:  # MySQL duplicate entry error
                messagebox.showerror("Error", "Username already exists!")
            else:
                messagebox.showerror("Error", f"Database error: {e}")

    def deposit(self):
        try:
            amount = float(self.amount_entry.get())
            notes = self.notes_entry.get()

            if amount <= 0:
                messagebox.showerror("Error", "Please enter a positive amount")
                return

            new_balance = float(self.current_user[5]) + amount

            # Re-establish connection to handle potential timeouts
            conn, cursor = create_db_connection()
            cursor.execute("USE banking_system")

            # Start transaction
            cursor.execute("START TRANSACTION")

            try:
                # Update balance
                cursor.execute(
                    "UPDATE users SET balance = %s WHERE user_id = %s",
                    (new_balance, self.current_user[0]),
                )

                # Record transaction
                cursor.execute(
                    """
                    INSERT INTO transactions (user_id, type, amount, balance, notes)
                    VALUES (%s, 'deposit', %s, %s, %s)
                """,
                    (self.current_user[0], amount, new_balance, notes),
                )

                # Commit transaction
                conn.commit()

                # Update current user data in memory
                self.current_user[5] = new_balance

                # Refresh UI
                self.refresh_transaction_history(self.trans_tree)
                self.refresh_transaction_history(self.recent_tree, limit=5)

                # Update balance display
                for widget in self.root.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Notebook):
                                for tab in child.winfo_children():
                                    for frame in tab.winfo_children():
                                        if isinstance(frame, ttk.Frame) or isinstance(
                                            frame, ttk.LabelFrame
                                        ):
                                            for label in frame.winfo_children():
                                                if isinstance(
                                                    label, ttk.Label
                                                ) and hasattr(label, "cget"):
                                                    if (
                                                        label.cget("style")
                                                        == "Balance.TLabel"
                                                    ):
                                                        label.config(
                                                            text=f"${new_balance:.2f}"
                                                        )

                # Clear entries
                self.amount_entry.delete(0, tk.END)
                self.notes_entry.delete(0, tk.END)

                messagebox.showinfo("Success", f"${amount:.2f} deposited successfully")

            except Error as e:
                conn.rollback()
                messagebox.showerror("Transaction Error", f"Deposit failed: {e}")

            finally:
                cursor.close()
                conn.close()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")

    def withdraw(self):
        try:
            amount = float(self.amount_entry.get())
            notes = self.notes_entry.get()

            if amount <= 0:
                messagebox.showerror("Error", "Please enter a positive amount")
                return

            if amount > float(self.current_user[5]):
                messagebox.showerror("Error", "Insufficient funds")
                return

            new_balance = float(self.current_user[5]) - amount

            # Re-establish connection to handle potential timeouts
            conn, cursor = create_db_connection()
            cursor.execute("USE banking_system")

            # Start transaction
            cursor.execute("START TRANSACTION")

            try:
                # Update balance
                cursor.execute(
                    "UPDATE users SET balance = %s WHERE user_id = %s",
                    (new_balance, self.current_user[0]),
                )

                # Record transaction
                cursor.execute(
                    """
                    INSERT INTO transactions (user_id, type, amount, balance, notes)
                    VALUES (%s, 'withdrawal', %s, %s, %s)
                """,
                    (self.current_user[0], amount, new_balance, notes),
                )

                # Commit transaction
                conn.commit()

                # Update current user data in memory
                self.current_user[5] = new_balance

                # Refresh UI
                self.refresh_transaction_history(self.trans_tree)
                self.refresh_transaction_history(self.recent_tree, limit=5)

                # Update balance display in UI
                for widget in self.root.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Notebook):
                                for tab in child.winfo_children():
                                    for frame in tab.winfo_children():
                                        if isinstance(frame, ttk.Frame) or isinstance(
                                            frame, ttk.LabelFrame
                                        ):
                                            for label in frame.winfo_children():
                                                if isinstance(
                                                    label, ttk.Label
                                                ) and hasattr(label, "cget"):
                                                    if (
                                                        label.cget("style")
                                                        == "Balance.TLabel"
                                                    ):
                                                        label.config(
                                                            text=f"${new_balance:.2f}"
                                                        )

                # Clear entries
                self.amount_entry.delete(0, tk.END)
                self.notes_entry.delete(0, tk.END)

                messagebox.showinfo("Success", f"${amount:.2f} withdrawn successfully")

            except Error as e:
                conn.rollback()
                messagebox.showerror("Transaction Error", f"Withdrawal failed: {e}")

            finally:
                cursor.close()
                conn.close()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")

    def refresh_transaction_history(self, tree_widget, limit=None):
        # Clear existing data
        for item in tree_widget.get_children():
            tree_widget.delete(item)

        try:
            # Re-establish connection to handle potential timeouts
            conn, cursor = create_db_connection()
            cursor.execute("USE banking_system")

            # Prepare query based on whether limit is provided
            query = """
                SELECT trans_id, type, amount, balance, notes, timestamp 
                FROM transactions 
                WHERE user_id = %s 
                ORDER BY timestamp DESC
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, (self.current_user[0],))

            for transaction in cursor.fetchall():
                # Format transaction type with capitalized first letter
                trans_type = transaction[1].capitalize()

                # Format amount with currency symbol and proper sign
                if trans_type == "Deposit":
                    amount_str = f"+${transaction[2]:.2f}"
                else:
                    amount_str = f"-${transaction[2]:.2f}"

                # Format balance with currency symbol
                balance_str = f"${transaction[3]:.2f}"

                # Format timestamp
                timestamp_str = transaction[5].strftime("%Y-%m-%d %I:%M %p")

                # Insert into tree
                values = (
                    transaction[0] if "ID" in tree_widget["columns"] else None,
                    trans_type,
                    amount_str,
                    balance_str,
                    transaction[4] or "-",
                    timestamp_str,
                )

                # Filter out None values based on columns
                values = [
                    v
                    for i, v in enumerate(values)
                    if i == 0 and "ID" not in tree_widget["columns"] or v is not None
                ]

                tree_widget.insert("", "end", values=values)

            cursor.close()
            conn.close()

        except Error as e:
            messagebox.showerror("Database Error", f"Could not fetch transactions: {e}")

    def search_transactions(self):
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            return

        # Clear existing data
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        try:
            # Re-establish connection to handle potential timeouts
            conn, cursor = create_db_connection()
            cursor.execute("USE banking_system")

            # Search in multiple fields
            query = """
                SELECT trans_id, type, amount, balance, notes, timestamp 
                FROM transactions 
                WHERE user_id = %s AND (
                    LOWER(type) LIKE %s OR 
                    CAST(amount AS CHAR) LIKE %s OR 
                    LOWER(notes) LIKE %s OR
                    CAST(timestamp AS CHAR) LIKE %s
                )
                ORDER BY timestamp DESC
            """

            search_pattern = f"%{search_term}%"
            cursor.execute(
                query,
                (
                    self.current_user[0],
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                ),
            )

            for transaction in cursor.fetchall():
                # Format transaction type with capitalized first letter
                trans_type = transaction[1].capitalize()

                # Format amount with currency symbol and proper sign
                if trans_type == "Deposit":
                    amount_str = f"+${transaction[2]:.2f}"
                else:
                    amount_str = f"-${transaction[2]:.2f}"

                # Format balance with currency symbol
                balance_str = f"${transaction[3]:.2f}"

                # Format timestamp
                timestamp_str = transaction[5].strftime("%Y-%m-%d %I:%M %p")

                # Insert into tree
                self.trans_tree.insert(
                    "",
                    "end",
                    values=(
                        transaction[0],
                        trans_type,
                        amount_str,
                        balance_str,
                        transaction[4] or "-",
                        timestamp_str,
                    ),
                )

            cursor.close()
            conn.close()

            if not self.trans_tree.get_children():
                messagebox.showinfo(
                    "Search Results", "No transactions found matching your search."
                )

        except Error as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")

    def export_transactions(self):
        """Export transaction history to a text file"""
        try:
            # Re-establish connection to handle potential timeouts
            conn, cursor = create_db_connection()
            cursor.execute("USE banking_system")

            cursor.execute(
                """
                SELECT trans_id, type, amount, balance, notes, timestamp 
                FROM transactions 
                WHERE user_id = %s 
                ORDER BY timestamp DESC
                """,
                (self.current_user[0],),
            )

            transactions = cursor.fetchall()

            if not transactions:
                messagebox.showinfo("Export", "No transactions to export.")
                return

            # Create filename with timestamp
            filename = (
                f"transaction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )

            with open(filename, "w") as file:
                # Write header
                file.write(f"Transaction History for {self.current_user[2]}\n")
                file.write(
                    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                file.write("-" * 80 + "\n\n")

                # Write column headers
                file.write(
                    f"{'ID':<5} {'Type':<12} {'Amount':<10} {'Balance':<10} {'Date & Time':<20} {'Notes':<30}\n"
                )
                file.write("-" * 80 + "\n")

                # Write transactions
                for trans in transactions:
                    trans_id = trans[0]
                    trans_type = trans[1].capitalize()
                    amount = f"${trans[2]:.2f}"
                    balance = f"${trans[3]:.2f}"
                    timestamp = trans[5].strftime("%Y-%m-%d %I:%M %p")
                    notes = trans[4] or "-"

                    file.write(
                        f"{trans_id:<5} {trans_type:<12} {amount:<10} {balance:<10} {timestamp:<20} {notes:<30}\n"
                    )

            cursor.close()
            conn.close()

            messagebox.showinfo(
                "Export Successful", f"Transactions exported to {filename}"
            )

        except Error as e:
            messagebox.showerror("Export Error", f"Failed to export transactions: {e}")
        except IOError as e:
            messagebox.showerror("File Error", f"Failed to write to file: {e}")

    def logout(self):
        """Log out the current user and return to welcome screen"""
        self.current_user = None
        self.setup_welcome_screen()

    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            if widget != self.clock_label:  # Keep the clock
                widget.destroy()

    def show_transfer_screen(self):
        self.clear_window()

        transfer_card = ttk.Frame(self.root, style="Card.TFrame")
        transfer_card.place(relx=0.5, rely=0.4, anchor="center", width=500)

        ttk.Label(transfer_card, text="Transfer Money", style="Header.TLabel").pack(
            pady=20, padx=40
        )

        form_frame = ttk.Frame(transfer_card)
        form_frame.pack(padx=40, pady=20, fill="x")

        # Recipient username
        ttk.Label(form_frame, text="Recipient Username:").pack(anchor="w")
        self.recipient_entry = ttk.Entry(form_frame)
        self.recipient_entry.pack(pady=(0, 10), fill="x")

        # Amount
        ttk.Label(form_frame, text="Amount ($):").pack(anchor="w")
        self.transfer_amount_entry = ttk.Entry(form_frame)
        self.transfer_amount_entry.pack(pady=(0, 10), fill="x")

        # Notes
        ttk.Label(form_frame, text="Notes (optional):").pack(anchor="w")
        self.transfer_notes_entry = ttk.Entry(form_frame)
        self.transfer_notes_entry.pack(pady=(0, 20), fill="x")

        # Buttons
        ttk.Button(
            form_frame,
            text="Transfer",
            style="Action.TButton",
            command=self.transfer_money,
        ).pack(fill="x", pady=5)

        ttk.Button(
            form_frame,
            text="Back",
            style="Action.TButton",
            command=self.setup_dashboard,
        ).pack(fill="x", pady=5)

    def transfer_money(self):
        recipient_username = self.recipient_entry.get().strip()
        try:
            amount = float(self.transfer_amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            return

        notes = self.transfer_notes_entry.get().strip()

        if not recipient_username or amount <= 0:
            messagebox.showerror("Error", "Please provide a valid recipient and amount")
            return

        if amount > float(self.current_user[5]):
            messagebox.showerror("Error", "Insufficient funds")
            return

        try:
            # Re-establish connection to handle potential timeouts
            conn, cursor = create_db_connection()
            cursor.execute("USE banking_system")

            # Check if recipient exists
            cursor.execute(
                "SELECT user_id, balance FROM users WHERE username = %s",
                (recipient_username,),
            )
            recipient = cursor.fetchone()

            if not recipient:
                messagebox.showerror("Error", "Recipient not found")
                return

            recipient_id, recipient_balance = recipient

            # Start transaction
            cursor.execute("START TRANSACTION")

            try:
                # Deduct amount from sender
                new_sender_balance = float(self.current_user[5]) - amount
                cursor.execute(
                    "UPDATE users SET balance = %s WHERE user_id = %s",
                    (new_sender_balance, self.current_user[0]),
                )

                # Add amount to recipient
                new_recipient_balance = float(recipient_balance) + amount
                cursor.execute(
                    "UPDATE users SET balance = %s WHERE user_id = %s",
                    (new_recipient_balance, recipient_id),
                )

                # Record transaction for sender
                cursor.execute(
                    """
                    INSERT INTO transactions (user_id, type, amount, balance, notes)
                    VALUES (%s, 'transfer_out', %s, %s, %s)
                    """,
                    (self.current_user[0], amount, new_sender_balance, notes),
                )

                # Record transaction for recipient
                cursor.execute(
                    """
                    INSERT INTO transactions (user_id, type, amount, balance, notes)
                    VALUES (%s, 'transfer_in', %s, %s, %s)
                    """,
                    (recipient_id, amount, new_recipient_balance, notes),
                )

                # Commit transaction
                conn.commit()

                # Update current user data in memory
                self.current_user[5] = new_sender_balance

                # Refresh UI
                self.refresh_transaction_history(self.trans_tree)
                self.refresh_transaction_history(self.recent_tree, limit=5)

                messagebox.showinfo(
                    "Success", f"${amount:.2f} transferred to {recipient_username}"
                )

                # Clear entries
                self.recipient_entry.delete(0, tk.END)
                self.transfer_amount_entry.delete(0, tk.END)
                self.transfer_notes_entry.delete(0, tk.END)

            except Error as e:
                conn.rollback()
                messagebox.showerror("Transaction Error", f"Transfer failed: {e}")

            finally:
                cursor.close()
                conn.close()

        except Error as e:
            messagebox.showerror("Database Error", f"Transfer failed: {e}")


if __name__ == "__main__":
    root = ThemedTk(theme="clearlooks")
    app = ModernBankingSystem(root)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()

    # Close any open database connections when the app closes
    try:
        if "conn" in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    except:
        pass
