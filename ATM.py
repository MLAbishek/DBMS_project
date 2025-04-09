import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import re
import os
import logging
from decimal import Decimal

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="atm_system.log",
)
logger = logging.getLogger("atm_system")


class Database:
    """Database handler class for MySQL operations"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="abishek@123",  # Change this to your MySQL password
                database="atm_system",
            )
            self.cursor = self.connection.cursor()
            return True
        except mysql.connector.Error as error:
            logger.error(f"Database connection failed: {error}")
            return False

    def initialize_database(self):
        """Create necessary tables if they don't exist"""
        try:
            # Connect to MySQL server without specifying database
            temp_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="abishek@123",  # Change this to your MySQL password
            )
            temp_cursor = temp_connection.cursor()

            # Create database if it doesn't exist
            temp_cursor.execute("CREATE DATABASE IF NOT EXISTS atm_db")
            temp_cursor.close()
            temp_connection.close()

            # Connect to the atm_db database
            self.connect()

            # Create accounts table
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id INT AUTO_INCREMENT PRIMARY KEY,
                    card_number VARCHAR(16) UNIQUE NOT NULL,
                    pin VARCHAR(4) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    balance DECIMAL(15, 2) DEFAULT 0.00,
                    account_type ENUM('Savings', 'Checking') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create transactions table
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                    account_id INT NOT NULL,
                    transaction_type ENUM('Deposit', 'Withdrawal', 'Transfer') NOT NULL,
                    amount DECIMAL(15, 2) NOT NULL,
                    recipient_account_id INT NULL,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
                    FOREIGN KEY (recipient_account_id) REFERENCES accounts(account_id)
                )
            """
            )

            # Insert sample account data if table is empty
            self.cursor.execute("SELECT COUNT(*) FROM accounts")
            if self.cursor.fetchone()[0] == 0:
                sample_accounts = [
                    ("1234567890123456", "1234", "John Doe", 1000.00, "Savings"),
                    ("2345678901234567", "2345", "Jane Smith", 2500.00, "Checking"),
                    ("3456789012345678", "3456", "Bob Johnson", 750.50, "Savings"),
                ]
                self.cursor.executemany(
                    """
                    INSERT INTO accounts (card_number, pin, full_name, balance, account_type)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    sample_accounts,
                )

            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            logger.error(f"Database initialization failed: {error}")
            return False

    def authenticate_user(self, card_number, pin):
        """Authenticate user with card number and PIN"""
        try:
            self.cursor.execute(
                """
                SELECT account_id, full_name, balance 
                FROM accounts 
                WHERE card_number = %s AND pin = %s
            """,
                (card_number, pin),
            )
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as error:
            logger.error(f"Authentication error: {error}")
            return None

    def get_balance(self, account_id):
        """Get account balance"""
        try:
            self.cursor.execute(
                "SELECT balance FROM accounts WHERE account_id = %s", (account_id,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except mysql.connector.Error as error:
            logger.error(f"Get balance error: {error}")
            return None

    def withdraw(self, account_id, amount):
        """Process withdrawal from account"""
        try:
            # Get current balance
            current_balance = self.get_balance(account_id)
            if current_balance is None:
                return False, "Account not found"

            # Check if enough funds
            if current_balance < amount:
                return False, "Insufficient funds"

            # Update balance
            new_balance = current_balance - amount
            self.cursor.execute(
                """
                UPDATE accounts SET balance = %s WHERE account_id = %s
            """,
                (new_balance, account_id),
            )

            # Record transaction
            self.cursor.execute(
                """
                INSERT INTO transactions (account_id, transaction_type, amount)
                VALUES (%s, 'Withdrawal', %s)
            """,
                (account_id, amount),
            )

            self.connection.commit()
            return True, new_balance
        except mysql.connector.Error as error:
            self.connection.rollback()
            logger.error(f"Withdrawal error: {error}")
            return False, str(error)

    def deposit(self, account_id, amount):
        """Process deposit to account"""
        try:
            # Get current balance
            current_balance = self.get_balance(account_id)
            if current_balance is None:
                return False, "Account not found"

            # Update balance
            new_balance = current_balance + amount
            self.cursor.execute(
                """
                UPDATE accounts SET balance = %s WHERE account_id = %s
            """,
                (new_balance, account_id),
            )

            # Record transaction
            self.cursor.execute(
                """
                INSERT INTO transactions (account_id, transaction_type, amount)
                VALUES (%s, 'Deposit', %s)
            """,
                (account_id, amount),
            )

            self.connection.commit()
            return True, new_balance
        except mysql.connector.Error as error:
            self.connection.rollback()
            logger.error(f"Deposit error: {error}")
            return False, str(error)

    def get_account_by_card(self, card_number):
        """Get account ID by card number"""
        try:
            self.cursor.execute(
                "SELECT account_id FROM accounts WHERE card_number = %s", (card_number,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except mysql.connector.Error as error:
            logger.error(f"Get account error: {error}")
            return None

    def transfer(self, from_account_id, to_card_number, amount):
        """Transfer money between accounts"""
        try:
            # Get recipient account ID
            to_account_id = self.get_account_by_card(to_card_number)
            if to_account_id is None:
                return False, "Recipient account not found"

            if from_account_id == to_account_id:
                return False, "Cannot transfer to the same account"

            # Get current balance of sender
            from_balance = self.get_balance(from_account_id)
            if from_balance is None:
                return False, "Sender account not found"

            # Check if enough funds
            if from_balance < amount:
                return False, "Insufficient funds"

            # Start transaction
            self.connection.start_transaction()

            # Update sender balance
            new_from_balance = from_balance - amount
            self.cursor.execute(
                """
                UPDATE accounts SET balance = %s WHERE account_id = %s
            """,
                (new_from_balance, from_account_id),
            )

            # Update recipient balance
            to_balance = self.get_balance(to_account_id)
            new_to_balance = to_balance + amount
            self.cursor.execute(
                """
                UPDATE accounts SET balance = %s WHERE account_id = %s
            """,
                (new_to_balance, to_account_id),
            )

            # Record transaction
            self.cursor.execute(
                """
                INSERT INTO transactions (account_id, transaction_type, amount, recipient_account_id)
                VALUES (%s, 'Transfer', %s, %s)
            """,
                (from_account_id, amount, to_account_id),
            )

            self.connection.commit()
            return True, new_from_balance
        except mysql.connector.Error as error:
            self.connection.rollback()
            logger.error(f"Transfer error: {error}")
            return False, str(error)

    def get_transaction_history(self, account_id, limit=10):
        """Get transaction history for an account"""
        try:
            self.cursor.execute(
                """
                SELECT 
                    t.transaction_id, 
                    t.transaction_type, 
                    t.amount, 
                    t.transaction_date,
                    CASE 
                        WHEN t.transaction_type = 'Transfer' THEN 
                            (SELECT card_number FROM accounts WHERE account_id = t.recipient_account_id)
                        ELSE NULL
                    END as recipient_card
                FROM transactions t
                WHERE t.account_id = %s
                ORDER BY t.transaction_date DESC
                LIMIT %s
            """,
                (account_id, limit),
            )

            transactions = []
            for tid, ttype, amount, tdate, recipient in self.cursor:
                transactions.append(
                    {
                        "id": tid,
                        "type": ttype,
                        "amount": amount,
                        "date": tdate,
                        "recipient": recipient,
                    }
                )

            return transactions
        except mysql.connector.Error as error:
            logger.error(f"Get transaction history error: {error}")
            return []

    def change_pin(self, account_id, new_pin):
        """Change account PIN"""
        try:
            self.cursor.execute(
                """
                UPDATE accounts SET pin = %s WHERE account_id = %s
            """,
                (new_pin, account_id),
            )
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            self.connection.rollback()
            logger.error(f"Change PIN error: {error}")
            return False

    def close(self):
        """Close database connection"""
        if self.connection:
            self.cursor.close()
            self.connection.close()


class ATMApp:
    """Main ATM application class"""

    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.current_user = None  # Will store (account_id, name, balance) tuple

        # Initialize the database
        if not self.db.initialize_database():
            messagebox.showerror(
                "Database Error",
                "Failed to initialize database. Check logs for details.",
            )
            root.destroy()
            return

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        self.root.title("ATM System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Create a style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 12), padding=10)
        self.style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
        self.style.configure(
            "Header.TLabel", font=("Arial", 18, "bold"), background="#f0f0f0"
        )

        # Create frames for different screens
        self.frames = {}
        for F in (
            LoginScreen,
            MainMenu,
            WithdrawScreen,
            DepositScreen,
            TransferScreen,
            BalanceScreen,
            TransactionHistoryScreen,
            ChangePINScreen,
        ):
            frame = F(self.root, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)
            frame.place_forget()  # Hide all frames initially

        # Show login screen
        self.show_frame("LoginScreen")

    def show_frame(self, frame_name):
        """Show the specified frame and hide others"""
        for frame in self.frames.values():
            frame.place_forget()
        self.frames[frame_name].place(relx=0, rely=0, relwidth=1, relheight=1)

        # If showing the main menu, update the user info
        if frame_name == "MainMenu" and self.current_user:
            self.frames["MainMenu"].update_user_info()

    def login(self, card_number, pin):
        """Handle user login"""
        if not self.db.connect():
            messagebox.showerror("Error", "Database connection failed")
            return False

        # Validate card number and PIN format
        if not self.validate_card_number(card_number):
            messagebox.showerror("Invalid Input", "Card number must be 16 digits")
            return False

        if not self.validate_pin(pin):
            messagebox.showerror("Invalid Input", "PIN must be 4 digits")
            return False

        # Authenticate user
        user_data = self.db.authenticate_user(card_number, pin)
        if user_data:
            self.current_user = user_data  # (account_id, name, balance)
            self.show_frame("MainMenu")
            logger.info(f"User {user_data[1]} logged in successfully")
            return True
        else:
            messagebox.showerror("Login Failed", "Invalid card number or PIN")
            logger.warning(f"Failed login attempt with card: {card_number}")
            return False

    def logout(self):
        """Handle user logout"""
        if self.current_user:
            logger.info(f"User {self.current_user[1]} logged out")
            self.current_user = None
        self.db.close()
        self.show_frame("LoginScreen")

    def get_balance(self):
        """Get current user's balance"""
        if not self.current_user:
            return None

        # Refresh balance from database
        balance = self.db.get_balance(self.current_user[0])
        if balance is not None:
            # Update the current user tuple with the new balance
            self.current_user = (self.current_user[0], self.current_user[1], balance)
        return balance

    def withdraw(self, amount):
        """Process withdrawal"""
        if not self.current_user:
            return False, "Not logged in"

        try:
            amount = Decimal(amount)
        except:
            return False, "Invalid amount format"

        if amount <= 0:
            return False, "Amount must be positive"

        success, result = self.db.withdraw(self.current_user[0], amount)
        if success:
            # Update current user balance
            self.current_user = (self.current_user[0], self.current_user[1], result)
            logger.info(f"User {self.current_user[1]} withdrew ${amount:.2f}")
        return success, result

    def deposit(self, amount):
        """Process deposit"""
        if not self.current_user:
            return False, "Not logged in"

        try:
            amount = Decimal(amount)
        except:
            return False, "Invalid amount format"

        if amount <= 0:
            return False, "Amount must be positive"

        success, result = self.db.deposit(self.current_user[0], amount)
        if success:
            # Update current user balance
            self.current_user = (self.current_user[0], self.current_user[1], result)
            logger.info(f"User {self.current_user[1]} deposited ${amount:.2f}")
        return success, result

    def transfer(self, recipient_card, amount):
        """Process transfer"""
        if not self.current_user:
            return False, "Not logged in"

        try:
            amount = Decimal(amount)
        except:
            return False, "Invalid amount format"

        if amount <= 0:
            return False, "Amount must be positive"

        if not self.validate_card_number(recipient_card):
            return False, "Invalid recipient card number"

        success, result = self.db.transfer(self.current_user[0], recipient_card, amount)
        if success:
            # Update current user balance
            self.current_user = (self.current_user[0], self.current_user[1], result)
            logger.info(
                f"User {self.current_user[1]} transferred ${amount:.2f} to card {recipient_card}"
            )
        return success, result

    def get_transaction_history(self):
        """Get transaction history for current user"""
        if not self.current_user:
            return []

        return self.db.get_transaction_history(self.current_user[0])

    def change_pin(self, old_pin, new_pin):
        """Change user's PIN"""
        if not self.current_user:
            return False, "Not logged in"

        if not self.validate_pin(old_pin) or not self.validate_pin(new_pin):
            return False, "PIN must be 4 digits"

        # Verify old PIN
        auth_result = self.db.authenticate_user(card_number=None, pin=old_pin)
        if not auth_result or auth_result[0] != self.current_user[0]:
            return False, "Current PIN is incorrect"

        success = self.db.change_pin(self.current_user[0], new_pin)
        if success:
            logger.info(f"User {self.current_user[1]} changed PIN")
            return True, "PIN changed successfully"
        else:
            return False, "Failed to change PIN"

    @staticmethod
    def validate_card_number(card_number):
        """Validate card number format"""
        return bool(re.match(r"^\d{16}$", card_number))

    @staticmethod
    def validate_pin(pin):
        """Validate PIN format"""
        return bool(re.match(r"^\d{4}$", pin))


class BaseScreen(ttk.Frame):
    """Base class for all screens"""

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.style = ttk.Style()


class LoginScreen(BaseScreen):
    """Login screen with card number and PIN input"""

    def __init__(self, parent, controller):
        BaseScreen.__init__(self, parent, controller)

        # Create a frame for login form
        login_frame = ttk.Frame(self, padding=20)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=300)

        # Title
        title_label = ttk.Label(login_frame, text="ATM System", style="Header.TLabel")
        title_label.pack(pady=20)

        # Card Number
        card_frame = ttk.Frame(login_frame)
        card_frame.pack(fill=tk.X, pady=10)
        card_label = ttk.Label(card_frame, text="Card Number:")
        card_label.pack(anchor=tk.W)
        self.card_entry = ttk.Entry(card_frame, width=30)
        self.card_entry.pack(fill=tk.X, pady=5)

        # PIN
        pin_frame = ttk.Frame(login_frame)
        pin_frame.pack(fill=tk.X, pady=10)
        pin_label = ttk.Label(pin_frame, text="PIN:")
        pin_label.pack(anchor=tk.W)
        self.pin_entry = ttk.Entry(pin_frame, show="*", width=30)
        self.pin_entry.pack(fill=tk.X, pady=5)

        # Login Button
        login_button = ttk.Button(login_frame, text="Login", command=self.login)
        login_button.pack(pady=20)

        # Sample accounts info (for demo purposes)
        info_text = (
            "Demo Accounts:\n1234567890123456 (PIN: 1234)\n2345678901234567 (PIN: 2345)"
        )
        info_label = ttk.Label(login_frame, text=info_text, font=("Arial", 8))
        info_label.pack(pady=10)

        # Bind Enter key to login
        self.card_entry.bind("<Return>", lambda event: self.pin_entry.focus())
        self.pin_entry.bind("<Return>", lambda event: self.login())

    def login(self):
        """Process login with entered credentials"""
        card_number = self.card_entry.get().strip()
        pin = self.pin_entry.get().strip()

        if self.controller.login(card_number, pin):
            # Clear entries for next login
            self.card_entry.delete(0, tk.END)
            self.pin_entry.delete(0, tk.END)


class MainMenu(BaseScreen):
    """Main menu with ATM operation options"""

    def __init__(self, parent, controller):
        BaseScreen.__init__(self, parent, controller)

        # User info frame at the top
        self.user_frame = ttk.Frame(self, padding=10)
        self.user_frame.pack(fill=tk.X, pady=10)

        self.user_label = ttk.Label(self.user_frame, text="", style="Header.TLabel")
        self.user_label.pack(side=tk.LEFT, padx=20)

        self.balance_label = ttk.Label(self.user_frame, text="")
        self.balance_label.pack(side=tk.RIGHT, padx=20)

        # Date and time
        self.datetime_label = ttk.Label(self, text="")
        self.datetime_label.pack(pady=5)
        self.update_datetime()

        # Menu buttons frame
        menu_frame = ttk.Frame(self, padding=20)
        menu_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=20)

        # Grid layout for menu buttons
        buttons = [
            ("Check Balance", lambda: controller.show_frame("BalanceScreen")),
            ("Withdraw", lambda: controller.show_frame("WithdrawScreen")),
            ("Deposit", lambda: controller.show_frame("DepositScreen")),
            ("Transfer", lambda: controller.show_frame("TransferScreen")),
            (
                "Transaction History",
                lambda: controller.show_frame("TransactionHistoryScreen"),
            ),
            ("Change PIN", lambda: controller.show_frame("ChangePINScreen")),
            ("Logout", controller.logout),
        ]

        # Create menu buttons in a 2x4 grid
        for i, (text, command) in enumerate(buttons):
            row, col = divmod(i, 2)
            button = ttk.Button(menu_frame, text=text, command=command, width=20)
            button.grid(row=row, column=col, padx=20, pady=15)

    def update_user_info(self):
        """Update user info display"""
        if self.controller.current_user:
            self.user_label.config(text=f"Welcome, {self.controller.current_user[1]}")
            balance = self.controller.get_balance()
            self.balance_label.config(text=f"Balance: ${balance:.2f}")

    def update_datetime(self):
        """Update date and time display"""
        current_time = datetime.now().strftime("%B %d, %Y %H:%M:%S")
        self.datetime_label.config(text=current_time)
        self.after(1000, self.update_datetime)  # Update every second


class WithdrawScreen(BaseScreen):
    """Screen for withdrawing money"""

    def __init__(self, parent, controller):
        BaseScreen.__init__(self, parent, controller)

        # Title
        title_label = ttk.Label(self, text="Withdraw Cash", style="Header.TLabel")
        title_label.pack(pady=20)

        # Amount entry
        amount_frame = ttk.Frame(self, padding=10)
        amount_frame.pack(pady=20)

        amount_label = ttk.Label(amount_frame, text="Enter amount:")
        amount_label.pack(side=tk.LEFT, padx=10)

        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=15)
        amount_entry.pack(side=tk.LEFT, padx=10)
        amount_entry.focus_set()

        # Quick withdrawal amounts
        quick_frame = ttk.Frame(self, padding=10)
        quick_frame.pack(pady=20)

        quick_label = ttk.Label(quick_frame, text="Quick withdrawal:")
        quick_label.pack(anchor=tk.CENTER, pady=10)

        amounts = [20, 50, 100, 200, 500]
        amount_frame = ttk.Frame(quick_frame)
        amount_frame.pack()

        for i, amount in enumerate(amounts):
            button = ttk.Button(
                amount_frame,
                text=f"${amount}",
                command=lambda a=amount: self.quick_withdraw(a),
            )
            button.grid(row=0, column=i, padx=10)

        # Action buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        withdraw_button = ttk.Button(
            button_frame, text="Withdraw", command=self.withdraw
        )
        withdraw_button.pack(side=tk.LEFT, padx=20)

        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=lambda: controller.show_frame("MainMenu"),
        )
        cancel_button.pack(side=tk.RIGHT, padx=20)

        # Bind Enter key
        amount_entry.bind("<Return>", lambda event: self.withdraw())

    def withdraw(self):
        """Process withdrawal with entered amount"""
        amount_str = self.amount_var.get().strip()

        try:
            amount = Decimal(amount_str)
        except:
            messagebox.showerror("Invalid Input", "Please enter a valid amount")
            return

        success, result = self.controller.withdraw(amount)

        if success:
            messagebox.showinfo(
                "Success",
                f"Withdrew ${amount:.2f} successfully.\nNew balance: ${result:.2f}",
            )
            self.amount_var.set("")
            self.controller.show_frame("MainMenu")
        else:
            messagebox.showerror("Error", result)

    def quick_withdraw(self, amount):
        """Process quick withdrawal with preset amount"""
        self.amount_var.set(str(amount))
        self.withdraw()


