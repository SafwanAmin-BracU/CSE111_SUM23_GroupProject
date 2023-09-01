import hashlib as hl
import json
import logging
import time
from functools import wraps

import pandas as pd
from IPython.display import HTML, ProgressBar, clear_output, display
from jinja2 import Environment, FileSystemLoader

# Configure the logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Create a FileHandler with the filename 'main.log'
log_file = "main.log"
file_handler = logging.FileHandler(log_file)

# Create a formatter to specify the log message format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the FileHandler to the logger
logger.addHandler(file_handler)

# BY NAFIS
class Book:
    # class variables
    all_books: dict = {}
    # Constructor

    def __init__(self, isbn, title, author, year, genre, price, quantity):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.price = price
        self.quantity = quantity
        Book.all_books[isbn] = self

    def get_book_details(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "price": self.price,
            "quantity": self.quantity,
        }

    def is_available(self, quantity=0):
        if quantity < 0:
            return False
        return self.quantity >= quantity

    def update_quantity(self, new_quantity, user):
        if user.is_employee:
            self.quantity = new_quantity
            return True
        else:
            return False

    def update_price(self, new_price, user):
        if user.is_employee:
            self.price = new_price
            return True
        else:
            return False

    # class methods
    @classmethod
    def search_by(cls, category, value):
        category = category.lower()
        categories = ["isbn", "title", "author", "genre"]
        result = []
        if category not in categories:
            return result
        match category:
            case "isbn":
                return cls.getBook(value)
            case _:
                for book in cls.all_books.values():
                    if getattr(book, category) == value:
                        result.append(book)
                return result

    @classmethod
    def getBook(cls, isbn):
        return cls.all_books.get(isbn, None)

    @classmethod
    def get_all_books(cls):
        return cls.all_books

    @classmethod
    def add_book(cls, isbn, title, author, year, genre, price, quantity):
        if cls.getBook(isbn):
            return False
        else:
            cls(isbn, title, author, year, genre, price, quantity)
            return True

    @classmethod
    def from_json(cls, file_path) -> None:
        with open(file_path, "rb") as f:
            all_books = json.load(f)

        print("Loading books...")
        p_bar = ProgressBar(len(all_books))
        p_bar.display()
        for book in all_books:
            cls(**book)
            p_bar.progress += 1
        clear_output(wait=True)

# BY SAFWAN
class User:
    # class variables
    all_users: dict = {}

    # Constructor
    def __init__(
        self,
        name: str,
        email: str,
        pin: str,
        address: str,
        phone: str,
        is_employee: bool = False,
    ) -> None:
        self.name: str = name
        self.email: str = email
        self.pin: str = User.encrypt_str(pin)
        self.address: str = address
        self.phone: str = phone
        self.is_employee: bool = is_employee
        self.logged_in: bool = False
        self.__class__.all_users[User.encrypt_str(email)] = self

    # instance methods
    def logout(self) -> None:
        self.logged_in = False

    def login(self, pin: str) -> bool:
        if self.pin == User.encrypt_str(pin):
            self.logged_in = True
            return True
        else:
            return False

    # class methods
    @classmethod
    def get_all_users(cls) -> list:
        return list(cls.all_users.items())

    @classmethod
    def signin(cls, email: str, pin: str) -> object:
        user = cls.all_users.get(User.encrypt_str(email), None)
        if user and user.login(pin):
            return user
        return None

    @classmethod
    def signup(
        cls,
        name: str,
        email: str,
        pin: str,
        address: str,
        phone: str,
        is_employee: bool = False,
    ) -> object:
        if cls.all_users.get(User.encrypt_str(email), None):
            return None
        else:
            return cls(
                name=name,
                email=email,
                pin=pin,
                address=address,
                phone=phone,
                is_employee=is_employee,
            )

    @classmethod
    def delete_user(cls, admin, user_email):
        if admin.is_employee:
            del cls.all_users[User.encrypt_str(user_email)]
            return True
        return False

    @classmethod
    def from_json(cls, file_path) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            all_users = json.load(f)
        for user in all_users:
            cls(**user)

    # static methods

    @staticmethod
    def encrypt_str(x_str: str) -> str:
        return hl.sha256(x_str.encode()).hexdigest()

