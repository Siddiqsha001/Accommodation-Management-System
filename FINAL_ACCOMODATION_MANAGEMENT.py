import smtplib   #for sending mails
from tkinter import simpledialog    
from tkinter.simpledialog import askstring
from email.mime.text import MIMEText  #for the content of the mail box
import qrcode       #for generating QR codes
import distutils    #used to include all the library installation
from nltk.sentiment import SentimentIntensityAnalyzer  #used in feedback section
from PIL import Image, ImageTk   #opening,manipulation,displaying images
import tkinter as tk
from tkinter import messagebox
import mysql.connector
import speech_recognition as sr
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  #to display the plots in tkinter window
import nltk   #to work with human language
nltk.download('vader_lexicon')  #to identify the sentiment polarity
conn = mysql.connector.connect(
    host=" LAPTOP-E8FD7K0H",
    user="root",
    password="SI41",
    database="new"
)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255), role VARCHAR(255))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS amenities (amenity VARCHAR(255), usage_count INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS food (item VARCHAR(255), sales_count INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS gender (gender VARCHAR(255), count INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (service VARCHAR(255), cost DECIMAL(10,2))''')
conn.commit()
class AccommodationManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Accommodation Management System")
        self.cart = {} 
        self.show_login_signup()

    def show_login_signup(self):
        self.clear_window()
        self.login_frame = tk.Frame(self.root, bg="#66CD00")
        self.login_frame.pack(pady=20)

        self.label_user = tk.Label(self.login_frame, text="Username:", bg="#F5F5F5", font=("Helvetica", 12))
        self.label_user.grid(row=0, column=0, padx=5, pady=5)
        self.entry_user = tk.Entry(self.login_frame, bg="#FFFFFF")
        self.entry_user.grid(row=0, column=1, padx=5, pady=5)

        self.label_pass = tk.Label(self.login_frame, text="Password:", bg="#F5F5F5", font=("Helvetica", 12))
        self.label_pass.grid(row=1, column=0, padx=5, pady=5)
        self.entry_pass = tk.Entry(self.login_frame, show="*", bg="#FFFFFF")
        self.entry_pass.grid(row=1, column=1, padx=5, pady=5)

        self.button_login = tk.Button(self.login_frame, text="Login", command=self.login, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.button_login.grid(row=2, column=0, columnspan=2, pady=5)

        self.button_signup = tk.Button(self.login_frame, text="Sign Up", command=self.signup, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.button_signup.grid(row=3, column=0, columnspan=2, pady=5)

    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        cursor.execute('SELECT role FROM users WHERE username=%s AND password=%s', (username, password))
        result = cursor.fetchone()

        if result:
            self.clear_window()
            self.show_role_selection_page()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def signup(self):
        def record_voice():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Please speak your password...")
                audio = recognizer.listen(source)
            return audio
        username = self.entry_user.get()
        self.signup_window = tk.Toplevel(self.root)
        self.signup_window.title("Sign Up")
        self.signup_window.configure(bg="#F5F5F5")
        tk.Label(self.signup_window, text="Username:", bg="#F5F5F5", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.signup_username_entry = tk.Entry(self.signup_window)
        self.signup_username_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.signup_window, text="Password:", bg="#F5F5F5", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.signup_password_entry = tk.Entry(self.signup_window, show="*")
        self.signup_password_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.signup_window, text="Sign Up", command=self.save_signup_details, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def save_signup_details(self):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")
            return
        if username and password:
            cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', (username, password, 'customer'))
            conn.commit()
            messagebox.showinfo("Success", "Sign up successful! You can now login.")
            self.signup_window.destroy() 
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    def show_profit_graph(self):
        self.clear_window()
        self.profit_frame = tk.Frame(self.root)
        self.profit_frame.pack(pady=20)
        self.label_profit = tk.Label(self.profit_frame, text="Profit Graph")
        self.label_profit.pack(pady=10)
        cursor.execute("""
            SELECT service, COALESCE(SUM(cost), 0) 
            FROM (
                SELECT DISTINCT service FROM bookings
            ) AS all_services
            LEFT JOIN bookings USING (service)
            GROUP BY service
        """)
        results = cursor.fetchall()
        services = [row[0] for row in results]
        profits = [row[1] for row in results]
        fig, ax = plt.subplots()
        ax.bar(services, profits)
        ax.set_xlabel('Service')
        ax.set_ylabel('Profit')
        ax.set_title('Profit by Service')
        canvas = FigureCanvasTkAgg(fig, master=self.profit_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.button_back = tk.Button(self.profit_frame, text="Back", command=self.show_manager_page)
        self.button_back.pack(pady=10)

    def show_role_selection_page(self):
        self.clear_window()
        self.role_selection_frame = tk.Frame(self.root, bg="#00B2EE")
        self.role_selection_frame.pack(pady=20)
        self.label_role = tk.Label(self.role_selection_frame, text="Are you a manager or a customer?", bg="#00BFFF", font=("Helvetica", 12))
        self.label_role.grid(row=0, column=0, padx=5, pady=5)
        self.button_manager = tk.Button(self.role_selection_frame, text="Manager", command=self.login_as_manager, bg="#104E8B", fg="white", font=("Helvetica", 12))
        self.button_manager.grid(row=1, column=0, padx=5, pady=5)
        self.button_customer = tk.Button(self.role_selection_frame, text="Customer", command=self.show_customer_page, bg="#104E8B", fg="white", font=("Helvetica", 12))
        self.button_customer.grid(row=2, column=0, padx=5, pady=5)

    def login_as_manager(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            self.root.update()
            messagebox.showinfo("Voice Recognition", "Speak your password to login as manager.")
            audio = recognizer.listen(source)
        try:
            recognized_text = recognizer.recognize_google(audio)
            if "manager" in recognized_text.lower():
                messagebox.showinfo("Voice Recognition", "Access granted. Logging in as manager.")
                self.show_manager_page()
            else:
                messagebox.showerror("Voice Recognition", "Access denied. You are not recognized as a manager.")
        except sr.UnknownValueError:
            messagebox.showerror("Voice Recognition", "Sorry, I could not understand what you said.")
        except sr.RequestError:
            messagebox.showerror("Voice Recognition", "Sorry, I'm having trouble accessing the Google API. Please check your internet connection.")

    def show_profit_graph(self):
        self.clear_window()
        self.profit_frame = tk.Frame(self.root)
        self.profit_frame.pack(pady=20)
        self.label_profit = tk.Label(self.profit_frame, text="Profit Graph")
        self.label_profit.pack(pady=10)
        cursor.execute("""
            SELECT service, COALESCE(SUM(cost), 0) 
            FROM (
                SELECT DISTINCT service FROM bookings
            ) AS all_services
            LEFT JOIN bookings USING (service)
            GROUP BY service
        """)
        results = cursor.fetchall()
        services = [row[0] for row in results]
        profits = [row[1] for row in results]
        fig, ax = plt.subplots()
        ax.bar(services, profits)
        ax.set_xlabel('Service')
        ax.set_ylabel('Profit')
        ax.set_title('Profit by Service')
        canvas = FigureCanvasTkAgg(fig, master=self.profit_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.button_back = tk.Button(self.profit_frame, text="Back", command=self.show_manager_page)
        self.button_back.pack(pady=10)

    def show_manager_page(self):
        self.clear_window()
        self.manager_frame = tk.Frame(self.root, bg="#FF69B4")
        self.manager_frame.pack(pady=20)
        self.label_manager = tk.Label(self.manager_frame, text="Welcome, Manager!", bg="#FF69B4", font=("Helvetica", 16, "bold"))
        self.label_manager.pack(pady=10)
        self.button_profit_graph = tk.Button(self.manager_frame, text="View Profit Graph", command=self.show_profit_graph, bg="#8B0A50", fg="white", font=("Helvetica", 12))
        self.button_profit_graph.pack(pady=10)
        self.button_profit_graph = tk.Button(self.manager_frame, text="View Customer feedback", command=self.show_feedback_summary, bg="#8B0A50", fg="white", font=("Helvetica", 12))
        self.button_profit_graph.pack(pady=10)
        self.button_back = tk.Button(self.manager_frame, text="Back", command=self.show_role_selection_page, bg="#8B0A50", fg="white", font=("Helvetica", 12))
        self.button_back.pack(pady=10)

    def show_customer_page(self):
        self.clear_window()
        self.customer_welcome_frame = tk.Frame(self.root, bg="#FFB6C1")
        self.customer_welcome_frame.pack(pady=20)
        self.label_customer_welcome = tk.Label(self.customer_welcome_frame, text="Welcome to Hotel Magnificent!", bg="#FFB6C1", font=("Helvetica", 16, "bold"))
        self.label_customer_welcome.pack(pady=10)
        cursor.execute("SELECT service, SUM(cost) FROM bookings GROUP BY service")
        booking_data = cursor.fetchall()
        self.button_enter = tk.Button(self.customer_welcome_frame, text="Enter", command=self.show_services_page, bg="#F08080", fg="white", font=("Helvetica", 12))
        self.button_enter.pack(pady=10)
        self.button_back = tk.Button(self.customer_welcome_frame, text="Back", command=self.show_role_selection_page, bg="#F08080", fg="white", font=("Helvetica", 12))
        self.button_back.pack(pady=10)

    def show_services_page(self):
        self.clear_window()
        self.services_frame = tk.Frame(self.root, bg="#DA70D6")
        self.services_frame.pack(pady=20)
        self.label_services = tk.Label(self.services_frame, text="Choose a service:", bg="#DA70D6", font=("Helvetica", 12))
        self.label_services.grid(row=0, column=0, padx=5, pady=5)
        services = ["Spa", "Naturals", "Cafe", "Canteen", "Gym", "Laundry", "Parlour", "Room Bookings"]
        for i, service in enumerate(services, start=1):
            button = tk.Button(self.services_frame, text=service, command=lambda service=service: self.show_menu_page(service), bg="#8B4789", fg="white", font=("Helvetica", 12))
            button.grid(row=i, column=0, padx=5, pady=5)
        self.button_view_cart = tk.Button(self.services_frame, text="View Cart", command=self.show_cart_page, bg="#8B4789", fg="white", font=("Helvetica", 12))
        self.button_view_cart.grid(row=len(services)+1, column=0, padx=5, pady=5)
        self.button_back = tk.Button(self.services_frame, text="Back", command=self.show_customer_page, bg="#8B4789", fg="white", font=("Helvetica", 12))
        self.button_back.grid(row=len(services)+2, column=0, padx=5, pady=5)

    def show_cart_page(self):
        self.clear_window()
        self.cart_frame = tk.Frame(self.root,bg="#BBFFFF")
        self.cart_frame.pack(pady=20)
        self.label_cart = tk.Label(self.cart_frame, text="Cart",bg="#BBFFFF")
        self.label_cart.pack(pady=10)
        total_amount = 0
        for key, value in self.cart.items():
            
            item = key[1]
            price = value
            label_item = tk.Label(self.cart_frame, text=f"{item}: rupees{price}",bg="#BBFFFF")
            label_item.pack()
            total_amount += price
        self.label_total = tk.Label(self.cart_frame, text=f"Total Amount: rupees{total_amount}",bg="#BBFFFF")
        self.label_total.pack()
        self.button_generate_bill = tk.Button(self.cart_frame, text="Generate Bill",bg="#96CDCD", command=self.generate_bill_page)
        self.button_generate_bill.pack(pady=10)
        self.button_back = tk.Button(self.cart_frame, text="Back",bg="#96CDCD", command=self.show_services_page)
        self.button_back.pack(pady=10)

    def generate_bill_page(self):
        self.clear_window()
        self.bill_frame = tk.Frame(self.root)
        self.bill_frame.pack(pady=20)
        current_datetime = datetime.datetime.now()
        date = current_datetime.strftime("%Y-%m-%d")
        time = current_datetime.strftime("%H:%M:%S")
        hotel_name = "Hotel Magnificent"
        total_amount = 0
        for key, value in self.cart.items():
            total_amount += value
        gst_rate = 18
        gst_amount = (gst_rate / 100) * total_amount
        total_amount_with_gst = total_amount + gst_amount
        label_bill_heading = tk.Label(self.bill_frame, text=f"{hotel_name} - Bill", font=("Helvetica", 16, "bold"))
        label_bill_heading.pack()
        label_date_time = tk.Label(self.bill_frame, text=f"Date: {date}   Time: {time}", font=("Helvetica", 10))
        label_date_time.pack()
        bill_text = tk.Text(self.bill_frame, width=40, height=20, font=("Helvetica", 10))
        bill_text.pack(pady=10)
        bill_text.insert(tk.END, "Item\t\tQuantity\t\tPrice\n")
        for key, value in self.cart.items():
            item = key[1]
            quantity = 1 
            price = value
            total_cost = price * quantity
            bill_text.insert(tk.END, f"{item}\t\t{quantity}\t\trupees{total_cost:.2f}\n")
        bill_text.insert(tk.END, "\n")
        bill_text.insert(tk.END, f"Subtotal:\t\t\t\trupees{total_amount:.2f}\n")
        bill_text.insert(tk.END, f"GST ({gst_rate}%):\t\t\trupees{gst_amount:.2f}\n")
        bill_text.insert(tk.END, "-" * 12 + "\n")
        bill_text.insert(tk.END, f"Total Amount (incl. GST):\trupees{total_amount_with_gst:.2f}\n")
        qr_data = f"Total Amount: rupees{total_amount_with_gst:.2f}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        qr_img = qr_img.resize((200, 200), Image.LANCZOS)
        qr_photo = ImageTk.PhotoImage(qr_img)
        label_qr = tk.Label(self.bill_frame, image=qr_photo)
        label_qr.image = qr_photo 
        label_qr.pack(pady=10)
        button_checkout = tk.Button(self.bill_frame, text="Checkout", command=self.checkout)
        button_checkout.pack(pady=10)
        self.button_back = tk.Button(self.bill_frame, text="Back to Cart", command=self.show_cart_page)
        self.button_back.pack(pady=10)
        self.button_feedback = tk.Button(self.bill_frame, text="Leave Feedback", command=self.show_feedback_section, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.button_feedback.pack(pady=10) #pady -> for the position

    def checkout(self):
        total_costs = {}
        for (service, item), price in self.cart.items():
            if service not in total_costs:
                total_costs[service] = price
            else:
                total_costs[service] += price
        for service, total_cost in total_costs.items():
            cursor.execute("INSERT INTO bookings (service, cost) VALUES (%s, %s)", (service, total_cost))
            conn.commit()
        self.cart.clear()
        messagebox.showinfo("Checkout", "Checkout successful!")
        self.show_services_page()

    def add_to_cart(self, service, item, price):
        if (service, item) in self.cart:
            self.cart[(service, item)] += price 
        else:
            self.cart[(service, item)] = price
        messagebox.showinfo("Added", f"{item} added to cart.")

    def calculate_total_cart_amount(self):
        total_amount = 0
        for key, value in self.cart.items():
            total_amount += value
        return total_amount

    def remove_from_cart(self, service, item, price):
        if (service, item) in self.cart:
            if self.cart[(service, item)] > price: 
                self.cart[(service, item)] -= price
            else:
                del self.cart[(service, item)]
            messagebox.showinfo("Removed", f"{item} removed from cart.")
        else:
            messagebox.showinfo("Error", f"{item} not in cart.")

    def show_menu_page(self, service):
        self.clear_window()

        self.menu_frame = tk.Frame(self.root,bg="#FFC0CB")
        self.menu_frame.pack(pady=20)

        self.label_menu = tk.Label(self.menu_frame, text=f"{service} Menu",bg="#FFC0CB")
        self.label_menu.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        if service == "Room Bookings":
            self.label_days = tk.Label(self.menu_frame, text="Number of Days:",bg="#FFC0CB")
            self.label_days.grid(row=1, column=0, padx=10, pady=5)
            self.entry_days = tk.Entry(self.menu_frame)
            self.entry_days.grid(row=1, column=1, padx=10, pady=5)

            room_types = ["Single Room", "Double Room", "Suite", "Penthouse"]
            self.room_type_var = tk.StringVar(self.menu_frame)
            self.room_type_var.set(room_types[0])  # Default value
            self.label_room_type = tk.Label(self.menu_frame, text="Room Type:",bg="#FFC0CB")
            self.label_room_type.grid(row=2, column=0, padx=10, pady=5)
            self.room_type_dropdown = tk.OptionMenu(self.menu_frame, self.room_type_var, *room_types)
            self.room_type_dropdown.grid(row=2, column=1, padx=10, pady=5)

            self.button_calculate = tk.Button(self.menu_frame, text="Calculate Cost", command=self.calculate_room_cost,bg="#CD919E")
            self.button_calculate.grid(row=3, column=0, columnspan=2, pady=10)

        else:
            menu_items = []
            prices = []

            if service == "Spa":
                menu_items = ["Massage", "Facial", "Pedicure", "Manicure"]
                prices = [400, 400, 450, 350]
            elif service == "Naturals":
                menu_items = ["Haircut", "Hair Coloring", "Hair Styling", "Facial"]
                prices = [1500, 2000, 5500, 500]
            elif service == "Cafe":
                menu_items = ["Coffee", "Tea", "Sandwich", "Cake"]
                prices = [30, 20, 50, 40]
            elif service == "Canteen":
                menu_items = ["Lemon Rice", "Veg Biriyani", "Paratta", "Veg Pulav"]
                prices = [100, 200, 50, 60]
            elif service == "Gym":
                menu_items = ["Treadmill Session", "Weight Training", "Yoga Class", "Personal Trainer Session"]
                prices = [200, 250, 150, 500]
            elif service == "Laundry":
                menu_items = ["Wash & Fold", "Dry Cleaning", "Ironing", "Stain Removal"]
                prices = [100, 150, 50, 80]
            elif service == "Parlour":
                menu_items = ["Haircut", "Manicure", "Pedicure", "Waxing"]
                prices = [250, 150, 200, 300]
            elif service == "Room Bookings":
                menu_items = ["Single Room", "Double Room", "Suite", "Penthouse"]
                prices = [1000, 2500, 3300, 4000]

            for i, item in enumerate(menu_items, start=1):
                label_item = tk.Label(self.menu_frame, text=f"{item}: rupees {prices[i-1]}",bg="#FFC0CB")
                label_item.grid(row=i, column=0, padx=10, pady=5)
                button_plus = tk.Button(self.menu_frame, text="+", command=lambda item=item: self.add_to_cart(service, item, prices[i-1]),bg="#CD919E")
                button_plus.grid(row=i, column=1, padx=5, pady=5)
                button_minus = tk.Button(self.menu_frame, text="-", command=lambda item=item: self.remove_from_cart(service, item, prices[i-1]),bg="#CD919E")
                button_minus.grid(row=i, column=2, padx=5, pady=5)
        self.button_back = tk.Button(self.menu_frame, text="Back", command=self.show_services_page,bg="#CD919E")
        self.button_back.grid(row=4 if service == "Room Bookings" else len(menu_items)+1, column=0, columnspan=3, pady=10)
        self.button_view_cart = tk.Button(self.menu_frame, text="View Cart", command=self.show_cart_page,bg="#CD919E")
        self.button_view_cart.grid(row=5 if service == "Room Bookings" else len(menu_items)+2, column=0, columnspan=3, pady=10)

    def calculate_room_cost(self):
        try:
            num_days = int(self.entry_days.get())
            room_type = self.room_type_var.get()
            room_prices = {
                "Single Room": 1000,
                "Double Room": 2500,
                "Suite": 3300,
                "Penthouse": 4000
            }
            total_cost = num_days * room_prices[room_type]
            self.add_to_cart("Room Bookings", f"Days-{num_days} in {room_type}", total_cost)
            messagebox.showinfo("Cost", f"The total cost for {num_days} days in a {room_type} is rupees{total_cost}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of days.")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_feedback_section(self):
        self.clear_window()
        self.feedback_frame = tk.Frame(self.root, bg="#FFBBFF")
        self.feedback_frame.pack(pady=20)
        self.label_feedback = tk.Label(self.feedback_frame, text="Feedback Section", bg="#FFBBFF", font=("Helvetica", 16, "bold"))
        self.label_feedback.pack(pady=10)
        self.label_comment = tk.Label(self.feedback_frame, text="Please provide your feedback:", bg="#FFBBFF", font=("Helvetica", 12))
        self.label_comment.pack(pady=5)
        self.entry_comment = tk.Text(self.feedback_frame, height=5, width=40)
        self.entry_comment.pack(pady=5)
        self.label_rating = tk.Label(self.feedback_frame, text="Rate your experience (out of 5):", bg="#FFBBFF", font=("Helvetica", 12))
        self.label_rating.pack(pady=5)
        self.rating_scale = tk.Scale(self.feedback_frame, from_=1, to=5, orient=tk.HORIZONTAL, length=200)
        self.rating_scale.pack(pady=5)
        self.button_submit_feedback = tk.Button(self.feedback_frame, text="Submit Feedback", command=self.submit_feedback, bg="#CD96CD", fg="white", font=("Helvetica", 12))
        self.button_submit_feedback.pack(pady=10)
        self.button_submit_feedback = tk.Button(self.feedback_frame, text="Back", command=self.generate_bill_page, bg="#CD96CD", fg="white", font=("Helvetica", 12))
        self.button_submit_feedback.pack(pady=10)

    def submit_feedback(self):
        try:
            feedback_text = self.entry_comment.get("1.0", "end-1c")  
            rating = self.rating_scale.get()
            sentiment_score = SentimentIntensityAnalyzer().polarity_scores(feedback_text)
            sentiment_rating = sentiment_score['compound'] 
            overall_rating = (sentiment_rating + 1) * 2.5
            cursor.execute("INSERT INTO feedback (text, rating) VALUES (%s, %s)", (feedback_text, rating))
            conn.commit()
            cursor.execute("UPDATE feedback SET frequency = frequency + 1 WHERE rating = %s", (rating,))
            conn.commit()
            sender_email = simpledialog.askstring("Email", "Enter your email address:")
            sender_password = simpledialog.askstring("Password", "Enter your email password:", show='*')
            if sender_email and sender_password: 
                receiver_email = "siddianand2005@gmail.com" 
                self.send_feedback_email(sender_email, sender_password, receiver_email, feedback_text)
                messagebox.showinfo("Feedback Updated", "Thank you for updating your feedback!")
            else:
                messagebox.showerror("Error", "Email address and password are required.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def show_feedback_summary(self):
        cursor.execute("SELECT rating, frequency FROM feedback")
        results = cursor.fetchall()
        ratings = [row[0] for row in results]
        frequencies = [row[1] for row in results]
        fig, ax = plt.subplots()
        ax.pie(frequencies, labels=ratings, autopct='%1.1f%%')
        ax.set_title('Feedback Summary')
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def send_feedback_email(self, sender_email, sender_password, receiver_email, feedback_message):
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(sender_email, sender_password)
            message = MIMEText(feedback_message)
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Subject'] = "Feedback"
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            messagebox.showinfo("Email Sent", "Feedback email sent successfully!")
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Error", "Failed to authenticate with the email server. Please check your email and password.")
        except smtplib.SMTPRecipientsRefused:
            messagebox.showerror("Error", "The recipient's email address was refused.")
        except smtplib.SMTPException as e:
            messagebox.showerror("Error", f"An SMTP error occurred: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AccommodationManagementApp(root)
    root.mainloop()
