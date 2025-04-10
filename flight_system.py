import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


class FlightBookingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Flight Booking System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Database connection
        self.conn = None
        self.cursor = None
        self.current_user = None

        # Initialize the database
        self.init_database()

        # Create the login frame
        self.create_login_frame()

    def init_database(self):
        """Initialize database connection and create tables if they don't exist"""
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with your MySQL username
                password="abishek@123",  # Replace with your MySQL password
                database="flight_booking",  # Create this database first
            )
            self.cursor = self.conn.cursor(buffered=True)

            # Create tables if they don't exist
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL
                )
            """
            )

            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS flights (
                    flight_id INT AUTO_INCREMENT PRIMARY KEY,
                    airline VARCHAR(100) NOT NULL,
                    source VARCHAR(100) NOT NULL,
                    destination VARCHAR(100) NOT NULL,
                    departure_time DATETIME NOT NULL,
                    arrival_time DATETIME NOT NULL,
                    price DECIMAL(10, 2) NOT NULL
                )
            """
            )

            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    flight_id INT NOT NULL,
                    passenger_name VARCHAR(100) NOT NULL,
                    date_of_travel DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
                )
            """
            )

            # Commit the changes
            self.conn.commit()

            # Add sample flight data if the flights table is empty
            self.cursor.execute("SELECT COUNT(*) FROM flights")
            count = self.cursor.fetchone()[0]

            if count == 0:
                sample_flights = [
                    (
                        "Air India",
                        "Delhi",
                        "Mumbai",
                        "2023-09-01 10:00:00",
                        "2023-09-01 12:00:00",
                        5000,
                    ),
                    (
                        "IndiGo",
                        "Mumbai",
                        "Bangalore",
                        "2023-09-01 14:00:00",
                        "2023-09-01 16:00:00",
                        4500,
                    ),
                    (
                        "SpiceJet",
                        "Bangalore",
                        "Chennai",
                        "2023-09-01 18:00:00",
                        "2023-09-01 19:30:00",
                        3000,
                    ),
                    (
                        "Air Asia",
                        "Chennai",
                        "Kolkata",
                        "2023-09-02 08:00:00",
                        "2023-09-02 10:30:00",
                        4000,
                    ),
                    (
                        "Vistara",
                        "Delhi",
                        "Bangalore",
                        "2023-09-02 12:00:00",
                        "2023-09-02 14:30:00",
                        6000,
                    ),
                    (
                        "IndiGo",
                        "Mumbai",
                        "Delhi",
                        "2023-09-02 16:00:00",
                        "2023-09-02 18:00:00",
                        5500,
                    ),
                    (
                        "Air India",
                        "Bangalore",
                        "Mumbai",
                        "2023-09-03 09:00:00",
                        "2023-09-03 11:00:00",
                        5200,
                    ),
                    (
                        "SpiceJet",
                        "Kolkata",
                        "Delhi",
                        "2023-09-03 13:00:00",
                        "2023-09-03 15:30:00",
                        4800,
                    ),
                ]

                self.cursor.executemany(
                    """
                    INSERT INTO flights (airline, source, destination, departure_time, arrival_time, price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    sample_flights,
                )

                self.conn.commit()

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database Error", f"Failed to connect to database: {err}"
            )

    def create_login_frame(self):
        """Create the login frame"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a frame for login
        login_frame = tk.Frame(self.root, bg="#f0f0f0")
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title
        title_label = tk.Label(
            login_frame,
            text="Flight Booking System",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Email
        email_label = tk.Label(
            login_frame, text="Email:", font=("Arial", 12), bg="#f0f0f0"
        )
        email_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        email_entry = tk.Entry(login_frame, font=("Arial", 12), width=25)
        email_entry.grid(row=1, column=1, padx=10, pady=10)

        # Password
        password_label = tk.Label(
            login_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0"
        )
        password_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        password_entry = tk.Entry(login_frame, font=("Arial", 12), width=25, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Login button
        login_button = tk.Button(
            login_frame,
            text="Login",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.login(email_entry.get(), password_entry.get()),
        )
        login_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Register link
        register_label = tk.Label(
            login_frame,
            text="Don't have an account? Register here",
            font=("Arial", 10, "underline"),
            bg="#f0f0f0",
            fg="blue",
            cursor="hand2",
        )
        register_label.grid(row=4, column=0, columnspan=2)
        register_label.bind("<Button-1>", lambda e: self.create_register_frame())

    def create_register_frame(self):
        """Create the registration frame"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a frame for registration
        register_frame = tk.Frame(self.root, bg="#f0f0f0")
        register_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title
        title_label = tk.Label(
            register_frame,
            text="Register New Account",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Name
        name_label = tk.Label(
            register_frame, text="Name:", font=("Arial", 12), bg="#f0f0f0"
        )
        name_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        name_entry = tk.Entry(register_frame, font=("Arial", 12), width=25)
        name_entry.grid(row=1, column=1, padx=10, pady=10)

        # Email
        email_label = tk.Label(
            register_frame, text="Email:", font=("Arial", 12), bg="#f0f0f0"
        )
        email_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        email_entry = tk.Entry(register_frame, font=("Arial", 12), width=25)
        email_entry.grid(row=2, column=1, padx=10, pady=10)

        # Password
        password_label = tk.Label(
            register_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0"
        )
        password_label.grid(row=3, column=0, sticky="e", padx=10, pady=10)
        password_entry = tk.Entry(
            register_frame, font=("Arial", 12), width=25, show="*"
        )
        password_entry.grid(row=3, column=1, padx=10, pady=10)

        # Register button
        register_button = tk.Button(
            register_frame,
            text="Register",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.register(
                name_entry.get(), email_entry.get(), password_entry.get()
            ),
        )
        register_button.grid(row=4, column=0, columnspan=2, pady=20)

        # Login link
        login_label = tk.Label(
            register_frame,
            text="Already have an account? Login here",
            font=("Arial", 10, "underline"),
            bg="#f0f0f0",
            fg="blue",
            cursor="hand2",
        )
        login_label.grid(row=5, column=0, columnspan=2)
        login_label.bind("<Button-1>", lambda e: self.create_login_frame())

    def login(self, email, password):
        """Login the user"""
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return

        try:
            self.cursor.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s",
                (email, password),
            )
            user = self.cursor.fetchone()

            if user:
                self.current_user = {"id": user[0], "name": user[1], "email": user[2]}
                messagebox.showinfo("Success", f"Welcome back, {user[1]}!")
                self.create_dashboard()
            else:
                messagebox.showerror("Error", "Invalid email or password")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Login failed: {err}")

    def register(self, name, email, password):
        """Register a new user"""
        if not name or not email or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            self.cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password),
            )
            self.conn.commit()

            # Get the user ID
            self.cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            user_id = self.cursor.fetchone()[0]

            self.current_user = {"id": user_id, "name": name, "email": email}
            messagebox.showinfo("Success", "Registration successful!")
            self.create_dashboard()
        except mysql.connector.Error as err:
            if err.errno == 1062:  # Duplicate entry error
                messagebox.showerror("Error", "Email already exists")
            else:
                messagebox.showerror("Database Error", f"Registration failed: {err}")

    def create_dashboard(self):
        """Create the dashboard frame after login"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a frame for the dashboard
        dashboard_frame = tk.Frame(self.root, bg="#f0f0f0")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # Create a navigation frame
        nav_frame = tk.Frame(dashboard_frame, bg="#333333", height=50)
        nav_frame.pack(fill=tk.X)

        # Welcome label
        welcome_label = tk.Label(
            nav_frame,
            text=f"Welcome, {self.current_user['name']}",
            font=("Arial", 12, "bold"),
            bg="#333333",
            fg="white",
        )
        welcome_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Search flights button
        search_button = tk.Button(
            nav_frame,
            text="Search Flights",
            font=("Arial", 10),
            command=self.create_search_frame,
        )
        search_button.pack(side=tk.LEFT, padx=10, pady=10)

        # My bookings button
        bookings_button = tk.Button(
            nav_frame,
            text="My Bookings",
            font=("Arial", 10),
            command=self.show_bookings,
        )
        bookings_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Logout button
        logout_button = tk.Button(
            nav_frame, text="Logout", font=("Arial", 10), command=self.logout
        )
        logout_button.pack(side=tk.RIGHT, padx=20, pady=10)

        # Content frame
        self.content_frame = tk.Frame(dashboard_frame, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Welcome message
        welcome_message = tk.Label(
            self.content_frame,
            text="Welcome to Flight Booking System",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
        )
        welcome_message.pack(pady=50)

        instructions = tk.Label(
            self.content_frame,
            text="Use the navigation buttons above to search for flights or view your bookings.",
            font=("Arial", 12),
            bg="#f0f0f0",
            wraplength=600,
        )
        instructions.pack(pady=20)

    def clear_content_frame(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_search_frame(self):
        """Create the flight search frame"""
        self.clear_content_frame()

        # Title
        title_label = tk.Label(
            self.content_frame,
            text="Search Flights",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
        )
        title_label.pack(pady=20)

        # Create a frame for search inputs
        search_inputs_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        search_inputs_frame.pack(pady=20)

        # Get unique sources and destinations for dropdowns
        self.cursor.execute("SELECT DISTINCT source FROM flights ORDER BY source")
        sources = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute(
            "SELECT DISTINCT destination FROM flights ORDER BY destination"
        )
        destinations = [row[0] for row in self.cursor.fetchall()]

        # Source
        source_label = tk.Label(
            search_inputs_frame, text="Source:", font=("Arial", 12), bg="#f0f0f0"
        )
        source_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        source_combo = ttk.Combobox(
            search_inputs_frame, font=("Arial", 12), width=20, values=sources
        )
        source_combo.grid(row=0, column=1, padx=10, pady=10)

        # Destination
        dest_label = tk.Label(
            search_inputs_frame, text="Destination:", font=("Arial", 12), bg="#f0f0f0"
        )
        dest_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        dest_combo = ttk.Combobox(
            search_inputs_frame, font=("Arial", 12), width=20, values=destinations
        )
        dest_combo.grid(row=0, column=3, padx=10, pady=10)

        # Search button
        search_button = tk.Button(
            search_inputs_frame,
            text="Search",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.search_flights(source_combo.get(), dest_combo.get()),
        )
        search_button.grid(row=1, column=0, columnspan=4, pady=20)

        # Create a frame for search results
        self.results_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=20)

    def search_flights(self, source, destination):
        """Search for flights based on source and destination"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not source or not destination:
            messagebox.showerror("Error", "Please select source and destination")
            return

        try:
            # Fetch matching flights
            self.cursor.execute(
                """
                SELECT flight_id, airline, source, destination, departure_time, arrival_time, price 
                FROM flights 
                WHERE source = %s AND destination = %s
            """,
                (source, destination),
            )

            flights = self.cursor.fetchall()

            if not flights:
                no_flights_label = tk.Label(
                    self.results_frame,
                    text="No flights found for the selected route.",
                    font=("Arial", 12),
                    bg="#f0f0f0",
                )
                no_flights_label.pack(pady=20)
                return

            # Create a treeview for flight results
            columns = (
                "Flight ID",
                "Airline",
                "Source",
                "Destination",
                "Departure",
                "Arrival",
                "Price",
            )
            tree = ttk.Treeview(
                self.results_frame, columns=columns, show="headings", height=10
            )

            # Configure the columns
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor=tk.CENTER)

            # Insert the flights
            for flight in flights:
                # Format datetime objects
                departure = flight[4].strftime("%Y-%m-%d %H:%M")
                arrival = flight[5].strftime("%Y-%m-%d %H:%M")

                tree.insert(
                    "",
                    tk.END,
                    values=(
                        flight[0],
                        flight[1],
                        flight[2],
                        flight[3],
                        departure,
                        arrival,
                        f"₹{flight[6]}",
                    ),
                )

            tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Add a scrollbar
            scrollbar = ttk.Scrollbar(
                self.results_frame, orient=tk.VERTICAL, command=tree.yview
            )
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Book flight button
            book_button = tk.Button(
                self.results_frame,
                text="Book Selected Flight",
                font=("Arial", 12),
                bg="#4CAF50",
                fg="white",
                command=lambda: self.create_booking_frame(
                    tree.item(tree.selection())["values"] if tree.selection() else None
                ),
            )
            book_button.pack(pady=20)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Search failed: {err}")

    def create_booking_frame(self, selected_flight):
        """Create the booking frame for a selected flight"""
        if not selected_flight:
            messagebox.showerror("Error", "Please select a flight to book")
            return

        # Clear content frame
        self.clear_content_frame()

        # Title
        title_label = tk.Label(
            self.content_frame,
            text="Book Flight",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
        )
        title_label.pack(pady=20)

        # Flight details frame
        flight_details_frame = tk.Frame(
            self.content_frame, bg="#f0f0f0", bd=1, relief=tk.SOLID
        )
        flight_details_frame.pack(fill=tk.X, padx=20, pady=10)

        # Flight ID
        flight_id = selected_flight[0]

        # Flight information
        info_text = f"Flight: {selected_flight[1]} ({flight_id})\n"
        info_text += f"Route: {selected_flight[2]} → {selected_flight[3]}\n"
        info_text += f"Departure: {selected_flight[4]}\n"
        info_text += f"Arrival: {selected_flight[5]}\n"
        info_text += f"Price: ₹{selected_flight[6]}"

        info_label = tk.Label(
            flight_details_frame,
            text=info_text,
            font=("Arial", 12),
            bg="#f0f0f0",
            justify=tk.LEFT,
            padx=20,
            pady=20,
        )
        info_label.pack()

        # Booking details frame
        booking_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        booking_frame.pack(fill=tk.X, padx=20, pady=20)

        # Passenger name
        name_label = tk.Label(
            booking_frame, text="Passenger Name:", font=("Arial", 12), bg="#f0f0f0"
        )
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_entry = tk.Entry(booking_frame, font=("Arial", 12), width=25)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        name_entry.insert(0, self.current_user["name"])  # Default to user's name

        # Travel date
        date_label = tk.Label(
            booking_frame,
            text="Date of Travel (YYYY-MM-DD):",
            font=("Arial", 12),
            bg="#f0f0f0",
        )
        date_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        date_entry = tk.Entry(booking_frame, font=("Arial", 12), width=25)
        date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        # Default to flight departure date
        departure_date = (
            selected_flight[4].split()[0]
            if isinstance(selected_flight[4], str)
            else datetime.now().strftime("%Y-%m-%d")
        )
        date_entry.insert(0, departure_date)

        # Book button
        book_button = tk.Button(
            booking_frame,
            text="Confirm Booking",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.book_flight(
                flight_id, name_entry.get(), date_entry.get()
            ),
        )
        book_button.grid(row=2, column=0, columnspan=2, pady=20)

        # Back button
        back_button = tk.Button(
            booking_frame,
            text="Back to Search",
            font=("Arial", 10),
            command=self.create_search_frame,
        )
        back_button.grid(row=3, column=0, columnspan=2)

    def book_flight(self, flight_id, passenger_name, date_of_travel):
        """Book a flight for the user"""
        if not passenger_name or not date_of_travel:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            # Validate date format
            try:
                travel_date = datetime.strptime(date_of_travel, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror(
                    "Error", "Invalid date format. Please use YYYY-MM-DD"
                )
                return

            # Insert booking
            self.cursor.execute(
                """
                INSERT INTO bookings (user_id, flight_id, passenger_name, date_of_travel)
                VALUES (%s, %s, %s, %s)
            """,
                (self.current_user["id"], flight_id, passenger_name, travel_date),
            )

            self.conn.commit()

            messagebox.showinfo("Success", "Flight booked successfully!")
            self.show_bookings()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Booking failed: {err}")

    def show_bookings(self):
        """Show the user's bookings"""
        self.clear_content_frame()

        # Title
        title_label = tk.Label(
            self.content_frame,
            text="My Bookings",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
        )
        title_label.pack(pady=20)

        try:
            # Fetch user's bookings with flight details
            self.cursor.execute(
                """
                SELECT b.booking_id, f.flight_id, f.airline, f.source, f.destination, 
                       f.departure_time, f.arrival_time, f.price, b.passenger_name, b.date_of_travel
                FROM bookings b
                JOIN flights f ON b.flight_id = f.flight_id
                WHERE b.user_id = %s
                ORDER BY b.date_of_travel DESC
            """,
                (self.current_user["id"],),
            )

            bookings = self.cursor.fetchall()

            if not bookings:
                no_bookings_label = tk.Label(
                    self.content_frame,
                    text="You don't have any bookings yet.",
                    font=("Arial", 12),
                    bg="#f0f0f0",
                )
                no_bookings_label.pack(pady=20)

                # Add a button to search flights
                search_button = tk.Button(
                    self.content_frame,
                    text="Search Flights",
                    font=("Arial", 12),
                    bg="#4CAF50",
                    fg="white",
                    command=self.create_search_frame,
                )
                search_button.pack(pady=10)
                return

            # Create a frame for bookings list
            bookings_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
            bookings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Create a canvas and scrollbar for scrolling
            canvas = tk.Canvas(bookings_frame, bg="#f0f0f0")
            scrollbar = ttk.Scrollbar(
                bookings_frame, orient=tk.VERTICAL, command=canvas.yview
            )
            scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Display each booking
            for i, booking in enumerate(bookings):
                booking_frame = tk.Frame(
                    scrollable_frame,
                    bg="#ffffff",
                    bd=1,
                    relief=tk.SOLID,
                    padx=10,
                    pady=10,
                )
                booking_frame.pack(fill=tk.X, pady=10)

                # Booking ID and flight info
                header_text = (
                    f"Booking #{booking[0]} - Flight {booking[1]} ({booking[2]})"
                )
                header_label = tk.Label(
                    booking_frame,
                    text=header_text,
                    font=("Arial", 12, "bold"),
                    bg="#ffffff",
                )
                header_label.pack(anchor="w")

                # Route and times
                departure_time = booking[5].strftime("%Y-%m-%d %H:%M")
                arrival_time = booking[6].strftime("%Y-%m-%d %H:%M")
                route_text = f"Route: {booking[3]} → {booking[4]}"
                route_label = tk.Label(
                    booking_frame, text=route_text, font=("Arial", 11), bg="#ffffff"
                )
                route_label.pack(anchor="w")

                times_text = f"Departure: {departure_time} | Arrival: {arrival_time}"
                times_label = tk.Label(
                    booking_frame, text=times_text, font=("Arial", 11), bg="#ffffff"
                )
                times_label.pack(anchor="w")

                # Passenger and date
                passenger_text = f"Passenger: {booking[8]} | Travel Date: {booking[9]}"
                passenger_label = tk.Label(
                    booking_frame, text=passenger_text, font=("Arial", 11), bg="#ffffff"
                )
                passenger_label.pack(anchor="w")

                # Price
                price_text = f"Price: ₹{booking[7]}"
                price_label = tk.Label(
                    booking_frame, text=price_text, font=("Arial", 11), bg="#ffffff"
                )
                price_label.pack(anchor="w")

            # Add a button to search more flights
            search_button = tk.Button(
                self.content_frame,
                text="Search More Flights",
                font=("Arial", 12),
                bg="#4CAF50",
                fg="white",
                command=self.create_search_frame,
            )
            search_button.pack(pady=20)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch bookings: {err}")

    def logout(self):
        """Logout the current user"""
        self.current_user = None
        messagebox.showinfo("Logout", "You have been logged out successfully")
        self.create_login_frame()

    def __del__(self):
        """Close database connection on exit"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = FlightBookingSystem(root)
    root.mainloop()