# BY SAFWAN
class Customer(User):
    # class variables
    all_customers: dict = {}

    # Constructor
    def __init__(
        self,
        name: str,
        email: str,
        pin: str,
        address: str,
        phone: str,
        member_type: str,
    ) -> None:
        super().__init__(name, email, pin, address, phone, False)
        self.member_type: str = member_type
        self.orders: dict = {}
        self.cart: Cart = Cart(self)
        self.total_spent: float = 0
        Customer.all_customers[User.encrypt_str(email)] = self

    # instance methods
    def checkout(self):
        if self.cart.can_checkout():
            order = Order(self, self.cart.items, self.cart.total)
            self.cart.clear_books()
            self.orders[order.order_id] = order
            return True
        return False

    # class methods
    @classmethod
    def get_all_customers(cls):
        return cls.all_customers

    @classmethod
    def from_json(cls, file_path) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            all_customers = json.load(f)
        print("Loading customers...")
        p_bar = ProgressBar(len(all_customers))
        p_bar.display()
        for customer in all_customers:
            cls(**customer)
            p_bar.progress += 1
        clear_output(wait=True)

# BY NAFIS
class Employee(User):
    # class variables
    all_employees: dict = {}

    # Constructor
    def __init__(
        self,
        name: str,
        email: str,
        pin: str,
        address: str,
        phone: str,
        designation: str,
    ) -> None:
        super().__init__(name, email, pin, address, phone, True)
        self.designation: str = designation
        Employee.all_employees[User.encrypt_str(email)] = self

    # instance methods

    # class methods

    @classmethod
    def get_all_employees(cls):
        return cls.all_employees

    @classmethod
    def from_json(cls, file_path) -> None:
        with open(file_path, "rb") as f:
            all_employees = json.load(f)
        print("Loading employees...")
        p_bar = ProgressBar(len(all_employees))
        p_bar.display()
        for employee in all_employees:
            cls(**employee)
            p_bar.progress += 1
        clear_output(wait=True)

# BY MAIMUNA
class Cart:
    def __init__(self, customer):
        self.customer = customer
        self.items = {}
        self.total = 0

    def getcartDict(self):
        books = []
        for book, qty in self.items.items():
            _book = {
                "isbn": book.isbn,
                "title": book.title,
                "price": book.price,
                "quantity": qty,
            }
            books.append(_book)
        return books

    def add_book(self, isbn, qty=1):
        book = Book.getBook(isbn)
        if qty > 0 and book and book.is_available(qty):
            self.items[book] = qty
            self.total += book.price * qty
            book.quantity -= qty
            return True
        else:
            return False

    def remove_book(self, isbn):
        book = Book.getBook(isbn)
        amount_in_cart = self.items.get(book, 0)
        if book and amount_in_cart:
            self.total -= book.price * amount_in_cart
            book.quantity += amount_in_cart
            del self.items[book]
            return True
        else:
            return False

    def clear_books(self):
        self.__init__(self.customer)

    def can_checkout(self):
        return self.total and self.items

    # class methods

# BY MAIMUNA
class Order:
    all_orders = {}
    last_order_id = 0

    def __init__(self, customer, items, total):
        self.order_id = str(f"{Order.last_order_id:06d}")
        self.customer = customer
        self.items = items
        self.total = total
        self.approved = False
        self.rejected = False
        Order.all_orders[self.order_id] = self
        Order.last_order_id = Order.last_order_id + 1

    def get_order_details(self):
        return {
            "order_id": self.order_id,
            "items": len(self.items),
            "total": self.total,
            "approved": self.approved,
            "rejected": self.rejected,
        }

    def approve(self, employee):
        if employee.is_employee:
            self.approved = True
            self.rejected = False
            return True
        return False

    def cancel(self, employee):
        if employee.is_employee:
            self.rejected = True
            self.approved = False
            for book, qty in self.items.items():
                book.quantity += qty
            return True
        return False

    @classmethod
    def get_all_orders(cls):
        return cls.all_orders

    @classmethod
    def get_pending_orders(cls):
        return [
            {
                "order_id": order.order_id,
                "customer_name": order.customer.name,
                "item_count": len(order.items),
                "total": order.total,
                "approved": order.approved,
            }
            for order in cls.all_orders.values()
            if not (order.approved or order.rejected)
        ]

    @classmethod
    def get_order_by_id(cls, order_id):
        return cls.all_orders.get(order_id, None)