class DepositScreen(BaseScreen):
    """Screen for depositing money"""

    def __init__(self, parent, controller):
        BaseScreen.__init__(self, parent, controller)

        # Title
        title_label = ttk.Label(self, text="Deposit Cash", style="Header.TLabel")
        title_label.pack(pady=20)

        # Amount entry
        amount_frame = ttk.Frame(self, padding=10)
        amount_frame.pack(pady=20)

        amount_label = ttk.Label(amount_frame, text="Enter amount:")
        amount_label.pack(side=tk.LEFT, padx=10)

        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=15)
        amount_entry.pack(side=tk.LEFT, padx=10)
        amount_entry.focus_set()

        # Action buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        deposit_button = ttk.Button(button_frame, text="Deposit", command=self.deposit)
        deposit_button.pack(side=tk.LEFT, padx=20)

        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=lambda: controller.show_frame("MainMenu"),
        )
        cancel_button.pack(side=tk.RIGHT, padx=20)

        # Bind Enter key
        amount_entry.bind("<Return>", lambda event: self.deposit())

    def deposit(self):
        """Process deposit with entered amount"""
        amount_str = self.amount_var.get().strip()

        try:
            amount = Decimal(amount_str)
        except:
            messagebox.showerror("Invalid Input", "Please enter a valid amount")
            return

        success, result = self.controller.deposit(amount)

        if success:
            messagebox.showinfo(
                "Success",
                f"Deposited ${amount:.2f} successfully.\nNew balance: ${result:.2f}",
            )
            self.amount_var.set("")
            self.controller.show_frame("MainMenu")
        else:
            messagebox.showerror("Error", result)