# BY SAFWAN
class BookStore:
    def __init__(self, name: str, address: str) -> None:
        self.name: str = name
        self.address: str = address
        self.current_user: User = None
        self.total_sales: float = 0
        self.pending_sales: int = 0
        self.completed_sales: int = 0

    def update_sales(self):
        for order in Order.get_all_orders().values():
            if order.approved:
                self.completed_sales += 1
                self.total_sales += order.total
            else:
                self.pending_sales += 1

    def run(self) -> None:
        # EVENTLOOP DECORATOR
        break_loop_flag = False
        crash: bool = False

        def eventloop(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                nonlocal break_loop_flag
                while True:
                    func(*args, **kwargs)
                    if break_loop_flag:
                        break_loop_flag = False
                        break
                    time.sleep(0.09)  # set to 0.09 to avoid keyboard input lag

            return wrapper

        # JINJA2 TEMPLATE RENDERER
        env = Environment(loader=FileSystemLoader("./screens/"))

        def render(template_name: str, *args, **kwargs) -> str:
            return env.get_template(template_name).render(*args, **kwargs)

        # MISCELLANEOUS FUNCTIONS

        def break_loop() -> None:
            nonlocal break_loop_flag
            break_loop_flag = True

        # SEARCH RESULTS SCREEN
        @eventloop
        def screen_search(
            searchTitle, headers, body, noResult=True, noResultMsg="No Reasons Given"
        ) -> None:
            clear_output(wait=True)
            display(
                HTML(
                    render(
                        "search.j2",
                        searchTitle=searchTitle,
                        headers=headers,
                        body=body,
                        noResult=noResult,
                        noResultMsg=noResultMsg,
                    )
                )
            )
            choice = input("Enter your choice: ")
            match choice:
                case "BACK":
                    break_loop()
                case _:
                    ...

        # EMPLOYEE SCREENS
        employeeData = {}

        @eventloop
        def screen_employee():
            clear_output(wait=True)
            nonlocal employeeData
            employeeData["userName"] = self.current_user.name
            employeeData["userEmail"] = self.current_user.email
            employeeData["userDesignation"] = self.current_user.designation
            employeeData["pendingOrders"] = Order.get_pending_orders()
            employeeData["pendingOrdersCount"] = len(employeeData["pendingOrders"])
            display(HTML(render("employee.j2", employeeData)))
            choice = input("Enter your choice: ")
            match choice:
                case "Logout":
                    self.current_user.logout()
                    self.current_user = None
                    break_loop()
                case "Confirm Order":
                    clear_output(wait=True)
                    renderScreen = "<h1>CONFIRM ORDER</h1><br><h2>PLEASE WAIT</h2>"
                    choice = input("Enter order id: ")
                    if order := Order.get_order_by_id(choice):
                        if order.approve(self.current_user):
                            renderScreen = "<h1>ORDER APPROVED</h1>"
                            display(HTML(renderScreen))
                            time.sleep(2)
                    else:
                        renderScreen = "<h1>ORDER NOT FOUND</h1>"
                        display(HTML(renderScreen))
                        time.sleep(2)
                case _:
                    ...

        # CUSTOMER SCREENS
        customerData = {
            "books": [],
            "cartTotal": 0,
            "cartItemsCount": 0,
        }

        @eventloop
        def screen_customer():
            nonlocal customerData
            customerData["userName"] = self.current_user.name
            customerData["userEmail"] = self.current_user.email
            customerData["cartTotal"] = self.current_user.cart.total
            customerData["cartItemsCount"] = len(self.current_user.cart.items)
            customerData["books"] = self.current_user.cart.getcartDict()
            if customerData["cartItemsCount"]:
                df = pd.read_json(json.dumps(customerData["books"]))
                df["total"] = df["price"] * df["quantity"]
                customerData["cartItemsCount"] = df["quantity"].sum()
                customerData["books"] = df.to_dict(orient="records")
            clear_output(wait=True)
            display(HTML(render("customer.j2", customerData)))
            choice = input("Enter your choice: ")
            match choice:
                case "All Orders":
                    clear_output(wait=True)
                    rednderScreen = "<h1>ALL ORDERS</h1><br><h2>PLEASE WAIT</h2>"
                    display(HTML(rednderScreen))
                    clear_output(wait=True)
                    searchTitle = "ALL ORDERS"
                    headers = [
                        "Order ID",
                        "Total Items",
                        "Total Price",
                        "Approved",
                        "Rejected",
                    ]
                    body = [
                        list(order.get_order_details().values())
                        for order in self.current_user.orders.values()
                    ]
                    screen_search(searchTitle, headers, body, False, "No Orders Found!")
                case "Search Book":
                    clear_output(wait=True)
                    renderScreen = "<h1>SEARCH BOOK</h1><br><h2>PLEASE WAIT</h2>"
                    display(HTML(renderScreen))
                    searchTitle = "SEARCH BOOK"
                    while True:
                        category = input(
                            "Enter search category (isbn|title|author|genre): "
                        )
                        if category in ["isbn", "title", "author", "genre"]:
                            break
                    value = input("Enter search value: ")
                    headers = [
                        "ISBN",
                        "Title",
                        "Author",
                        "Year",
                        "Genre",
                        "Price",
                        "Quantity",
                    ]
                    body = [
                        list(book.get_book_details().values())
                        for book in Book.search_by(category=category, value=value)
                    ]
                    flag = not bool(body)
                    screen_search(
                        searchTitle=searchTitle,
                        headers=headers,
                        body=body,
                        noResult=flag,
                        noResultMsg="No Books Found!",
                    )

                case "Add Book":
                    clear_output(wait=True)
                    renderScreen = "<h1>ADD BOOK</h1><br><h2>ENTER BOOK DETAILS</h2>"
                    display(HTML(renderScreen))

                    isbn = input("Enter ISBN: ").strip()
                    qty = 0
                    while not qty:
                        try:
                            qty = int(input("Enter Quantity: ").strip())
                        except ValueError:
                            qty = int(
                                input(
                                    "Enter Quantity (Please enter a number)!: "
                                ).strip()
                            )
                    if book := Book.getBook(isbn):
                        if self.current_user.cart.add_book(isbn, qty):
                            renderScreen = "<h1>ADDED BOOK TO CART</h1>"
                            display(HTML(renderScreen))
                            time.sleep(2)
                    else:
                        renderScreen = "<h1>Please check ISBN and Quantity!</h1>"
                        display(HTML(renderScreen))
                        time.sleep(2)

                case "Remove Book":
                    clear_output(wait=True)
                    renderScreen = "<h1>REMOVE BOOK</h1><br><h2>ENTER BOOK DETAILS</h2>"
                    display(HTML(renderScreen))
                    isbn = input("Enter ISBN: ").strip()
                    if Book.getBook(isbn):
                        if self.current_user.cart.remove_book(isbn):
                            renderScreen = "<h1>REMOVED BOOK FROM CART</h1>"
                            display(HTML(renderScreen))
                            time.sleep(2)
                    else:
                        renderScreen = "<h1>Please check ISBN!</h1>"
                        display(HTML(renderScreen))
                        time.sleep(2)
                case "Checkout":
                    clear_output(wait=True)
                    renderScreen = (
                        "<h1>TRYING TO PLACE ORDER</h1><br><h2>PLEASE WAIT</h2>"
                    )
                    display(HTML(renderScreen))
                    if self.current_user.checkout():
                        renderScreen = "<h1>ORDER PLACED SUCCESSFULLY</h1>"
                        display(HTML(renderScreen))
                        time.sleep(2)
                    else:
                        renderScreen = "<h1>ORDER PLACEMENT FAILED</h1>"
                        display(HTML(renderScreen))
                        time.sleep(2)
                case "Logout":
                    self.current_user.logout()
                    self.current_user = None
                    break_loop()

        # SIGNIN SCREEN
        temp_signin_creds: dict = {}

        @eventloop
        def screen_signin():
            nonlocal temp_signin_creds
            clear_output(wait=True)
            display(HTML(render("signin.j2", temp_signin_creds)))
            # DYNAMIC SIGNIN FORM
            if not temp_signin_creds.get("userEmail", None):
                temp_signin_creds["userEmail"] = input("Enter your email: ")
            elif not temp_signin_creds.get("userPin", None):
                temp_signin_creds["userPin"] = input("Enter your pin: ")
                temp_signin_creds["signinComplete"] = True  # SIGNIN COMPLETE

            # SIGNIN FORM COMPLETE
            if temp_signin_creds.get("signinComplete", False):
                clear_output(wait=True)
                display(HTML(render("signin.j2", temp_signin_creds)))
                choice = input("Enter your choice: ")
                match choice:
                    case "ENTER":
                        clear_output(wait=True)
                        user = Customer.signin(
                            temp_signin_creds["userEmail"],
                            temp_signin_creds["userPin"],
                        )
                        if user:
                            temp_str = "<h1>SIGNIN SUCCESSFUL</h1><br><h2>WELCOME</h2>"
                            display(HTML(temp_str))
                            self.current_user = user
                            temp_signin_creds = {}
                            time.sleep(2)
                            if user.is_employee:
                                clear_output(wait=True)
                                renderScreen = "<h1>REDIRECTING TO EMPLOYEE SCREEN</h1><br><h2>PLEASE WAIT</h2>"
                                display(HTML(renderScreen))
                                screen_employee()
                            else:
                                clear_output(wait=True)
                                renderScreen = "<h1>REDIRECTING TO CUSTOMER SCREEN</h1><br><h2>PLEASE WAIT</h2>"
                                display(HTML(renderScreen))
                                screen_customer()
                            break_loop()
                        else:
                            temp_str = "<h1>SIGNIN FAILED</h1><br><h2>TRY AGAIN</h2>"
                            display(HTML(temp_str))
                            time.sleep(2)
                            temp_signin_creds = {}
                    case "CLEAR":
                        temp_signin_creds = {}
                    case "BACK":
                        break_loop()
                    case _:
                        ...

        temp_signup_creds: dict = {}
        # SIGNUP SCREEN

        @eventloop
        def screen_signup():
            nonlocal temp_signup_creds
            clear_output(wait=True)
            display(HTML(render("signup.j2", temp_signup_creds)))

            # DYNAMIC SIGNUP FORM
            if not temp_signup_creds.get("userName", None):
                temp_signup_creds["userName"] = input("Enter your name: ")
            elif not temp_signup_creds.get("userEmail", None):
                temp_signup_creds["userEmail"] = input("Enter your email: ")
            elif not temp_signup_creds.get("userPin", None):
                temp_signup_creds["userPin"] = input("Enter your pin: ")
            elif not temp_signup_creds.get("userAddress", None):
                temp_signup_creds["userAddress"] = input("Enter your address: ")
            elif not temp_signup_creds.get("userPhone", None):
                temp_signup_creds["userPhone"] = input("Enter your phone: ")
                temp_signup_creds["signupComplete"] = True  # SIGNUP COMPLETE

            # SIGNUP FORM COMPLETE
            if temp_signup_creds.get("signupComplete", False):
                clear_output(wait=True)
                display(HTML(render("signup.j2", temp_signup_creds)))
                choice = input("Enter your choice: ")
                match choice:
                    case "ENTER":
                        clear_output(wait=True)
                        user = Customer.signup(**temp_signup_creds)
                        if user:
                            tempStr = "<h1>SIGNUP SUCCESSFUL</h1><br><h2>LOGIN TO CONTINUE</h2>"
                            display(HTML(tempStr))
                            time.sleep(2)
                            temp_signup_creds = {}
                            break_loop()
                        else:
                            tempStr = "<h1>SIGNUP FAILED</h1><br><h2>TRY AGAIN</h2>"
                            display(HTML(tempStr))
                            time.sleep(2)
                            temp_signup_creds = {}
                    case "CLEAR":
                        temp_signup_creds = {}
                    case "BACK":
                        break_loop()
                    case _:
                        ...

        # LOGIN SCREEN

        @eventloop
        def screen_login() -> None:
            clear_output(wait=True)
            display(HTML(render("login.j2")))
            choice = input("Enter your choice: ")
            match choice:
                case "SIGN UP":
                    screen_signup()
                case "SIGN IN":
                    screen_signin()
                case "BACK":
                    break_loop()
                case _:
                    ...

        # WELCOME SCREEN

        @eventloop
        def screen_welcome() -> None:
            clear_output(wait=True)
            display(
                HTML(render("home.j2", storeName=self.name, storeAddress=self.address))
            )
            choice = input("Enter your choice: ")
            match choice:
                case "LOGIN":
                    screen_login()
                case "EXIT":
                    break_loop()
                case _:
                    ...

        # MAINLOOP

        def mainloop():
            nonlocal crash
            try:
                screen_welcome()
                clear_output(wait=True)
                display(HTML(render("shutdown.j2", crash=crash)))
            except Exception as exception:
                crash = True
                clear_output(wait=True)
                display(HTML(render("shutdown.j2", crash=crash, exception=exception)))
                logger.exception(exception)
            except KeyboardInterrupt:
                crash = True
                clear_output(wait=True)
                display(HTML(render("shutdown.j2", crash=crash)))

        # RUN MAINLOOP
        mainloop()