class TransferScreen(BaseScreen):
    """Screen for transferring money"""

    def __init__(self, parent, controller):
        BaseScreen.__init__(self, parent, controller)

        # Title
        title_label = ttk.Label(self, text="Transfer Money", style="Header.TLabel")
        title_label.pack(pady=20)

        # Form frame
        form_frame = ttk.Frame(self, padding=10)
        form_frame.pack(pady=20)

        # Recipient card number
        card_label = ttk.Label(form_frame, text="Recipient Card Number:")
        card_label.grid(row=0, column=0, sticky=tk.W, pady=10)

        self.card_var = tk.StringVar()
        card_entry = ttk.Entry(form_frame, textvariable=self.card_var, width=20)
        card_entry.grid(row=0, column=1, padx=10, pady=10)
        card_entry.focus_set()

        # Amount
        amount_label = ttk.Label(form_frame, text="Amount:")
        amount_label.grid(row=1, column=0, sticky=tk.W, pady=10)

        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(form_frame, textvariable=self.amount_var, width=20)
        amount_entry.grid(row=1, column=1, padx=10, pady=10)

        # Action buttons
        # Action buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        transfer_button = ttk.Button(
            button_frame, text="Transfer", command=self.transfer
        )
        transfer_button.pack(side=tk.LEFT, padx=20)

        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=lambda: controller.show_frame("MainMenu"),
        )
        cancel_button.pack(side=tk.RIGHT, padx=20)

        # Bind Enter key
        card_entry.bind("<Return>", lambda event: amount_entry.focus())
        amount_entry.bind("<Return>", lambda event: self.transfer())

    def transfer(self):
        """Process transfer with entered recipient and amount"""
        card_number = self.card_var.get().strip()
        amount_str = self.amount_var.get().strip()

        try:
            amount = Decimal(amount_str)
        except:
            messagebox.showerror("Invalid Input", "Please enter a valid amount")
            return

        success, result = self.controller.transfer(card_number, amount)

        if success:
            messagebox.showinfo(
                "Success",
                f"Transferred ${amount:.2f} successfully.\nNew balance: ${result:.2f}",
            )
            self.card_var.set("")
            self.amount_var.set("")
            self.controller.show_frame("MainMenu")
        else:
            messagebox.showerror("Error", result)


class BalanceScreen(BaseScreen):
    """Screen for displaying account balance"""

    def __init__(self, parent, controller):
        BaseScreen.__init__(self, parent, controller)

        # Title
        title_label = ttk.Label(self, text="Account Balance", style="Header.TLabel")
        title_label.pack(pady=20)

        # Balance display
        self.balance_frame = ttk.Frame(self, padding=20)
        self.balance_frame.pack(expand=True, pady=50)

        self.balance_label = ttk.Label(self.balance_frame, text="", font=("Arial", 24))
        self.balance_label.pack()

        # Action button
        back_button = ttk.Button(
            self,
            text="Back to Main Menu",
            command=lambda: controller.show_frame("MainMenu"),
        )
        back_button.pack(side=tk.BOTTOM, pady=30)

    def tkraise(self):
        """Override tkraise to update balance before showing"""
        super().tkraise()
        if self.controller.current_user:
            balance = self.controller.get_balance()
            self.balance_label.config(text=f"${balance:.2f}")


class TransactionHistoryScreen(BaseScreen):
    """Screen for displaying transaction history"""

    def __init__(self, parent, controller):
        BaseScreen.__init__(self, parent, controller)

        # Title
        title_label = ttk.Label(self, text="Transaction History", style="Header.TLabel")
        title_label.pack(pady=20)

        # Transaction list frame
        self.history_frame = ttk.Frame(self, padding=10)
        self.history_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Create treeview for transactions
        columns = ("id", "type", "amount", "date", "recipient")
        self.tree = ttk.Treeview(self.history_frame, columns=columns, show="headings")

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("date", text="Date")
        self.tree.heading("recipient", text="Recipient")

        # Define columns
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("type", width=100, anchor=tk.CENTER)
        self.tree.column("amount", width=100, anchor=tk.CENTER)
        self.tree.column("date", width=150, anchor=tk.CENTER)
        self.tree.column("recipient", width=150, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.history_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action button
        back_button = ttk.Button(
            self,
            text="Back to Main Menu",
            command=lambda: controller.show_frame("MainMenu"),
        )
        back_button.pack(side=tk.BOTTOM, pady=20)

    def tkraise(self):
        """Override tkraise to update transaction history before showing"""
        super().tkraise()
        # Clear existing items
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Load transaction history
        if self.controller.current_user:
            transactions = self.controller.get_transaction_history()

            for tx in transactions:
                # Format data for display
                tx_id = tx["id"]
                tx_type = tx["type"]
                amount = f"${tx['amount']:.2f}"
                date = tx["date"].strftime("%Y-%m-%d %H:%M:%S")
                recipient = tx["recipient"] if tx["recipient"] else "-"

                self.tree.insert(
                    "", tk.END, values=(tx_id, tx_type, amount, date, recipient)
                )


class ChangePINScreen(BaseScreen):
    """Screen for changing PIN"""

    def __init__(self, parent, controller):
        BaseScreen.__init__(self, parent, controller)

        # Title
        title_label = ttk.Label(self, text="Change PIN", style="Header.TLabel")
        title_label.pack(pady=20)

        # Form frame
        form_frame = ttk.Frame(self, padding=10)
        form_frame.pack(pady=20)

        # Current PIN
        old_pin_label = ttk.Label(form_frame, text="Current PIN:")
        old_pin_label.grid(row=0, column=0, sticky=tk.W, pady=10)

        self.old_pin_var = tk.StringVar()
        old_pin_entry = ttk.Entry(
            form_frame, textvariable=self.old_pin_var, show="*", width=10
        )
        old_pin_entry.grid(row=0, column=1, padx=10, pady=10)
        old_pin_entry.focus_set()

        # New PIN
        new_pin_label = ttk.Label(form_frame, text="New PIN:")
        new_pin_label.grid(row=1, column=0, sticky=tk.W, pady=10)

        self.new_pin_var = tk.StringVar()
        new_pin_entry = ttk.Entry(
            form_frame, textvariable=self.new_pin_var, show="*", width=10
        )
        new_pin_entry.grid(row=1, column=1, padx=10, pady=10)

        # Confirm new PIN
        confirm_pin_label = ttk.Label(form_frame, text="Confirm New PIN:")
        confirm_pin_label.grid(row=2, column=0, sticky=tk.W, pady=10)

        self.confirm_pin_var = tk.StringVar()
        confirm_pin_entry = ttk.Entry(
            form_frame, textvariable=self.confirm_pin_var, show="*", width=10
        )
        confirm_pin_entry.grid(row=2, column=1, padx=10, pady=10)

        # Action buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        change_button = ttk.Button(
            button_frame, text="Change PIN", command=self.change_pin
        )
        change_button.pack(side=tk.LEFT, padx=20)

        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=lambda: controller.show_frame("MainMenu"),
        )
        cancel_button.pack(side=tk.RIGHT, padx=20)

        # Bind Enter key
        old_pin_entry.bind("<Return>", lambda event: new_pin_entry.focus())
        new_pin_entry.bind("<Return>", lambda event: confirm_pin_entry.focus())
        confirm_pin_entry.bind("<Return>", lambda event: self.change_pin())

    def change_pin(self):
        """Process PIN change"""
        old_pin = self.old_pin_var.get().strip()
        new_pin = self.new_pin_var.get().strip()
        confirm_pin = self.confirm_pin_var.get().strip()

        # Validate inputs
        if not old_pin or not new_pin or not confirm_pin:
            messagebox.showerror("Invalid Input", "All fields are required")
            return

        if new_pin != confirm_pin:
            messagebox.showerror(
                "PIN Mismatch", "New PIN and confirmation do not match"
            )
            return

        if old_pin == new_pin:
            messagebox.showerror(
                "Invalid PIN", "New PIN must be different from current PIN"
            )
            return

        # Process PIN change
        success, message = self.controller.change_pin(old_pin, new_pin)

        if success:
            messagebox.showinfo("Success", message)
            self.old_pin_var.set("")
            self.new_pin_var.set("")
            self.confirm_pin_var.set("")
            self.controller.show_frame("MainMenu")
        else:
            messagebox.showerror("Error", message)


def main():
    """Main function to start the application"""
    root = tk.Tk()
    app = ATMApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
