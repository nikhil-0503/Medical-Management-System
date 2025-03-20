from tkinter import * 
from tkinter import messagebox,ttk,Tk, Frame, Label, ttk, Scrollbar, VERTICAL, HORIZONTAL
from PIL import Image, ImageTk
from customtkinter import *
import cx_Oracle
import re
from datetime import datetime, timedelta

# Establishing Oracle SQL Connectivity using Singleton class
class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, username, password):
        if not hasattr(self, 'initialized'):  # Avoid re-initialization
            try:
                dsn = "localhost:1521"
                self.connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
                self.cursor = self.connection.cursor()
                print("Database connection established successfully.")

                # Check for existing constraint before adding it
                self.check_and_add_constraint(
                    'SALES_ITEMS',
                    'check_sales_item_quantity_positive',
                    'CHECK (quantity > 0)'
                )

                # Drop existing trigger if it exists
                try:
                    self.execute_query("DROP TRIGGER update_medicine_stock", show_success=False)
                except cx_Oracle.DatabaseError:
                    pass  # Ignore error if trigger does not exist

                # Define the trigger to update medicine stock after sale item insert
                trigger_code = """
                CREATE OR REPLACE TRIGGER update_medicine_stock
                AFTER INSERT ON SALES_ITEMS
                FOR EACH ROW
                BEGIN
                    UPDATE MEDICINE
                    SET quantity = quantity - :NEW.quantity
                    WHERE medicine_id = :NEW.medicine_id
                    AND quantity >= :NEW.quantity;
                    IF SQL%ROWCOUNT = 0 THEN
                        RAISE_APPLICATION_ERROR(-20001, 'Insufficient stock in MEDICINE table.');
                    END IF;
                END;
                """
                self.execute_query(trigger_code, show_success=False)

                self.initialized = True  # Set flag to indicate initialization
            except cx_Oracle.DatabaseError as e:
                messagebox.showerror("Database Error", str(e))

    def execute_query(self, query, params=(), success_message="Operation completed successfully", show_success=True):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            error_message = str(e)
            if "ORA-20001" in error_message:  # Custom trigger error
                messagebox.showerror("Trigger Error", "Trigger prevented the operation: Insufficient stock in MEDICINE table.")
            else:
                messagebox.showerror("Database Error", error_message)

    def fetch_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
            return []

    def close(self):
        self.cursor.close()
        self.connection.close()

    def check_and_add_constraint(self, table_name, constraint_name, constraint_definition):
        # Check if the constraint already exists
        check_query = """
        SELECT COUNT(*)
        FROM all_constraints
        WHERE table_name = :table_name
        AND constraint_name = :constraint_name
        """
        result = self.fetch_query(check_query, {'table_name': table_name.upper(), 'constraint_name': constraint_name.upper()})

        # If constraint does not exist, add it
        if result and result[0][0] == 0:
            add_constraint_query = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} {constraint_definition}"
            self.execute_query(add_constraint_query, show_success=False)
            print(f"Constraint {constraint_name} added successfully.")
        else:
            print(f"Constraint {constraint_name} already exists.")

# Strategy Pattern - Different discount strategies for sales
class DiscountStrategy:
    def apply_discount(self, total):
        return total

class NoDiscount(DiscountStrategy):
    def apply_discount(self, total):
        return total

class SeasonalDiscount(DiscountStrategy):
    def apply_discount(self, total):
        return total * 0.9  # 10% discount

class FirstTimeBuyerDiscount(DiscountStrategy):
    def apply_discount(self, total):
        return total * 0.8  

# Template and Factory Patterns for Insert Operations
class InsertTemplate:
    def insert(self):
        if not self.validate():
            messagebox.showerror('Error!', 'Validation failed.')
            return
        self.perform_insert()

    def validate(self):
        """Override this method for custom validation logic."""
        raise NotImplementedError

    def perform_insert(self):
        """Override this method to insert the entity into the database."""
        raise NotImplementedError

class InsertFactory:
    @staticmethod
    def create_insert(insert_type, supplier_id=None, s_name=None, contact_number=None, email=None, address=None):
        if insert_type == 'Supplier':
            return SupplierInsert()
        # Add other types as needeed
        elif insert_type == 'Medicine':
            return MedicineInsert()
        elif insert_type == 'Customer':
            return CustomerInsert()
        elif insert_type == 'Prescription':
            return PrescriptionInsert()
        elif insert_type == 'Sales':
            return SalesInsert()
        elif insert_type == 'SalesItem':
            return SalesItemInsert()
        else:
            raise ValueError("Invalid entity type")

# Command Pattern - Queue database operations for batch execution
class Command:
    def execute(self):
        raise NotImplementedError

class InsertCommand(Command):
    def __init__(self, insert_obj):
        self.insert_obj = insert_obj

    def execute(self):
        self.insert_obj.insert()

class CommandInvoker:
    def __init__(self):
        self._commands = []

    def add_command(self, command):
        self._commands.append(command)

    def execute_commands(self):
        for command in self._commands:
            command.execute()
        self._commands.clear()  # Clear the list after executing


# Implementing Specific Insert Classes
class SupplierInsert(InsertTemplate):
    def __init__(self, supplier_id, s_name, contact_number, email, address):
        self.supplier_id = supplier_id
        self.s_name = s_name
        self.contact_number = contact_number
        self.email = email
        self.address = address

    def validate(self):
        # Implement validation logic for Supplier entity
        return bool(self.s_name and self.contact_number and self.email and self.address)

    def perform_insert(self):
        query = """
        INSERT INTO SUPPLIER (supplier_id, s_name, contact_number, email, address)
        VALUES (:supplier_id, :s_name, :contact_number, :email, :address)
        """
        params = {
            'supplier_id': self.supplier_id,
            's_name': self.s_name,
            'contact_number': self.contact_number,
            'email': self.email,
            'address': self.address
        }
        db_manager = DatabaseManager(username="your_username", password="your_password")
        db_manager.execute_query(query, params)

class MedicineInsert(InsertTemplate):
    def __init__(self, medicine_id, m_name, brand, batch_number, expiry_date, quantity, price, supplier_id):
        self.medicine_id = medicine_id
        self.m_name = m_name
        self.brand = brand
        self.batch_number = batch_number
        self.expiry_date = expiry_date
        self.quantity = quantity
        self.price = price
        self.supplier_id = supplier_id

    def validate(self):
        if not self.medicine_id or not self.m_name or not self.brand or not self.batch_number or not self.expiry_date or not self.quantity or not self.price or not self.supplier_id:
            messagebox.showerror('Error!', 'All fields are required.')
            return False
        if int(self.quantity) <= 0:
            messagebox.showerror('Error!', 'Quantity must be positive.')
            return False
        if float(self.price) <= 0:
            messagebox.showerror('Error!', 'Price must be positive.')
            return False
        if not re.match(r"^M\d{3}$", self.medicine_id):
            messagebox.showerror('Error!', 'Invalid Medicine ID format. It should start with "M" followed by three digits.')
            return False
        if not re.match(r"^BATCH\d{3}$", self.batch_number):
            messagebox.showerror('Error!', 'Invalid Batch Number format. It should start with "BATCH" followed by three digits.')
            return False
        return True

    def perform_insert(self):
        query = """INSERT INTO MEDICINE (medicine_id, m_name, brand, batch_number, expiry_date, quantity, price, supplier_id)
                   VALUES (:medicine_id, :m_name, :brand, :batch_number, :expiry_date, :quantity, :price, :supplier_id)"""
        params = {
            'medicine_id': self.medicine_id,
            'm_name': self.m_name,
            'brand': self.brand,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date,
            'quantity': self.quantity,
            'price': self.price,
            'supplier_id': self.supplier_id
        }
        dbms.execute_query(query, params)
        dbms.execute_query("COMMIT")


class CustomerInsert(InsertTemplate):
    def __init__(self, customer_id, customer_name, contact_number, email, address):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.contact_number = contact_number
        self.email = email
        self.address = address

    def validate(self):
        if not self.customer_id or not self.customer_name or not self.contact_number or not self.email or not self.address:
            messagebox.showerror('Error!', 'All fields are required.')
            return False
        if not re.match(r"^C\d{3}$", self.customer_id):
            messagebox.showerror('Error!', 'Invalid Customer ID format. It should start with "C" followed by three digits.')
            return False
        return True

    def perform_insert(self):
        query = """INSERT INTO CUSTOMER (customer_id, c_name, contact_number, email, address)
                   VALUES (:customer_id, :customer_name, :contact_number, :email, :address)"""
        params = {
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'contact_number': self.contact_number,
            'email': self.email,
            'address': self.address
        }
        dbms.execute_query(query, params)
        dbms.execute_query("COMMIT")

class PrescriptionInsert(InsertTemplate):
    def __init__(self, prescription_id, customer_id, doctor_name, prescription_date, dosage, frequency, duration, additional_instructions):
        self.prescription_id = prescription_id
        self.customer_id = customer_id
        self.doctor_name = doctor_name
        self.prescription_date = prescription_date
        self.dosage = dosage
        self.frequency = frequency
        self.duration = duration
        self.additional_instructions = additional_instructions

    def validate(self):
        if not self.prescription_id or not self.customer_id or not self.doctor_name or not self.prescription_date or not self.dosage or not self.frequency or not self.duration or not self.additional_instructions:
            messagebox.showerror('Error!', 'All fields are required.')
            return False

        # Validate Prescription ID format (should start with "P" followed by three digits)
        if not re.match(r"^P\d{3}$", self.prescription_id):
            messagebox.showerror('Error!', 'Invalid Prescription ID format. It should start with "P" followed by three digits.')
            return False

        # Check if the prescription date is in the correct format (DD-MON-YY)
        try:
            datetime.strptime(self.prescription_date, "%d-%b-%y")
        except ValueError:
            messagebox.showerror('Error!', 'Invalid date format. Please enter the prescription date in DD-MON-YY format.')
            return False
        
        # Assuming check_customer_id is defined to validate customer ID
        if not check_customer_id(self.customer_id):
            messagebox.showerror('Error!', 'Customer ID does not exist.')
            return False

        return True

    def perform_insert(self):
        query = """INSERT INTO PRESCRIPTION (prescription_id, customer_id, doctor_name, prescription_date, dosage, frequency, duration, additional_instructions)
                   VALUES (:prescription_id, :customer_id, :doctor_name, :prescription_date, :dosage, :frequency, :duration, :additional_instructions)"""
        params = {
            'prescription_id': self.prescription_id,
            'customer_id': self.customer_id,
            'doctor_name': self.doctor_name,
            'prescription_date': self.prescription_date,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'additional_instructions': self.additional_instructions
        }
        dbms.execute_query(query, params)
        dbms.execute_query("COMMIT")


class SalesInsert(InsertTemplate):
    def __init__(self, sales_id, customer_id, sales_date, total_amount, payment_method):
        self.sales_id = sales_id
        self.customer_id = customer_id
        self.sales_date = sales_date
        self.total_amount = total_amount
        self.payment_method = payment_method

    def validate(self):
        if not self.sales_id or not self.customer_id or not self.sales_date or not self.total_amount or not self.payment_method:
            messagebox.showerror('Error!', 'All fields are required.')
            return False
        if self.payment_method not in ['Cash', 'Credit Card', 'Debit Card', 'Online','UPI']:
            messagebox.showerror('Error!', 'Invalid payment method. Choose from: Cash, Credit Card, Debit Card, Online, or UPI.')
            return False
        return True

    def perform_insert(self):
        query = """INSERT INTO SALES (sale_id, customer_id, sale_date, total_amount, payment_method)
                   VALUES (:sales_id, :customer_id, :sales_date, :total_amount, :payment_method)"""
        params = {
            'sales_id': self.sales_id,
            'customer_id': self.customer_id,
            'sales_date': self.sales_date,
            'total_amount': self.total_amount,
            'payment_method': self.payment_method
        }
        dbms.execute_query(query, params)
        dbms.execute_query("COMMIT")

class SalesItemInsert(InsertTemplate):
    def __init__(self, item_id, sales_id, medicine_id, quantity, price):
        self.item_id = item_id
        self.sales_id = sales_id
        self.medicine_id = medicine_id
        self.quantity = quantity
        self.price = price
        self.subtotal = self.calculate_subtotal()

    def calculate_subtotal(self):
        return self.quantity * self.price

    def validate(self):
        # Validate that quantity and price are positive
        if self.quantity <= 0:
            messagebox.showerror('Error!', 'Quantity must be greater than 0.')
            return False
        if self.price <= 0:
            messagebox.showerror('Error!', 'Price must be greater than 0.')
            return False
        return True

    def perform_insert(self):
        query = """INSERT INTO SALES_ITEMS (sale_item_id, sale_id, medicine_id, quantity, price_per_unit, subtotal)
                   VALUES (:item_id, :sales_id, :medicine_id, :quantity, :price, :subtotal)"""
        params = {
            'item_id': self.item_id,
            'sales_id': self.sales_id,
            'medicine_id': self.medicine_id,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.subtotal
        }
        dbms.execute_query(query, params)
        dbms.execute_query("COMMIT")


# Creating an object for Database to Python link
dbms = DatabaseManager(username='system', password='Rajini')

#Viewing records in supplier
def checkbysupplier():
     # Create a tkinter window for viewing records in the supplier table
    root18 = Tk()
    root18.geometry('1000x700+250+50')  # Set window size
    root18.title('Checking Medicines in Supplier Page')  # Set window title
    root18.resizable(0, 0)  # Disable window resizing
    root18.config(bg='gray')  # Set background color
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root18, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    # Create top frame for displaying the title
    Topframe = Frame(root18, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)
    Introtext = Label(Topframe, text='Viewing Supplier Table',
    font=('Georgia', 23, 'bold'),bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)
    DetailsFrame = Frame(root18, bg='black', width=1000, height=540)
    DetailsFrame.place(x=0, y=120)

    records = dbms.fetch_query("SELECT * FROM SUPPLIER")

    style = ttk.Style()
    style.configure("Treeview", font=("Georgia", 11))  
    style.configure("Treeview.Heading", font=("Georgia", 12, "bold"))  

    columns = ("Supplier ID", "Supplier Name", "Contact", "Email", "Address")
    c_width=(110, 170, 125, 270, 400)
    tree = ttk.Treeview(DetailsFrame, columns=columns, show="headings", style="Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=c_width[columns.index(col)], anchor="center")  
    tree.place(x=0, y=30, width=980, height=480)

    v_scroll = Scrollbar(DetailsFrame, orient=VERTICAL, command=tree.yview)
    h_scroll = Scrollbar(DetailsFrame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.place(x=980, y=30, height=480)
    h_scroll.place(x=0, y=500, width=980)

    for record in records:
        tree.insert("", "end", values=record)
    
    #Function when back button is pressed
    def backpage():
        root18.destroy()
        check_medicine()

    #Button for going back to previous page
    backbutton = Button(root18,text='Back',command=backpage,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root18.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root18,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root18.mainloop()

#Viewing records in medicine
def checkbymedicine():
    #Create a tkinter page for viewing records in medicine page
    root19 = Tk()
    root19.geometry('1000x700+250+50') #Set window size
    root19.title('Checking Medicines in Medicine Page') #Set window title
    root19.resizable(0,0) # Disable window resizing
    root19.config(bg='gray') #Set background colour
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root19, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Create top frame for displaying title
    Topframe = Frame(root19, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Medicine Table',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    DetailsFrame = Frame(root19,bg='black',width=1000,height=540)
    DetailsFrame.place(x=0,y=120)

    records = dbms.fetch_query("SELECT * FROM MEDICINE")

    style = ttk.Style()
    style.configure("Treeview", font=("Georgia", 11))  
    style.configure("Treeview.Heading", font=("Georgia", 12, "bold"))  

    columns=("Medicine ID", "Medicine Name", "Brand", "Batch Number", "Expiry Date", "Quantity", "Price", "Supplier ID")
    tree = ttk.Treeview(DetailsFrame, columns=columns, show="headings", style="Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=1000 // len(columns), anchor="center")  
    tree.place(x=0, y=30, width=980, height=480)

    v_scroll = Scrollbar(DetailsFrame, orient=VERTICAL, command=tree.yview)
    h_scroll = Scrollbar(DetailsFrame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.place(x=980, y=30, height=480)
    h_scroll.place(x=0, y=490, width=980)
        
    for record in records:
        tree.insert("", "end", values=record)

    #Function when back button is pressed
    def backpage():
        root19.destroy()
        check_medicine()

    #Button for going back to previous page
    backbutton = Button(root19,text='Back',command=backpage,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root19.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root19,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root19.mainloop()

#Viewing records in customer
def checkbycustomer():
    #Create a tkinter page for viewing records in customer page
    root20 = Tk()
    root20.geometry('1000x700+250+50') #Set window size
    root20.title('Checking Medicines in Customer Page') #Set window title
    root20.resizable(0,0) # Disable window resizing
    root20.config(bg='gray') #Set background colour
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root20, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Create top frame for displaying title
    Topframe = Frame(root20, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Customer Table',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    DetailsFrame = Frame(root20,bg='black',width=1000,height=540)
    DetailsFrame.place(x=0,y=120)

    records = dbms.fetch_query("SELECT * FROM CUSTOMER")

    style = ttk.Style()
    style.configure("Treeview", font=("Georgia", 11))  
    style.configure("Treeview.Heading", font=("Georgia", 12, "bold"))  

    columns=("Customer ID", "Customer Name", "Contact", "Email", "Address")
    tree = ttk.Treeview(DetailsFrame, columns=columns, show="headings", style="Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=1000 // len(columns), anchor="center")  
    tree.place(x=0, y=30, width=980, height=480)

    v_scroll = Scrollbar(DetailsFrame, orient=VERTICAL, command=tree.yview)
    h_scroll = Scrollbar(DetailsFrame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.place(x=980, y=30, height=480)
    h_scroll.place(x=0, y=490, width=980)

    for record in records:
        tree.insert("", "end", values=record)

    #Function when back button is pressed
    def backpage():
        root20.destroy()
        check_medicine()

    #Button for going back to previous page
    backbutton = Button(root20,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root20.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root20,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root20.mainloop()

#Viewing records in prescription
def checkbyprescription():
    #Create a tkinter page for viewing records in prescription page
    root21 = Tk()
    root21.geometry('1000x700+250+50') #Set window size
    root21.title('Checking Medicines in Prescription Page') #Set window title
    root21.resizable(0,0) # Disable window resizing
    root21.config(bg='gray') #Set background colour

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root21, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Create top frame for displaying title
    Topframe = Frame(root21, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Prescription Table',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    DetailsFrame = Frame(root21,bg='black',width=1000,height=540)
    DetailsFrame.place(x=0,y=120)

    records = dbms.fetch_query("SELECT * FROM PRESCRIPTION")

    style = ttk.Style()
    style.configure("Treeview", font=("Georgia", 11))  
    style.configure("Treeview.Heading", font=("Georgia", 12, "bold"))  

    columns=("Prescription ID", "Customer ID", "Doctor Name", "Prescription Date", "Dosage", "Frequency", "Duration", "Additional Information")
    tree = ttk.Treeview(DetailsFrame, columns=columns, show="headings", style="Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=1000 // len(columns), anchor="center")  
    tree.place(x=0, y=30, width=980, height=480)

    v_scroll = Scrollbar(DetailsFrame, orient=VERTICAL, command=tree.yview)
    h_scroll = Scrollbar(DetailsFrame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.place(x=980, y=30, height=480)
    h_scroll.place(x=0, y=490, width=980)

    for record in records:
        tree.insert("", "end", values=record)

    #Function when back button is pressed
    def backpage():
        root21.destroy()
        check_medicine()

    #Button for going back to previous page
    backbutton = Button(root21,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root21.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root21,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root21.mainloop()

#Viewing records in Sales
def checkbysales():
    #Create a tkinter page for viewing records in Sales page
    root22 = Tk()
    root22.geometry('1000x700+250+50') #Set window size
    root22.title('Checking Medicines in Sales Page') #Set window title
    root22.resizable(0,0) # Disable window resizing
    root22.config(bg='gray') #Set background colour
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root22, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Create top frame for displaying title
    Topframe = Frame(root22, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Sales Table',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    DetailsFrame = Frame(root22,bg='black',width=1000,height=540)
    DetailsFrame.place(x=0,y=120)

    records = dbms.fetch_query("SELECT * FROM SALES")

    style = ttk.Style()
    style.configure("Treeview", font=("Georgia", 11))  
    style.configure("Treeview.Heading", font=("Georgia", 12, "bold"))  

    columns=("Sale ID", "Customer ID", "Sale Date", "Total Amount", "Payment Method")
    tree = ttk.Treeview(DetailsFrame, columns=columns, show="headings", style="Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=1000 // len(columns), anchor="center")  
    tree.place(x=0, y=30, width=980, height=480)

    v_scroll = Scrollbar(DetailsFrame, orient=VERTICAL, command=tree.yview)
    h_scroll = Scrollbar(DetailsFrame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.place(x=980, y=30, height=480)
    h_scroll.place(x=0, y=490, width=980)
        
    for record in records:
        tree.insert("", "end", values=record)

    #Function when back button is pressed
    def backpage():
        root22.destroy()
        check_medicine()

    #Button for going back to previous page
    backbutton = Button(root22,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root22.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root22,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root22.mainloop()

#Viewing records in Sales Items
def checkbysalesitems():
    #Create a tkinter page for viewing records in Sales Items page
    root23 = Tk()
    root23.geometry('1000x700+250+50') #Set window size
    root23.title('Checking Medicines in Sales Items Page') #Set window title
    root23.resizable(0,0) # Disable window resizing
    root23.config(bg='gray') #Set background colour
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root23, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Create top frame for displaying title
    Topframe = Frame(root23, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Sales Items Table',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    DetailsFrame = Frame(root23,bg='black',width=1000,height=540)
    DetailsFrame.place(x=0,y=120)

    records = dbms.fetch_query("SELECT * FROM SALES_ITEMS")

    style = ttk.Style()
    style.configure("Treeview", font=("Georgia", 11))  
    style.configure("Treeview.Heading", font=("Georgia", 12, "bold"))  

    columns=("Sale Item ID", "Sale ID", "Medicine ID", "Quantity", "Price Per Unit", "Subtotal")
    tree = ttk.Treeview(DetailsFrame, columns=columns, show="headings", style="Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=1000 // len(columns), anchor="center")  
    tree.place(x=0, y=30, width=980, height=480)

    v_scroll = Scrollbar(DetailsFrame, orient=VERTICAL, command=tree.yview)
    h_scroll = Scrollbar(DetailsFrame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.place(x=980, y=30, height=480)
    h_scroll.place(x=0, y=490, width=980)

    for record in records:
        tree.insert("", "end", values=record)

    #Function when back button is pressed
    def backpage():
        root23.destroy()
        check_medicine()

    #Button for going back to previous page
    backbutton = Button(root23,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)
    
    #Function when back home button is pressed
    def backtohome():
        root23.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root23,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root23.mainloop()

def check_customer_history():
    # Create tkinter page for viewing customer's purchase history
    root_history = Tk()
    root_history.geometry('1000x700+250+50')
    root_history.title('Customer Purchase History')
    root_history.resizable(0, 0)
    root_history.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root_history, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    # Create top frame for displaying title
    Topframe = Frame(root_history, bg='black', width=1000, height=150)
    Topframe.place(x=0, y=0)

    # Title text with increased font size
    Introtext = Label(Topframe, text='Customer Data',
                      font=('Georgia', 30, 'bold'), bg='black', fg='white')
    Introtext.place(x=50, y=40, width=900)

    DetailsFrame = Frame(root_history, bg='black', width=1000, height=540)
    DetailsFrame.place(x=0, y=180)

    # Label and entry for Customer ID with realignment
    Label(Topframe, text='Customer ID', font=('Georgia', 14), fg='white', bg='black').place(x=250, y=95)
    customerid_entry = Entry(Topframe, font=('Georgia', 14), width=15)
    customerid_entry.place(x=375, y=95)

    # Define Treeview table for displaying results
    columns = ("Customer ID", "Customer Name", "Prescription ID", "Medicine Name", "Quantity Sold", "Sale Date", "Most Recent Prescription")
    tree = ttk.Treeview(DetailsFrame, columns=columns, show="headings", style="Treeview")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=1000 // len(columns), anchor="center")
    tree.place(x=0, y=30, width=980, height=480)

    v_scroll = Scrollbar(DetailsFrame, orient=VERTICAL, command=tree.yview)
    h_scroll = Scrollbar(DetailsFrame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.place(x=980, y=30, height=480)
    h_scroll.place(x=0, y=490, width=980)

    def resetfield():
        customerid_entry.delete(0, END)
    

    def fetch_and_display_customer_history():
        customer_id = customerid_entry.get()

        # Check if Customer ID is in the correct format (e.g., C001)
        if not re.match(r'^C\d{3}$', customer_id):
            messagebox.showerror('Error!', 'Customer ID format is invalid. It should be in the format Cxxx (e.g., C001).')
            return

        try:
            # Check if Customer ID exists in the CUSTOMER table
            check_query = "SELECT COUNT(*) FROM CUSTOMER WHERE customer_id = :1"
            print(f"Executing query: {check_query} with {customer_id}")
            result = dbms.execute_query(check_query, (customer_id,))
            print(f"Query result: {result}")

            if result and result[0][0] == 0:
                messagebox.showerror('Error!', 'Customer ID does not exist in the database.')
                customerid_entry.delete(0, END)
                return

        except Exception as e:
            print(f"Error during customer check: {e}")
            messagebox.showerror('Error!', f'Error checking Customer ID: {e}')
            customerid_entry.delete(0, END)
            return

        try:
            query = """
                SELECT C.customer_id, C.c_name AS customer_name, 
                       P.prescription_id, M.m_name AS medicine_name, 
                       SI.quantity, S.sale_date,
                       (  SELECT MAX(P1.prescription_id)  -- Subquery to get the most recent prescription
                           FROM PRESCRIPTION P1
                           WHERE P1.customer_id = C.customer_id
                       ) AS most_recent_prescription_id
                FROM CUSTOMER C
                JOIN PRESCRIPTION P ON C.customer_id = P.customer_id
                JOIN SALES S ON C.customer_id = S.customer_id
                JOIN SALES_ITEMS SI ON SI.sale_id = S.sale_id
                JOIN MEDICINE M ON M.medicine_id = SI.medicine_id
                WHERE C.customer_id = :1
            """
            print(f"Executing query: {query} with {customer_id}")
            records = dbms.fetch_query(query, (customer_id,))
            print(f"Fetched records: {records}")

            # Ensure records are not None before accessing
            if not records or len(records) == 0:
                messagebox.showinfo('No Data', 'This customer has no sales or prescription history.')
                resetfield()
                return

            tree.delete(*tree.get_children())  # Clear previous records

            for record in records:
                # Debug: Print each record to verify its format
                print(f"Inserting record: {record}")

                if isinstance(record, tuple):
                    tree.insert("", "end", values=record)  # Insert into Treeview
                else:
                    messagebox.showerror('Data Error', 'Record format is incorrect.')
                    resetfield()
                    return

        except Exception as e:
            print(f"Error during fetch: {e}")
            messagebox.showerror('Query Failed', f'Error fetching customer history: {e}')
            resetfield()


    # Button to fetch history based on entered Customer ID with realignment
    check_button = Button(Topframe, text='Check History', command=fetch_and_display_customer_history,
                          font=('Georgia', 14), bg='light blue', fg='black')
    check_button.place(x=630, y=90)

    # Function for Back button
    def backpage():
        root_history.destroy()
        check_medicine()  # Adjust if needed

    # Back button
    backbutton = Button(root_history, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function for Back to Home button
    def backtohome():
        root_history.destroy()
        introscreen()  # Adjust if needed

    # Back to Home button
    home_page_button = Button(root_history, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root_history.mainloop()


#Checking the medicines available
def check_medicine():
    #Create a tkinter page for the check medicine page
    root2 = Tk()
    root2.geometry('1000x700+250+50') #Set window size
    root2.title('Check Medicine Page') #Set window title
    root2.resizable(0,0) # Disable window resizing
    root2.config(bg='gray') #Set background colour
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root2, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Function when back home button is pressed
    def backtohome():
        root2.destroy()
        introscreen()
    
    #Create top frame for displaying title
    Topframe = Frame(root2, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Check table for',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    ButtonsFrame = Frame(root2,bg='black',width=520,height=550)
    ButtonsFrame.place(x=240,y=120)

    #Function when buttons are pressed for checking into specific tables
    def check_supplier():
        root2.destroy()
        checkbysupplier()
    
    def check_medicine():
        root2.destroy()
        checkbymedicine()
    
    def check_customer():
        root2.destroy()
        checkbycustomer()
    
    def check_prescription():
        root2.destroy()
        checkbyprescription()

    def check_sales():
        root2.destroy()
        checkbysales()
    
    def check_sales_items():
        root2.destroy()
        checkbysalesitems()
    
    def check_custom_data():
        root2.destroy()
        check_customer_history()

    #Button for inserting medicine by supplier
    supplier_button = Button(ButtonsFrame,text='Supplier',command=check_supplier,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=40,width=220)

    #Button for inserting medicine by medicine
    medicine_button = Button(ButtonsFrame,text='Medicine',command=check_medicine,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    medicine_button.place(x=150,y=115,width=220)

    #Button for inserting medicine by customer
    customer_button = Button(ButtonsFrame,text='Customer',command=check_customer,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    customer_button.place(x=150,y=190,width=220)

    #Button for inserting medicine by prescription
    prescription_button = Button(ButtonsFrame,text='Prescription',command=check_prescription,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    prescription_button.place(x=150,y=265,width=220)

    #Button for inserting medicine by sales
    sales_button = Button(ButtonsFrame,text='Sales',command=check_sales,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    sales_button.place(x=150,y=340,width=220)

    #Button for inserting medicine by sales
    salesitems_button = Button(ButtonsFrame,text='Sales Items',command=check_sales_items,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    salesitems_button.place(x=150,y=415,width=220)

    customdata_button = Button(ButtonsFrame,text='Customer Data',command=check_custom_data,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    customdata_button.place(x=150,y=490,width=220)

    #Button for going back to home page
    home_page_button = Button(root2,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root2.mainloop()

#Checking if Supplier ID entered is a valid Supplier ID or not
def check_supplier_id(supplier_id):
    pattern = r"^S\d{3}$"
    if not re.match(pattern, supplier_id):
        messagebox.showerror('Error!', 'Invalid Supplier ID format. It should start with "S" followed by three digits.')
        return False
        
    query = "SELECT supplier_id FROM SUPPLIER WHERE supplier_id = :1"
    params = (supplier_id,)
    result = dbms.fetch_query(query, params)
        
    if not result:
        messagebox.showerror('Error!', f'Supplier ID {supplier_id} does not exist in the SUPPLIER table.')
        return False
        
    return True

#Checking if Medicine ID entered is a valid Medicine ID or not
def check_medicine_id(medicine_id):
    pattern = r"^M\d{3}$"
        
    if not re.match(pattern, medicine_id):
        messagebox.showerror('Error!', 'Invalid Medicine ID format. It should start with "M" followed by three digits.')
        return False
        
    query = "SELECT medicine_id FROM MEDICINE WHERE medicine_id = :1"
    params = (medicine_id,)
    result = dbms.fetch_query(query, params)
        
    if not result:
        messagebox.showerror('Error!', f'Medicine ID {medicine_id} does not exist in the MEDICINE table.')
        return False
        
    return True

#Checking if Customer ID entered is a valid Customer ID or not
def check_customer_id(customer_id):
    pattern = r"^C\d{3}$"
        
    if not re.match(pattern, customer_id):
        messagebox.showerror('Error!', 'Invalid Customer ID format. It should start with "C" followed by three digits.')
        return False
        
    query = "SELECT customer_id FROM CUSTOMER WHERE customer_id = :1"
    params = (customer_id,)
    result = dbms.fetch_query(query, params)
        
    if not result:
        messagebox.showerror('Error!', f'Customer ID {customer_id} does not exist in the CUSTOMER table.')
        return False
        
    return True

#Checking if Prescription ID entered is a valid Prescription ID or not
def check_prescription_id(prescription_id):
    pattern = r"^P\d{3}$"

    if not re.match(pattern, prescription_id):
        messagebox.showerror('Error!', 'Invalid Prescription ID format. It should start with "P" followed by three digits.')
        return False
        
    query = "SELECT prescription_id FROM PRESCRIPTION WHERE prescription_id = :1"
    params = (prescription_id,)
    result = dbms.fetch_query(query, params)
        
    if not result:
        messagebox.showerror('Error!', f'Prescription ID {prescription_id} does not exist in the PRESCRIPTION table.')
        return False
        
    return True

#Checking if Sale ID entered is a valid Sale ID or not
def check_sale_id(sale_id):
    pattern = r"^S\d{3}$"
        
    if not re.match(pattern, sale_id):
        messagebox.showerror('Error!', 'Invalid Sale ID format. It should start with "S" followed by three digits.')
        return False
        
    query = "SELECT sale_id FROM SALES WHERE sale_id = :1"
    params = (sale_id,)
    result = dbms.fetch_query(query, params)
        
    if not result:
        messagebox.showerror('Error!', f'Sale ID {sale_id} does not exist in the SALES table.')
        return False
        
    return True

#Checking if Sale ID entered is a valid Sale ID or not
def check_sale_item_id(sale_item_id):
    pattern = r"^SI\d{3}$"
        
    if not re.match(pattern, sale_item_id):
        messagebox.showerror('Error!', 'Invalid Sale Item ID format. It should start with "SI" followed by three digits.')
        return False
        
    query = "SELECT sale_item_id FROM SALES_ITEMS WHERE sale_item_id = :1"
    params = (sale_item_id,)
    result = dbms.fetch_query(query, params)
        
    if not result:
        messagebox.showerror('Error!', f'Sale Item ID {sale_item_id} does not exist in the SALES_ITEMS table.')
        return False
        
    return True

#Inserting in supplier
def insertbysupplier():
    #Create a tkinter page for the insert in supplier page
    root6 = Tk()
    root6.geometry('1000x700+250+50') #Set window size
    root6.title('Insert in Supplier Page') #Set window title
    root6.resizable(0,0) # Disable window resizing
    root6.config(bg='gray') #Set background colour
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root6, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Create top frame for displaying title
    Topframe = Frame(root6, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Supplier Table',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    DetailsFrame = Frame(root6,bg='black',width=520,height=520)
    DetailsFrame.place(x=240,y=150)

    def resetfield():
        sidentry.delete(0, END)
        snameentry.delete(0, END)
        numberentry.delete(0, END)
        emailentry.delete(0, END)
        addressentry.delete(0, END)

    def insertdetails():
        global se, sne, ne, ee, ae
        se = sidentry.get()  # Supplier ID
        sne = snameentry.get()  # Supplier Name
        ne = numberentry.get()  # Contact Number
        ee = emailentry.get()  # Email
        ae = addressentry.get()  # Address

        def email_check(email):
            pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            return bool(re.match(pattern, email))

        def pattern():
            pattern_regex = r"^S\d{3}$"
            if not re.match(pattern_regex, se):
                messagebox.showerror('Error!', 'Invalid Supplier ID format. It should start with "S" followed by three digits.')
                return False
            return True 

        if se == '' or sne == '' or ne == '' or ee == '' or ae == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
        elif not pattern():
            resetfield()
        elif len(ne) != 10 or str(ne)[0] == '0':
            messagebox.showerror('Error!', 'Enter a valid mobile number.')
            resetfield()
        elif email_check(ee) != True:
            messagebox.showerror('Error', 'Enter a valid email ID')
            resetfield()
        else:
            # Check if Supplier ID already exists
            query = "SELECT supplier_id FROM SUPPLIER WHERE supplier_id = :1"
            params = (se,)
            c = dbms.fetch_query(query, params)
            if c:
                # Display an error message if the supplier ID already exists
                messagebox.showerror('Insert Error!', f'Supplier ID {se} already exists!')
                resetfield()
            else:
                # Create SupplierInsert object using collected data
                supplier_insert = SupplierInsert(se, sne, ne, ee, ae)

                # Wrap SupplierInsert in the Command and execute
                supplier_command = InsertCommand(supplier_insert)
                invoker = CommandInvoker()
                invoker.add_command(supplier_command)
                invoker.execute_commands()  # Execute the insert operation
                messagebox.showinfo('Success!', 'Record inserted successfully into Supplier Table!')
                resetfield()



    # Labels and entry fields for inserting data by supplier
    sidtext = Label(DetailsFrame, text='Supplier ID', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    sidtext.place(x=20, y=50)
    snametext = Label(DetailsFrame, text='Supplier Name', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    snametext.place(x=20, y=130)
    numbertext = Label(DetailsFrame, text='Contact Number', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    numbertext.place(x=20, y=210)
    emailtext = Label(DetailsFrame, text='Email', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    emailtext.place(x=20, y=290)
    addresstext = Label(DetailsFrame, text='Address', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    addresstext.place(x=20, y=370)

    sidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    sidentry.place(x=20, y=80, width=350)
    snameentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    snameentry.place(x=20, y=160, width=350)
    numberentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    numberentry.place(x=20, y=240, width=350)
    emailentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    emailentry.place(x=20, y=320, width=350)
    addressentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    addressentry.place(x=20, y=400, width=350)

    EnterButton = Button(DetailsFrame,text='Enter',command=insertdetails,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    EnterButton.place(x=150,y=440,width=220)

    #Function when back button is pressed
    def backpage():
        root6.destroy()
        insert_medicine()

    #Button for going back to previous page
    backbutton = Button(root6,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root6.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root6,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root6.mainloop()

#Inserting in medicine
def insertbymedicine():
    # Create a tkinter page for the insert in medicine page
    root7 = Tk()
    root7.geometry('1000x700+250+50')
    root7.title('Insert in Medicine Page')
    root7.resizable(0, 0)
    root7.config(bg='gray')

    # Background image setup (make sure the path is correct)
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root7, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    # Create top frame for displaying title
    Topframe = Frame(root7, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Medicine Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root7, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    def resetfield():
        midentry.delete(0, END)
        mnameentry.delete(0, END)
        brandentry.delete(0, END)
        batchnoentry.delete(0, END)
        expdateentry.delete(0, END)
        qtyentry.delete(0, END)
        priceentry.delete(0, END)
        sidentry.delete(0, END)

    def insertdetails():
        # Get the input data from the entry fields
        me = midentry.get()  # Medicine ID
        mne = mnameentry.get()  # Medicine Name
        bre = brandentry.get()  # Brand
        be = batchnoentry.get()  # Batch Number
        ee = expdateentry.get()  # Expiry Date
        qe = qtyentry.get()  # Quantity
        pe = priceentry.get()  # Price
        se = sidentry.get()  # Supplier ID

        # Create an instance of the MedicineInsert class
        medicine = MedicineInsert(me, mne, bre, be, ee, qe, pe, se)

        # Validate the inputs using the validate method
        if not medicine.validate():
            return  # Validation failed, return without proceeding

        # If validation passed, proceed to insert into the database
        try:
            # Check if the expiry date is in the correct format (DD-MON-YY)
            exp_date = datetime.strptime(ee, "%d-%b-%y")

            # Validate if the date is within 30 days from today
            today_date = datetime.today()
            thirty_days_later = today_date + timedelta(days=30)

            # Check if the expiry date is within 30 days from today
            if exp_date <= thirty_days_later:
                messagebox.showerror('Expiry Date Error!', 'Expiry date is within 30 days from today. Please check!')
                resetfield()
                return

        except ValueError:
            # If the date format is incorrect or the date does not exist
            messagebox.showerror('Error!', 'Invalid date. Please enter a valid date in DD-MON-YY format.')
            resetfield()
            return

        # Check if the medicine ID already exists
        query = "SELECT medicine_id FROM MEDICINE WHERE medicine_id = :1"
        params = (me,)
        c = dbms.fetch_query(query, params)

        if c:
            messagebox.showerror('Insert Error!', f'Medicine ID {me} already exists!')
            resetfield()
        else:
            # Wrap MedicineInsert in the Command and execute
            medicine_command = InsertCommand(medicine)
            invoker = CommandInvoker()
            invoker.add_command(medicine_command)
            invoker.execute_commands()  # Execute the insert operation

            messagebox.showinfo('Success!', 'Record inserted successfully into Medicine Table!')
            resetfield()

    # Labels and entry fields for inserting data by medicine
    midtext = Label(DetailsFrame, text='Medicine ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    midtext.place(x=20, y=50)
    mnametext = Label(DetailsFrame, text='Medicine Name', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    mnametext.place(x=20, y=130)
    brandtext = Label(DetailsFrame, text='Brand', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    brandtext.place(x=20, y=210)
    batchnotext = Label(DetailsFrame, text='Batch Number', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    batchnotext.place(x=20, y=290)
    expdatetext = Label(DetailsFrame, text='Expiry Date', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    expdatetext.place(x=450, y=50)
    qtytext = Label(DetailsFrame, text='Quantity', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    qtytext.place(x=450, y=130)
    pricetext = Label(DetailsFrame, text='Price', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    pricetext.place(x=450, y=210)
    sidtext = Label(DetailsFrame, text='Supplier ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    sidtext.place(x=450, y=290)

    midentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    midentry.place(x=20, y=80, width=350)
    mnameentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    mnameentry.place(x=20, y=160, width=350)
    brandentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    brandentry.place(x=20, y=240, width=350)
    batchnoentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    batchnoentry.place(x=20, y=320, width=350)
    expdateentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    expdateentry.place(x=450, y=80, width=350)
    qtyentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    qtyentry.place(x=450, y=160, width=350)
    priceentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    priceentry.place(x=450, y=240, width=350)
    sidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    sidentry.place(x=450, y=320, width=350)

    EnterButton = Button(DetailsFrame, text='Enter', command=insertdetails, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    EnterButton.place(x=150, y=440, width=220)

    # Function when back button is pressed
    def backpage():
        root7.destroy()
        insert_medicine()

    # Button for going back to previous page
    backbutton = Button(root7, text='Back', command=backpage, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root7.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root7, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root7.mainloop()


def insertbycustomer():
    # Create a tkinter page for the insert in customer page
    root8 = Tk()
    root8.geometry('1000x700+250+50')
    root8.title('Insert in Customer Page')
    root8.resizable(0, 0)
    root8.config(bg='gray')

    # Background image setup (make sure the path is correct)
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root8, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    # Create top frame for displaying title
    Topframe = Frame(root8, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Customer Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root8, bg='black', width=520, height=520)
    DetailsFrame.place(x=240, y=150)

    def resetfield():
        cidentry.delete(0, END)
        cnameentry.delete(0, END)
        numberentry.delete(0, END)
        emailentry.delete(0, END)
        addressentry.delete(0, END)

    def insertdetails():
        ce = cidentry.get()  # Customer ID
        cne = cnameentry.get()  # Customer Name
        ne = numberentry.get()  # Contact Number
        ee = emailentry.get()  # Email
        ae = addressentry.get()  # Address

        # Function to validate email
        def email_check(email):
            pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(pattern, email):
                messagebox.showerror('Error', 'Enter a valid Gmail ID')
                return False
            return True

        # Function to validate Customer ID format
        def pattern():
            pattern = r"^C\d{3}$"
            if not re.match(pattern, ce):
                messagebox.showerror('Error!', 'Invalid Customer ID format. It should start with "C" followed by three digits.')
                return False
            return True

        # Check if all fields are filled
        if ce == '' or cne == '' or ne == '' or ee == '' or ae == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
            return
        elif not pattern():
            resetfield()
            return
        elif len(ne) != 10 or not ne.isdigit() or ne[0] == '0':
            messagebox.showerror('Error!', 'Enter a valid 10-digit mobile number that doesn\'t start with 0.')
            resetfield()
            return
        elif not email_check(ee):
            resetfield()
            return
        else:
            # Check if the customer ID already exists
            query = "SELECT customer_id FROM CUSTOMER WHERE customer_id = :1"
            params = (ce,)
            c = dbms.fetch_query(query, params)

            if c:
                messagebox.showerror('Insert Error!', f'Customer ID {ce} already exists!')
                resetfield()
                return
            else:
                # Use CustomerInsert class to validate and insert
                customer_insert = CustomerInsert(ce, cne, ne, ee, ae)

                if customer_insert.validate():
                    customer_insert.perform_insert()
                    messagebox.showinfo('Success!', 'Record inserted successfully into Customer Table!')
                    resetfield()

    # Labels and entry fields for inserting data by customer
    cidtext = Label(DetailsFrame, text='Customer ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    cidtext.place(x=20, y=50)
    cnametext = Label(DetailsFrame, text='Customer Name', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    cnametext.place(x=20, y=130)
    numbertext = Label(DetailsFrame, text='Contact Number', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    numbertext.place(x=20, y=210)
    emailtext = Label(DetailsFrame, text='Email', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    emailtext.place(x=20, y=290)
    addresstext = Label(DetailsFrame, text='Address', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    addresstext.place(x=20, y=370)

    # Input fields
    cidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    cidentry.place(x=20, y=80, width=350)
    cnameentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    cnameentry.place(x=20, y=160, width=350)
    numberentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    numberentry.place(x=20, y=240, width=350)
    emailentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    emailentry.place(x=20, y=320, width=350)
    addressentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    addressentry.place(x=20, y=400, width=350)

    EnterButton = Button(DetailsFrame, text='Enter', command=insertdetails, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    EnterButton.place(x=150, y=440, width=220)

    # Back button
    def backpage():
        root8.destroy()
        insert_medicine()

    backbutton = Button(root8, text='Back', command=backpage, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Home button
    def backtohome():
        root8.destroy()
        introscreen()

    home_page_button = Button(root8, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root8.mainloop()

def insertbyprescription():
    # Create a tkinter page for the insert in prescription page
    root9 = Tk()
    root9.geometry('1000x700+250+50')
    root9.title('Insert in Prescription Page')
    root9.resizable(0, 0)
    root9.config(bg='gray')

    # Background image setup (make sure the path is correct)
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root9, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    # Create top frame for displaying title
    Topframe = Frame(root9, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Prescription Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root9, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    def resetfield():
        pidentry.delete(0, END)
        cidentry.delete(0, END)
        docnameentry.delete(0, END)
        dateentry.delete(0, END)
        dosageentry.delete(0, END)
        freqentry.delete(0, END)
        durationentry.delete(0, END)
        addinentry.delete(0, END)

# Assuming necessary imports have been made for Command pattern and the required classes

    def insertdetails():
        # Get input values
        pe = pidentry.get()  # Prescription ID
        ce = cidentry.get()  # Customer ID
        dne = docnameentry.get()  # Doctor Name
        pde = dateentry.get()  # Prescription Date
        doe = dosageentry.get()  # Dosage
        fe = freqentry.get()  # Frequency
        due = durationentry.get()  # Duration
        ae = addinentry.get()  # Additional Instructions

        # Check if all fields are filled
        if pe == '' or ce == '' or dne == '' or pde == '' or doe == '' or fe == '' or due == '' or ae == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
            return

        # Validate Prescription ID format
        if not re.match(r"^P\d{3}$", pe):
            messagebox.showerror('Error!', 'Invalid Prescription ID format. It should start with "P" followed by three digits.')
            resetfield()
            return

        # Validate Prescription Date format
        try:
            presc_date = datetime.strptime(pde, "%d-%b-%y")
        except ValueError:
            messagebox.showerror('Error!', 'Invalid date format. Please enter the prescription date in DD-MON-YY format.')
            resetfield()
            return

        # Validate Customer ID
        if not check_customer_id(ce):  # Assuming check_customer_id is a defined function
            resetfield()
            return

        # Create an instance of the PrescriptionInsert class
        prescription = PrescriptionInsert(pe, ce, dne, pde, doe, fe, due, ae)

        # Validate the data before performing the insert
        if prescription.validate():
            # Create an InsertCommand object with the prescription insert action
            insert_command = InsertCommand(prescription)
            # Create an invoker object and add the insert command
            invoker = CommandInvoker()
            invoker.add_command(insert_command)

            # Execute the command
            invoker.execute_commands()

            messagebox.showinfo('Success!', 'Record inserted successfully into Prescription Table!')
            resetfield()


    # Labels and entry fields for inserting data by prescription
    pidtext = Label(DetailsFrame, text='Prescription ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    pidtext.place(x=20, y=50)
    cidtext = Label(DetailsFrame, text='Customer ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    cidtext.place(x=20, y=130)
    docnametext = Label(DetailsFrame, text='Doctor Name', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    docnametext.place(x=20, y=210)
    datetext = Label(DetailsFrame, text='Prescription Date', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    datetext.place(x=20, y=290)
    dosagetext = Label(DetailsFrame, text='Dosage', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    dosagetext.place(x=450, y=50)
    freqtext = Label(DetailsFrame, text='Frequency', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    freqtext.place(x=450, y=130)
    durationtext = Label(DetailsFrame, text='Duration', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    durationtext.place(x=450, y=210)
    addintext = Label(DetailsFrame, text='Additional Instructions', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    addintext.place(x=450, y=290)

    # Input fields
    pidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    pidentry.place(x=20, y=80, width=350)
    cidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    cidentry.place(x=20, y=160, width=350)
    docnameentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    docnameentry.place(x=20, y=240, width=350)
    dateentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    dateentry.place(x=20, y=320, width=350)
    dosageentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    dosageentry.place(x=450, y=80, width=350)
    freqentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    freqentry.place(x=450, y=160, width=350)
    durationentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    durationentry.place(x=450, y=240, width=350)
    addinentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    addinentry.place(x=450, y=320, width=350)
    EnterButton = Button(DetailsFrame, text='Enter', command=insertdetails, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    EnterButton.place(x=150, y=440, width=220)

    # Function when back button is pressed
    def backpage():
        root9.destroy()
        insert_medicine()

    # Button for going back to previous page
    backbutton = Button(root9, text='Back', command=backpage, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root9.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root9, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root9.mainloop()

#Inserting in sales
def insertbysales():
    # Create a tkinter page for the insert in sales page
    root10 = Tk()
    root10.geometry('1000x700+250+50')
    root10.title('Insert in Sales Page')
    root10.resizable(0, 0)
    root10.config(bg='gray')

    # Background image setup (make sure the path is correct)
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root10, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    # Create top frame for displaying title
    Topframe = Frame(root10, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Sales Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root10, bg='black', width=520, height=520)
    DetailsFrame.place(x=240, y=150)

    def resetfield():
        sidentry.delete(0, END)
        cidentry.delete(0, END)
        sdateentry.delete(0, END)
        totamtentry.delete(0, END)
        payentry.delete(0, END)

    def insertdetails():
        global se, ce, sde, te, pe
        se = sidentry.get()  # Sale ID
        ce = cidentry.get()  # Customer ID
        sde = sdateentry.get()  # Sale Date
        te = totamtentry.get()  # Total Amount
        pe = payentry.get()  # Payment Method

        # Function to validate Sale ID format
        def pattern():
            pattern_regex = r"^S\d{3}$"
            if not re.match(pattern_regex, se):
                messagebox.showerror('Error!', 'Invalid Sale ID format. It should start with "S" followed by three digits.')
                return False
            return True

        # Check if all fields are filled
        if se == '' or ce == '' or sde == '' or te == '' or pe == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
            return
        elif not pattern():  # Validate Sale ID format
            resetfield()
            return
        elif float(te) < 0:
            messagebox.showerror('Error!', 'Enter a valid total amount.')
            resetfield()
            return
        elif not check_customer_id(ce):  # Assuming check_customer_id is a defined function
            resetfield()
            return
        else:
            try:
                # Check if the sale date is in the correct format (DD-MON-YY)
                sale_date = datetime.strptime(sde, "%d-%b-%y")
            except ValueError:
                # Display an error message if the date format is invalid or if the date does not exist
                messagebox.showerror('Error!', 'Invalid date format. Please enter the sale date in DD-MON-YY format.')
                resetfield()
                return

            # Check if the sale ID already exists
            query = "SELECT sale_id FROM SALES WHERE sale_id = :1"
            params = (se,)
            c = dbms.fetch_query(query, params)

            if c:
                messagebox.showerror('Insert Error!', f'Sale ID {se} already exists!')
                resetfield()
                return
            else:
                # Create SalesInsert object
                sales_insert = SalesInsert(se, ce, sale_date, te, pe)

                # Validate the data
                if sales_insert.validate():
                    # Create an InsertCommand for the sales insert
                    insert_command = InsertCommand(sales_insert)

                    # Create the CommandInvoker and add the insert command
                    invoker = CommandInvoker()
                    invoker.add_command(insert_command)

                    # Execute the command via the invoker
                    invoker.execute_commands()

                    # Inform the user that the insertion was successful
                    messagebox.showinfo('Success!', 'Record inserted successfully into Sales Table!')
                    resetfield()
                    return

    # Labels and entry fields for inserting data by sales
    sidtext = Label(DetailsFrame, text='Sale ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    sidtext.place(x=20, y=50)
    cidtext = Label(DetailsFrame, text='Customer ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    cidtext.place(x=20, y=130)
    sdatetext = Label(DetailsFrame, text='Sale Date', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    sdatetext.place(x=20, y=210)
    totamttext = Label(DetailsFrame, text='Total Amount', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    totamttext.place(x=20, y=290)
    paytext = Label(DetailsFrame, text='Payment Method', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    paytext.place(x=20, y=370)

    # Input fields
    sidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    sidentry.place(x=20, y=80, width=350)
    cidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    cidentry.place(x=20, y=160, width=350)
    sdateentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    sdateentry.place(x=20, y=240, width=350)
    totamtentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    totamtentry.place(x=20, y=320, width=350)
    payentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    payentry.place(x=20, y=400, width=350)

    EnterButton = Button(DetailsFrame, text='Enter', command=insertdetails, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    EnterButton.place(x=150, y=440, width=220)

    # Function when back button is pressed
    def backpage():
        root10.destroy()
        insert_medicine()

    # Button for going back to previous page
    backbutton = Button(root10, text='Back', command=backpage, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root10.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root10, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root10.mainloop()

#Inserting in sales items
def insertbysalesitems():
    # Create a tkinter page for the insert in sales items page
    root11 = Tk()
    root11.geometry('1000x700+250+50')
    root11.title('Insert in Sales Items Page')
    root11.resizable(0, 0)
    root11.config(bg='gray')

    # Background image setup (make sure the path is correct)
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root11, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    # Create top frame for displaying title
    Topframe = Frame(root11, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Sales Items Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root11, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    def resetfield():
        saidentry.delete(0, END)
        sidentry.delete(0, END)
        midentry.delete(0, END)
        qtyentry.delete(0, END)
        priceentry.delete(0, END)

    def insertdetails():
        sie = saidentry.get()  # Sale Item ID
        se = sidentry.get()    # Sale ID
        me = midentry.get()    # Medicine ID
        qe = qtyentry.get()    # Quantity
        pe = priceentry.get()  # Price per unit

        # Check if all fields are filled
        if sie == '' or se == '' or me == '' or qe == '' or pe == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
            return

        # Validate Sale Item ID format
        def pattern():
            pattern_regex = r"^SI\d{3}$"
            if not re.match(pattern_regex, sie):
                messagebox.showerror('Error!', 'Invalid Sale Item ID format. It should start with "SI" followed by three digits.')
                return False
            return True

        if not pattern():
            resetfield()
            return

        # Check if Quantity and Price per Unit are valid positive values
        try:
            qe = int(qe)
            pe = float(pe)
            if qe <= 0 or pe <= 0:
                messagebox.showerror('Error!', 'Quantity and Price must be greater than 0.')
                resetfield()
                return
        except ValueError:
            messagebox.showerror('Error!', 'Quantity must be an integer and Price per unit a number.')
            resetfield()
            return

        # Determine discount strategy based on selection
        discount_strategy = discount_choice.get()
        if discount_strategy == "NoDiscount":
            discount = NoDiscount()
        elif discount_strategy == "SeasonalDiscount":
            discount = SeasonalDiscount()
        elif discount_strategy == "FirstTimeBuyerDiscount":
            discount = FirstTimeBuyerDiscount()

        # Create SalesItemInsert instance and apply discount
        sales_item = SalesItemInsert(sie, se, me, qe, pe)
        sales_item.subtotal = discount.apply_discount(sales_item.subtotal)

        # Validate and perform insert if valid
        if not sales_item.validate():
            resetfield()
            return

        # Check if Sale ID and Medicine ID exist in their respective tables
        if not check_sale_id(se):  # Assuming check_sale_id is a defined function
            resetfield()
            return
        if not check_medicine_id(me):  # Assuming check_medicine_id is a defined function
            resetfield()
            return

        # Check if the sale_item_id already exists
        query = "SELECT sale_item_id FROM SALES_ITEMS WHERE sale_item_id = :1"
        params = (sie,)
        c = dbms.fetch_query(query, params)

        if c:
            messagebox.showerror('Insert Error!', f'Sale Item ID {sie} already exists!')
            resetfield()
            return
        else:
            # Create InsertSalesItemCommand
            insert_command = InsertCommand(sales_item)

            # Create CommandInvoker
            invoker = CommandInvoker()
            invoker.add_command(insert_command)

            # Execute the command via the invoker
            try:
                invoker.execute_commands()
                messagebox.showinfo('Success!', 'Record inserted successfully into Sales Items Table!')
            except cx_Oracle.DatabaseError as e:
                error_message = str(e)
                if "ORA-20001" in error_message:
                    messagebox.showerror("Trigger Error", "Trigger prevented the operation: Insufficient stock in MEDICINE table.")
                else:
                    messagebox.showerror("Database Error", error_message)
            finally:
                resetfield()
            return


    # Labels and entry fields for inserting data by sales items
    saidtext = Label(DetailsFrame, text='Sale Item ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    saidtext.place(x=20, y=50)
    sidtext = Label(DetailsFrame, text='Sale ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    sidtext.place(x=20, y=130)
    midtext = Label(DetailsFrame, text='Medicine ID', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    midtext.place(x=20, y=210)
    qtytext = Label(DetailsFrame, text='Quantity', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    qtytext.place(x=450, y=50)
    pricetext = Label(DetailsFrame, text='Price Per Unit', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white', activebackground='black')
    pricetext.place(x=450, y=130)
    Label(DetailsFrame, text='Discount Type', font=('Georgia', 18, 'bold', 'italic'), bg='black', fg='white').place(x=450, y=210)

    # Input fields
    saidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    saidentry.place(x=20, y=80, width=350)
    sidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    sidentry.place(x=20, y=160, width=350)
    midentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    midentry.place(x=20, y=240, width=350)
    qtyentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    qtyentry.place(x=450, y=80, width=350)
    priceentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='black')
    priceentry.place(x=450, y=160, width=350)

    discount_choice = StringVar(DetailsFrame)
    discount_choice.set("NoDiscount")  # Default value
    discount_menu = ttk.Combobox(DetailsFrame, textvariable=discount_choice, font=("Georgia", 16, 'bold'), values=["NoDiscount", "SeasonalDiscount", "FirstTimeBuyerDiscount"])
    discount_menu.place(x=450, y=240, width=350)

    EnterButton = Button(DetailsFrame, text='Enter', command=insertdetails, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    EnterButton.place(x=150, y=440, width=220)

    # Function when back button is pressed
    def backpage():
        root11.destroy()
        insert_medicine()

    # Button for going back to previous page
    backbutton = Button(root11, text='Back', command=backpage, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root11.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root11, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'), cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=750, y=25, width=220)

    root11.mainloop()

#Inserting a medicine
def insert_medicine():
    #Create a tkinter page for the insert medicine page
    root3 = Tk()
    root3.geometry('1000x700+250+50') #Set window size
    root3.title('Insert Medicine Page') #Set window title
    root3.resizable(0,0) # Disable window resizing
    root3.config(bg='gray') #Set background colour
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root3, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Function when back home button is pressed
    def backtohome():
        root3.destroy()
        introscreen()
    
    #Create top frame for displaying title
    Topframe = Frame(root3, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert by',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    ButtonsFrame = Frame(root3,bg='black',width=520,height=500)
    ButtonsFrame.place(x=240,y=150)

    #Function when buttons are pressed for inserting into specific tables
    def insert_supplier():
        root3.destroy()
        insertbysupplier()
    
    def insert_medicine():
        root3.destroy()
        insertbymedicine()
    
    def insert_customer():
        root3.destroy()
        insertbycustomer()
    
    def insert_prescription():
        root3.destroy()
        insertbyprescription()

    def insert_sales():
        root3.destroy()
        insertbysales()
    
    def insert_sales_items():
        root3.destroy()
        insertbysalesitems()

    #Button for inserting medicine by supplier
    supplier_button = Button(ButtonsFrame,text='Supplier',command=insert_supplier,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=40,width=220)

    #Button for inserting medicine by medicine
    medicine_button = Button(ButtonsFrame,text='Medicine',command=insert_medicine,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    medicine_button.place(x=150,y=115,width=220)

    #Button for inserting medicine by customer
    customer_button = Button(ButtonsFrame,text='Customer',command=insert_customer,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    customer_button.place(x=150,y=190,width=220)

    #Button for inserting medicine by prescription
    prescription_button = Button(ButtonsFrame,text='Prescription',command=insert_prescription,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    prescription_button.place(x=150,y=265,width=220)

    #Button for inserting medicine by sales
    sales_button = Button(ButtonsFrame,text='Sales',command=insert_sales,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    sales_button.place(x=150,y=340,width=220)

    #Button for inserting medicine by sales
    salesitems_button = Button(ButtonsFrame,text='Sales Items',command=insert_sales_items,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    salesitems_button.place(x=150,y=415,width=220)

    #Button for going back to home page
    home_page_button = Button(root3,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root3.mainloop()

#updating in supplier
def updatebysupplier():
    root12 = Tk()
    root12.geometry('1000x700+250+50')
    root12.title('Update Supplier Page')
    root12.resizable(0, 0)
    root12.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root12, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def resetfield():
        sidentry.delete(0, END)
        snameentry.delete(0, END)
        numberentry.delete(0, END)
        emailentry.delete(0, END)
        addressentry.delete(0, END)

    def update_supplier_details():
        se = sidentry.get()  # Supplier ID (primary key for identification)
        sne = snameentry.get()  # Supplier Name
        ne = numberentry.get()  # Contact Number
        ee = emailentry.get()  # Email
        ae = addressentry.get()  # Address

        # Validate email format
        def email_check(email):
            pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            return bool(re.match(pattern, email))

        # Validate Supplier ID format
        def pattern():
            pattern_regex = r"^S\d{3}$"
            if not re.match(pattern_regex, se):
                messagebox.showerror('Error!', 'Invalid Supplier ID format. It should start with "S" followed by three digits.')
                return False
            return True

        # Check if all fields are filled
        if se == '' or sne == '' or ne == '' or ee == '' or ae == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
            return
        elif not pattern():  # Check if Supplier ID format is correct
            resetfield()
            return
        elif len(ne) != 10 or not ne.isdigit() or ne[0] == '0':  # Validate Contact Number format
            messagebox.showerror('Error!', 'Enter a valid 10-digit mobile number that does not start with 0.')
            resetfield()
            return
        elif not email_check(ee):  # Check if email format is correct
            messagebox.showerror('Error', 'Enter a valid Gmail ID (e.g., example@gmail.com).')
            resetfield()
            return
        else:
            # Check if Supplier ID exists in the table before updating
            try:
                query_check = "SELECT supplier_id FROM SUPPLIER WHERE supplier_id = :1"
                params_check = (se,)
                result = dbms.fetch_query(query_check, params_check)
                
                if not result:
                    messagebox.showerror('Error!', f'Supplier ID {se} does not exist in the SUPPLIER table.')
                    resetfield()
                    return

                # Update Supplier details if all validations pass
                query = """
                    UPDATE SUPPLIER
                    SET s_name=:1, contact_number=:2, email=:3, address=:4
                    WHERE supplier_id=:5
                """
                params = (sne, ne, ee, ae, se)
                dbms.execute_query(query, params)
                dbms.execute_query("COMMIT")
                messagebox.showinfo('Success!', f'Supplier ID {se} updated successfully.')
                resetfield()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                resetfield()
            
    # Create top frame for displaying title
    Topframe = Frame(root12, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Update Supplier Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root12, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    # Create entry fields and labels for the supplier update form
    Label(DetailsFrame, text='Supplier ID', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=50)
    sidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    sidentry.place(x=375, y=50)

    Label(DetailsFrame, text='Supplier Name', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=100)
    snameentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    snameentry.place(x=375, y=100)

    Label(DetailsFrame, text='Contact Number', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=150)
    numberentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    numberentry.place(x=375, y=150)

    Label(DetailsFrame, text='Email', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=200)
    emailentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    emailentry.place(x=375, y=200)

    Label(DetailsFrame, text='Address', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=250)
    addressentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    addressentry.place(x=375, y=250)

    # Button to trigger the update operation
    update_button = Button(DetailsFrame, text='Update Supplier', command=update_supplier_details,
                           font=('Georgia', 16, 'bold'), bg='light blue', fg='black', width=20)
    update_button.place(relx=0.5, y=400, anchor='center')

    # Function when back button is pressed
    def backpage():
        root12.destroy()
        update_medicine()

    # Button for going back to previous page
    backbutton = Button(root12, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root12.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root12, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root12.mainloop()

#updating in medicine
def updatebymedicine():
    root13 = Tk()
    root13.geometry('1000x700+250+50')
    root13.title('Update Medicine Page')
    root13.resizable(0, 0)
    root13.config(bg='gray')
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root13, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def resetfield():
        midentry.delete(0, END)
        mnameentry.delete(0, END)
        brandentry.delete(0, END)
        batchnoentry.delete(0, END)
        expdateentry.delete(0, END)
        qtyentry.delete(0, END)
        priceentry.delete(0, END)
        sidentry.delete(0, END)

    def validate_medicine_id(me):
        # Medicine ID should match format like M001, M002, etc.
        return bool(re.match(r'^M\d{3}$', me))

    def validate_batch_number(be):
        # Batch Number should match format like BATCH123
        return bool(re.match(r'^BATCH\d{3}$', be))

    def validate_expiry_date(ee):
        # Expiry Date should match format dd-mon-yy
        return bool(re.match(r'^\d{2}-[A-Za-z]{3}-\d{2}$', ee))

    def validate_supplier_id(se):
        # Supplier ID should match format like S001, S002, etc.
        return bool(re.match(r'^S\d{3}$', se))

    def update_medicine_details():
        me = midentry.get()  # Medicine ID (primary key for identification)
        mne = mnameentry.get()  # Medicine Name
        bre = brandentry.get()  # Brand
        be = batchnoentry.get()  # Batch Number
        ee = expdateentry.get()  # Expiry Date
        qe = qtyentry.get()  # Quantity
        pe = priceentry.get()  # Price
        se = sidentry.get()  # Supplier ID

        # Check if Medicine ID is valid and exists
        if not validate_medicine_id(me):
            messagebox.showerror('Error!', 'Please enter a valid Medicine ID (e.g., M001).')
            resetfield()
            return

        # Check if Medicine ID exists in the table
        try:
            query = "SELECT COUNT(*) FROM MEDICINE WHERE medicine_id = :1"
            params = (me,)
            result = dbms.execute_query(query, params)
            if result[0][0] == 0:
                messagebox.showerror('Error!', f'Medicine ID {me} does not exist in the table.')
                resetfield()
                return
        except Exception as e:
            messagebox.showerror('Error!', f'Failed to check Medicine ID: {str(e)}')
            resetfield()
            return

        # Validate Batch Number
        if not validate_batch_number(be):
            messagebox.showerror('Error!', 'Please enter a valid Batch Number (e.g., BATCH123).')
            resetfield()
            return

        # Validate Expiry Date
        if not validate_expiry_date(ee):
            messagebox.showerror('Error!', 'Please enter a valid Expiry Date (dd-mon-yy).')
            resetfield()
            return

        # Validate Quantity and Price (Non-negative)
        if not (qe.isdigit() and int(qe) >= 0):
            messagebox.showerror('Error!', 'Please enter a valid non-negative Quantity.')
            resetfield()
            return
        if not (pe.replace('.', '', 1).isdigit() and float(pe) >= 0):
            messagebox.showerror('Error!', 'Please enter a valid non-negative Price.')
            resetfield()
            return

        # Validate Supplier ID
        if not validate_supplier_id(se):
            messagebox.showerror('Error!', 'Please enter a valid Supplier ID (e.g., S001).')
            resetfield()
            return

        # Check if Supplier ID exists in the supplier table
        try:
            query = "SELECT COUNT(*) FROM SUPPLIER WHERE supplier_id = :1"
            params = (se,)
            result = dbms.execute_query(query, params)
            if result[0][0] == 0:
                messagebox.showerror('Error!', f'Supplier ID {se} does not exist in the Supplier table.')
                resetfield()
                return
        except Exception as e:
            messagebox.showerror('Error!', f'Failed to check Supplier ID: {str(e)}')
            resetfield()
            return

        # If all validations pass, update the record
        try:
            query = """
                UPDATE MEDICINE 
                SET m_name=:1, brand=:2, batch_number=:3, expiry_date=:4, quantity=:5, price=:6, supplier_id=:7 
                WHERE medicine_id=:8
            """
            params = (mne, bre, be, ee, qe, pe, se, me)
            dbms.execute_query(query, params)
            messagebox.showinfo('Success!', f'Medicine ID {me} updated successfully.')
            resetfield()
        except Exception as e:
            messagebox.showerror('Update Failed', str(e))
            resetfield()
            
    # Create top frame for displaying title
    Topframe = Frame(root13, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Update into Medicine Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root13, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    # Create entry fields and labels for the medicine update form
    Label(DetailsFrame, text='Medicine ID', font=('Georgia', 14), fg='white', bg='black').place(x=200, y=50)
    midentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    midentry.place(x=375, y=50)

    Label(DetailsFrame, text='Medicine Name', font=('Georgia', 14), fg='white', bg='black').place(x=200, y=100)
    mnameentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    mnameentry.place(x=375, y=100)

    Label(DetailsFrame, text='Brand', font=('Georgia', 14), fg='white', bg='black').place(x=200, y=150)
    brandentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    brandentry.place(x=375, y=150)

    Label(DetailsFrame, text='Batch Number', font=('Georgia', 14), fg='white', bg='black').place(x=200, y=200)
    batchnoentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    batchnoentry.place(x=375, y=200)

    Label(DetailsFrame, text='Expiry Date', font=('Georgia', 14), fg='white', bg='black').place(x=200, y=250)
    expdateentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    expdateentry.place(x=375, y=250)

    Label(DetailsFrame, text='Quantity', font=('Georgia', 14), fg='white', bg='black').place(x=200, y=300)
    qtyentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    qtyentry.place(x=375, y=300)

    Label(DetailsFrame, text='Price', font=('Georgia', 14), fg='white', bg='black').place(x=200, y=350)
    priceentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    priceentry.place(x=375, y=350)

    Label(DetailsFrame, text='Supplier ID', font=('Georgia', 14), fg='white', bg='black').place(x=200, y=400)
    sidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    sidentry.place(x=375, y=400)

    # Button to trigger the update operation
    update_button = Button(DetailsFrame, text='Update Medicine', command=update_medicine_details,
                           font=('Georgia', 16, 'bold'), bg='light blue', fg='black', width=20)
    update_button.place(relx=0.5, y=475, anchor='center')

    # Function when back button is pressed
    def backpage():
        root13.destroy()
        update_medicine()

    # Button for going back to previous page
    backbutton = Button(root13, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root13.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root13, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root13.mainloop()

#Updating in customer
def updatebycustomer():
    root14 = Tk()
    root14.geometry('1000x700+250+50')
    root14.title('Update Customer Page')
    root14.resizable(0, 0)
    root14.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root14, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def resetfield():
        cidentry.delete(0, END)
        cnameentry.delete(0, END)
        numberentry.delete(0, END)
        emailentry.delete(0, END)
        addressentry.delete(0, END)

    def update_customer_details():
        cid = cidentry.get()  # Customer ID (primary key for identification)
        cname = cnameentry.get()  # Customer Name
        contact_number = numberentry.get()  # Contact Number
        email = emailentry.get()  # Email
        address = addressentry.get()  # Address

        # Check if Customer ID format is valid (e.g., "CUST123")
        def validate_customer_id():
            pattern = r"^C\d{3}$"
            if not re.match(pattern, cid):
                messagebox.showerror('Error!', 'Invalid Customer ID format. It should start with "CUST" followed by three digits.')
                return False
            return True

        # Check if email format is valid
        def validate_email():
            pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(pattern, email):
                messagebox.showerror('Error!', 'Invalid Email format. Please enter a valid email address.')
                return False
            return True

        # Check if phone number is valid (should not start with 0 and should be 10 digits)
        def validate_phone():
            if len(contact_number) != 10 or not contact_number.isdigit() or contact_number.startswith("0"):
                messagebox.showerror('Error!', 'Invalid phone number. It must be 10 digits and not start with 0.')
                return False
            return True

        if cid == '':
            messagebox.showerror('Error!', 'Please enter a valid Customer ID to update.')
            resetfield()
        elif not (cname and contact_number and email and address):
            messagebox.showerror('Error!', 'Please fill in all fields to update the customer record.')
            resetfield()
        elif not validate_customer_id():  # Validate customer ID format
            resetfield()
            return
        elif not validate_email():  # Validate email format
            resetfield()
            return
        elif not validate_phone():  # Validate phone number format
            resetfield()
            return
        else:
            try:
                # Check if customer ID exists in the table
                query = "SELECT customer_id FROM CUSTOMER WHERE customer_id = :1"
                params = (cid,)
                c = dbms.fetch_query(query, params)

                if not c:
                    messagebox.showerror('Error!', f'Customer ID {cid} does not exist.')
                    resetfield()
                    return

                query = """
                    UPDATE CUSTOMER
                    SET c_name=:1, contact_number=:2, email=:3, address=:4
                    WHERE customer_id=:5
                """
                params = (cname, contact_number, email, address, cid)
                dbms.execute_query(query, params)
                messagebox.showinfo('Success!', f'Customer ID {cid} updated successfully.')
                resetfield()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                resetfield()

    # Create top frame for displaying title
    Topframe = Frame(root14, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Update into Customer Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root14, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    # Create entry fields and labels for the customer update form
    Label(DetailsFrame, text='Customer ID', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=50)
    cidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    cidentry.place(x=375, y=50)

    Label(DetailsFrame, text='New Customer Name', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=100)
    cnameentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    cnameentry.place(x=375, y=100)

    Label(DetailsFrame, text='New Contact Number', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=150)
    numberentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    numberentry.place(x=375, y=150)

    Label(DetailsFrame, text='New Email', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=200)
    emailentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    emailentry.place(x=375, y=200)

    Label(DetailsFrame, text='New Address', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=250)
    addressentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    addressentry.place(x=375, y=250)

    # Button to trigger the update operation
    update_button = Button(DetailsFrame, text='Update Customer', command=update_customer_details,
                           font=('Georgia', 16, 'bold'), bg='light blue', fg='black', width=20)
    update_button.place(relx=0.5, y=400, anchor='center')

    # Function when back button is pressed
    def backpage():
        root14.destroy()
        update_medicine()

    # Button for going back to previous page
    backbutton = Button(root14, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root14.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root14, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root14.mainloop()

#Updating in prescription
def updatebyprescription():
    root15 = Tk()
    root15.geometry('1000x700+250+50')
    root15.title('Update Prescription Page')
    root15.resizable(0, 0)
    root15.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root15, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def resetfield():
        pidentry.delete(0, END)
        cidentry.delete(0, END)
        docnameentry.delete(0, END)
        dateentry.delete(0, END)
        dosageentry.delete(0, END)
        freqentry.delete(0, END)
        durationentry.delete(0, END)
        addinentry.delete(0, END)

    def validate_prescription_id(pid):
        # Check if prescription ID is in the correct format (e.g., P002)
        return bool(re.match(r'^P\d{3}$', pid))

    def validate_customer_exists(cid):
        # Check if customer ID exists in the database
        query = "SELECT COUNT(*) FROM CUSTOMER WHERE customer_id=:1"
        result = dbms.execute_query(query, (cid,))
        return result[0][0] > 0  # Returns True if customer exists, otherwise False

    def validate_prescription_date(date):
        # Check if prescription date is in the correct format (dd-mon-yy)
        try:
            datetime.datetime.strptime(date, '%d-%b-%y')
            return True
        except ValueError:
            return False

    def update_prescription_details():
        pe = pidentry.get()  # Prescription ID (primary key for identification)
        ce = cidentry.get()  # Customer ID
        dne = docnameentry.get()  # Doctor Name
        pde = dateentry.get()  # Prescription Date
        doe = dosageentry.get()  # Dosage
        fe = freqentry.get()  # Frequency
        due = durationentry.get()  # Duration
        ae = addinentry.get()  # Additional Instructions

        if pe == '':
            messagebox.showerror('Error!', 'Please enter a valid Prescription ID to update.')
            resetfield()
        elif not (ce and dne and pde and doe and fe and due and ae):
            messagebox.showerror('Error!', 'Please fill in all fields to update the prescription.')
            resetfield()
        elif not validate_prescription_id(pe):
            messagebox.showerror('Error!', 'Prescription ID format is invalid. It should be in the format Pxxx (e.g., P002).')
            resetfield()
        elif not validate_customer_exists(ce):
            messagebox.showerror('Error!', 'Customer ID does not exist in the database.')
            resetfield()
        elif not validate_prescription_date(pde):
            messagebox.showerror('Error!', 'Prescription date should be in the format dd-mon-yy (e.g., 01-Jan-24).')
            resetfield()
        else:
            # Check if Prescription ID exists in the database
            try:
                check_query = "SELECT COUNT(*) FROM PRESCRIPTION WHERE prescription_id=:1"
                prescription_count = dbms.execute_query(check_query, (pe,))[0][0]
                if prescription_count == 0:
                    messagebox.showerror('Error!', 'Prescription ID does not exist in the database.')
                    resetfield()
                    return
            except Exception as e:
                messagebox.showerror('Error!', f'Error checking Prescription ID: {e}')
                resetfield()
                return

            # If all validations pass, proceed with the update
            try:
                query = """
                    UPDATE PRESCRIPTION
                    SET customer_id=:1, doctor_name=:2, prescription_date=:3, dosage=:4,
                        frequency=:5, duration=:6, additional_instructions=:7
                    WHERE prescription_id=:8
                """
                params = (ce, dne, pde, doe, fe, due, ae, pe)
                dbms.execute_query(query, params)
                messagebox.showinfo('Success!', f'Prescription ID {pe} updated successfully.')
                resetfield()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                resetfield()

    
    # Create top frame for displaying title
    Topframe = Frame(root15, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Update into Prescription Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root15, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    # Create entry fields and labels for the prescription update form
    Label(DetailsFrame, text='Prescription ID', font=('Georgia', 14), fg='white', bg='black').place(x=160, y=50)
    pidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    pidentry.place(x=395, y=50)

    Label(DetailsFrame, text='New Customer ID', font=('Georgia', 14), fg='white', bg='black').place(x=160, y=100)
    cidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    cidentry.place(x=395, y=100)

    Label(DetailsFrame, text='New Doctor Name', font=('Georgia', 14), fg='white', bg='black').place(x=160, y=150)
    docnameentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    docnameentry.place(x=395, y=150)

    Label(DetailsFrame, text='New Prescription Date', font=('Georgia', 14), fg='white', bg='black').place(x=160, y=200)
    dateentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    dateentry.place(x=395, y=200)

    Label(DetailsFrame, text='New Dosage', font=('Georgia', 14), fg='white', bg='black').place(x=160, y=250)
    dosageentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    dosageentry.place(x=395, y=250)

    Label(DetailsFrame, text='New Frequency', font=('Georgia', 14), fg='white', bg='black').place(x=160, y=300)
    freqentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    freqentry.place(x=395, y=300)

    Label(DetailsFrame, text='New Duration', font=('Georgia', 14), fg='white', bg='black').place(x=160, y=350)
    durationentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    durationentry.place(x=395, y=350)

    Label(DetailsFrame, text='New Additional Instructions', font=('Georgia', 14), fg='white', bg='black').place(x=160, y=400)
    addinentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    addinentry.place(x=395, y=400)

    # Button to trigger the update operation
    update_button = Button(DetailsFrame, text='Update Prescription', command=update_prescription_details,
                           font=('Georgia', 16, 'bold'), bg='light blue', fg='black', width=20)
    update_button.place(relx=0.5, y=475, anchor='center')

    # Function when back button is pressed
    def backpage():
        root15.destroy()
        update_medicine()

    # Button for going back to previous page
    backbutton = Button(root15, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root15.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root15, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root15.mainloop()

#Updating in sales
def updatebysales():
    root16 = Tk()
    root16.geometry('1000x700+250+50')
    root16.title('Update Sales Page')
    root16.resizable(0, 0)
    root16.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root16, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def resetfield():
        sidentry.delete(0, END)
        cidentry.delete(0, END)
        sdateentry.delete(0, END)
        totamtentry.delete(0, END)
        payentry.delete(0, END)

    def update_sales_details():
        sid = sidentry.get()  # Sale ID (primary key for identification)
        cid = cidentry.get()  # Customer ID
        sdate = sdateentry.get()  # Sale Date
        total_amt = totamtentry.get()  # Total Amount
        payment_method = payentry.get()  # Payment Method

        # Check if Sale ID exists in the SALES table
        try:
            check_sale_query = "SELECT COUNT(*) FROM SALES WHERE sale_id=:1"
            sale_count = dbms.execute_query(check_sale_query, (sid,))[0][0]
            if sale_count == 0:
                messagebox.showerror('Error!', f'Sale ID {sid} does not exist in the SALES table.')
                resetfield()
                return
        except Exception as e:
            messagebox.showerror('Error!', f'Error checking Sale ID: {e}')
            resetfield()
            return

        # Check if Sale ID is in the correct format (S002 something)
        if not re.match(r'^S\d{3} .+', sid):
            messagebox.showerror('Error!', 'Sale ID must be in the format S002 something.')
            resetfield()
            return

        # Check if Customer ID is in the correct format (C002) and exists in the customer table
        if not re.match(r'^C\d{3}$', cid):
            messagebox.showerror('Error!', 'Customer ID must be in the format C002.')
            resetfield()
            return

        # Validate if the Customer ID exists in the database (assuming the database has a check for this)
        try:
            check_query = "SELECT COUNT(*) FROM CUSTOMER WHERE customer_id=:1"
            customer_count = dbms.execute_query(check_query, (cid,))[0][0]
            if customer_count == 0:
                messagebox.showerror('Error!', 'Customer ID does not exist in the database.')
                resetfield()
                return
        except Exception as e:
            messagebox.showerror('Error!', f'Error checking Customer ID: {e}')
            resetfield()
            return

        # Check if Sale Date is in the correct format (dd-mon-yy)
        try:
            datetime.strptime(sdate, "%d-%b-%y")  # Validates the date format
        except ValueError:
            messagebox.showerror('Error!', 'Sale Date must be in the format dd-mon-yy.')
            resetfield()
            return

        # Check if Total Amount is a non-negative number
        try:
            total_amt = float(total_amt)
            if total_amt < 0:
                raise ValueError("Total Amount must be a non-negative value.")
        except ValueError:
            messagebox.showerror('Error!', 'Total Amount must be a valid non-negative number.')
            resetfield()
            return

        if not (cid and sdate and total_amt >= 0 and payment_method):
            messagebox.showerror('Error!', 'Please fill in all fields to update the sale record.')
            resetfield()
            return
        else:
            try:
                query = """
                    UPDATE SALES
                    SET customer_id=:1, sale_date=:2, total_amount=:3, payment_method=:4
                    WHERE sale_id=:5
                """
                params = (cid, sdate, total_amt, payment_method, sid)
                dbms.execute_query(query, params)
                messagebox.showinfo('Success!', f'Sale ID {sid} updated successfully.')
                resetfield()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                resetfield()

            
    # Create top frame for displaying title
    Topframe = Frame(root16, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Update into Sales Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root16, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    # Create entry fields and labels for the sales update form
    Label(DetailsFrame, text='Sale ID', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=50)
    sidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    sidentry.place(x=375, y=50)

    Label(DetailsFrame, text='New Customer ID', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=100)
    cidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    cidentry.place(x=375, y=100)

    Label(DetailsFrame, text='New Sale Date', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=150)
    sdateentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    sdateentry.place(x=375, y=150)

    Label(DetailsFrame, text='New Total Amount', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=200)
    totamtentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    totamtentry.place(x=375, y=200)

    Label(DetailsFrame, text='New Payment Method', font=('Georgia', 14), fg='white', bg='black').place(x=180, y=250)
    payentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    payentry.place(x=375, y=250)

    # Button to trigger the update operation
    update_button = Button(DetailsFrame, text='Update Sales', command=update_sales_details, font=('Georgia', 16, 'bold'), bg='light blue', fg='black', width=20)
    update_button.place(relx=0.5, y=400, anchor='center')

    # Function when back button is pressed
    def backpage():
        root16.destroy()
        update_medicine()

    # Button for going back to previous page
    backbutton = Button(root16, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root16.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root16, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root16.mainloop()

#Updating in sales items
def updatebysalesitems():
    root17 = Tk()
    root17.geometry('1000x700+250+50')
    root17.title('Update Sales Items Page')
    root17.resizable(0, 0)
    root17.config(bg='gray')

    def resetfield():
        saidentry.delete(0, END)
        sidentry.delete(0, END)
        midentry.delete(0, END)
        qtyentry.delete(0, END)
        priceentry.delete(0, END)

    def is_valid_sale_item_id(sale_item_id):
        return bool(re.match(r"^SI\d{3}$", sale_item_id))

    def is_valid_sale_id(sale_id):
        return bool(re.match(r"^S\d{3}$", sale_id))

    def is_valid_medicine_id(medicine_id):
        return bool(re.match(r"^M\d{3}$", medicine_id))

    def is_non_negative(value):
        try:
            return float(value) >= 0
        except ValueError:
            return False

    def update_sales_items_details():
        sale_item_id = saidentry.get()  # Sale Item ID (primary key for identification)
        sale_id = sidentry.get()  # Sale ID
        medicine_id = midentry.get()  # Medicine ID
        quantity = qtyentry.get()  # Quantity
        price_per_unit = priceentry.get()  # Price Per Unit

        if sale_item_id == '' or not is_valid_sale_item_id(sale_item_id):
            messagebox.showerror('Error!', 'Please enter a valid Sale Item ID (format SIxxx).')
            resetfield()
            return
        elif sale_id == '' or not is_valid_sale_id(sale_id):
            messagebox.showerror('Error!', 'Please enter a valid Sale ID (format Sxxx).')
            resetfield()
            return
        elif medicine_id == '' or not is_valid_medicine_id(medicine_id):
            messagebox.showerror('Error!', 'Please enter a valid Medicine ID (format Mxxx).')
            resetfield()
            return
        elif not is_non_negative(quantity) or not is_non_negative(price_per_unit):
            messagebox.showerror('Error!', 'Quantity and Price Per Unit must be non-negative values.')
            resetfield()
            return

        # Check if Sale Item ID exists
        query = "SELECT COUNT(*) FROM SALES_ITEMS WHERE sale_item_id = :1"
        if dbms.execute_query(query, (sale_item_id,))[0][0] == 0:
            messagebox.showerror('Error!', f'Sale Item ID {sale_item_id} does not exist.')
            resetfield()
            return

        # Check if Sale ID exists
        query = "SELECT COUNT(*) FROM SALES WHERE sale_id = :1"
        if dbms.execute_query(query, (sale_id,))[0][0] == 0:
            messagebox.showerror('Error!', f'Sale ID {sale_id} does not exist.')
            resetfield()
            return

        # Check if Medicine ID exists
        query = "SELECT COUNT(*) FROM MEDICINE WHERE medicine_id = :1"
        if dbms.execute_query(query, (medicine_id,))[0][0] == 0:
            messagebox.showerror('Error!', f'Medicine ID {medicine_id} does not exist.')
            resetfield()
            return

        try:
            subtotal = int(quantity) * float(price_per_unit)  # Calculate subtotal
            query = """
                UPDATE SALES_ITEMS
                SET sale_id = :1, medicine_id = :2, quantity = :3, price_per_unit = :4, subtotal = :5
                WHERE sale_item_id = :6
            """
            params = (sale_id, medicine_id, quantity, price_per_unit, subtotal, sale_item_id)
            dbms.execute_query(query, params)
            messagebox.showinfo('Success!', f'Sale Item ID {sale_item_id} updated successfully.')
            resetfield()
        except Exception as e:
            messagebox.showerror('Update Failed', str(e))
            resetfield()

    # Create top frame for displaying title
    Topframe = Frame(root17, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Update into Sales Items Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root17, bg='black', width=820, height=520)
    DetailsFrame.place(x=90, y=150)

    # Create entry fields and labels for the sales items update form
    Label(DetailsFrame, text='Sale Item ID', font=('Georgia', 14), fg='white', bg='black').place(x=165, y=100)
    saidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    saidentry.place(x=375, y=100)

    Label(DetailsFrame, text='New Sale ID', font=('Georgia', 14), fg='white', bg='black').place(x=165, y=150)
    sidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    sidentry.place(x=375, y=150)

    Label(DetailsFrame, text='New Medicine ID', font=('Georgia', 14), fg='white', bg='black').place(x=165, y=200)
    midentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    midentry.place(x=375, y=200)

    Label(DetailsFrame, text='New Quantity', font=('Georgia', 14), fg='white', bg='black').place(x=165, y=250)
    qtyentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    qtyentry.place(x=375, y=250)

    Label(DetailsFrame, text='New Price Per Unit', font=('Georgia', 14), fg='white', bg='black').place(x=165, y=300)
    priceentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    priceentry.place(x=375, y=300)

    # Button to trigger the update operation
    update_button = Button(DetailsFrame, text='Update Sales Item', command=update_sales_items_details,
                           font=('Georgia', 16, 'bold'), bg='light blue', fg='black', width=20)
    update_button.place(relx=0.5, y=400, anchor='center')

    # Function when back button is pressed
    def backpage():
        root17.destroy()
        update_medicine()

    # Button for going back to previous page
    backbutton = Button(root17, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back home button is pressed
    def backtohome():
        root17.destroy()
        introscreen()

    # Button for going back to home page
    home_page_button = Button(root17, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root17.mainloop()

#Updating a medicine
def update_medicine():
    #Create a tkinter page for the update medicine page
    root4 = Tk()
    root4.geometry('1000x700+250+50') #Set window size
    root4.title('Update Medicine Page') #Set window title
    root4.resizable(0,0) # Disable window resizing
    root4.config(bg='gray') #Set background colour

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root4, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Function when back home button is pressed
    def backtohome():
        root4.destroy()
        introscreen()
    
    #Create top frame for displaying title
    Topframe = Frame(root4, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Update by',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    ButtonsFrame = Frame(root4,bg='black',width=520,height=500)
    ButtonsFrame.place(x=240,y=150)

    #Function when buttons are pressed for updating into specific tables
    def update_supplier():
        root4.destroy()
        updatebysupplier()
    
    def update_medicine():
        root4.destroy()
        updatebymedicine()

    def update_customer():
        root4.destroy()
        updatebycustomer()

    def update_prescription():
        root4.destroy()
        updatebyprescription()

    def update_sales():
        root4.destroy()
        updatebysales()

    def update_sales_items():
        root4.destroy()
        updatebysalesitems()

    #Button for updating medicine by supplier
    supplier_button = Button(ButtonsFrame,text='Supplier',command=update_supplier,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=40,width=220)

    #Button for updating medicine by medicine
    medicine_button = Button(ButtonsFrame,text='Medicine',command=update_medicine,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    medicine_button.place(x=150,y=115,width=220)

    #Button for updating medicine by customer
    customer_button = Button(ButtonsFrame,text='Customer',command=update_customer,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    customer_button.place(x=150,y=190,width=220)

    #Button for updating medicine by prescription
    prescription_button = Button(ButtonsFrame,text='Prescription',command=update_prescription,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    prescription_button.place(x=150,y=265,width=220)

    #Button for updating medicine by sales
    sales_button = Button(ButtonsFrame,text='Sales',command=update_sales,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    sales_button.place(x=150,y=340,width=220)

    #Button for updating medicine by sales
    salesitems_button = Button(ButtonsFrame,text='Sales Items',command=update_sales_items,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    salesitems_button.place(x=150,y=415,width=220)

    #Button for going back to home page
    home_page_button = Button(root4,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root4.mainloop()

# Delete supplier record
def deletebysupplier():
    root_del_supplier = Tk()
    root_del_supplier.geometry('1000x525')
    root_del_supplier.title('Delete Supplier')
    root_del_supplier.resizable(0, 0)
    root_del_supplier.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root_del_supplier, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def delete_supplier():
        sid = sidentry.get()  # Supplier ID

        # Check if Supplier ID is in the correct format (e.g., S002)
        if not re.match(r'^S\d{3}$', sid):
            messagebox.showerror('Error!', 'Supplier ID format is invalid. It should be in the format Sxxx (e.g., S002).')
            return

        if sid == '':
            messagebox.showerror('Error!', 'Please enter a Supplier ID to delete.')
            return
        else:
            # Check if Supplier ID exists in the SUPPLIER table
            try:
                check_query = "SELECT COUNT(*) FROM SUPPLIER WHERE supplier_id=:1"
                result = dbms.fetch_query(check_query, (sid,))
                
                # Check if result is valid and contains data
                if result and result[0][0] > 0:
                    supplier_count = result[0][0]
                else:
                    messagebox.showerror('Error!', 'Supplier ID does not exist in the database.')
                    sidentry.delete(0, END)
                    return
            except Exception as e:
                messagebox.showerror('Error!', f'Error checking Supplier ID: {e}')
                sidentry.delete(0, END)
                return

            # If all checks pass, proceed with deletion
            try:
                query = "DELETE FROM SUPPLIER WHERE supplier_id=:1"
                dbms.execute_query(query, (sid,))
                messagebox.showinfo('Success!', f'Supplier ID {sid} deleted successfully.')
                sidentry.delete(0, END)
            except Exception as e:
                messagebox.showerror('Delete Failed', str(e))

    #Create top frame for displaying title
    Topframe = Frame(root_del_supplier, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)#Create top frame for displaying title

    #Title text for the introduction
    Introtext = Label(Topframe, text='Delete from Supplier Table',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    DetailsFrame = Frame(root_del_supplier,bg='black',width=820,height=330)
    DetailsFrame.place(x=90,y=150)

    Label(DetailsFrame, text='Supplier ID', font=('Georgia', 14), fg='white', bg='black').place(x=220, y=100)
    sidentry = Entry(DetailsFrame, font=('Georgia', 14), width=20)
    sidentry.place(x=375, y=100)

    delete_button = Button(DetailsFrame, text='Delete Supplier', command=delete_supplier,
                           font=('Georgia', 14), bg='light blue', fg='black')
    delete_button.place(relx=0.5, y=220, anchor='center')

    #Function when back button is pressed
    def backpage():
        root_del_supplier.destroy()
        delete_medicine()

    #Button for going back to previous page
    backbutton = Button(root_del_supplier,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root_del_supplier.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root_del_supplier,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root_del_supplier.mainloop()

# Delete medicine record
def deletebymedicine():
    root_del_medicine = Tk()
    root_del_medicine.geometry('1000x525')
    root_del_medicine.title('Delete Medicine')
    root_del_medicine.resizable(0, 0)
    root_del_medicine.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root_del_medicine, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def delete_medicine():
        mid = midentry.get()  # Get the medicine_id from the entry field

        # Check if Medicine ID is in the correct format (e.g., M002)
        if not re.match(r'^M\d{3}$', mid):
            messagebox.showerror('Error!', 'Medicine ID format is invalid. It should be in the format Mxxx (e.g., M002).')
            return

        if mid == '':
            messagebox.showerror('Error!', 'Please enter a Medicine ID to delete.')
            return
        else:
            # Check if Medicine ID exists in the MEDICINE table
            try:
                check_query = "SELECT COUNT(*) FROM MEDICINE WHERE medicine_id=:1"
                result = dbms.fetch_query(check_query, (mid,))
                
                # Check if result is valid and contains data
                if result and result[0][0] > 0:
                    medicine_count = result[0][0]
                else:
                    messagebox.showerror('Error!', 'Medicine ID does not exist in the database.')
                    midentry.delete(0, END)
                    return
            except Exception as e:
                messagebox.showerror('Error!', f'Error checking Medicine ID: {e}')
                midentry.delete(0, END)
                return

            # If all checks pass, proceed with deletion
            try:
                query = "DELETE FROM MEDICINE WHERE medicine_id = :1"
                dbms.execute_query(query, (mid,))
                messagebox.showinfo('Success!', f'Medicine ID {mid} deleted successfully.')
                midentry.delete(0, END)
            except Exception as e:
                messagebox.showerror('Delete Failed', str(e))

    # Create top frame for displaying title
    Topframe = Frame(root_del_medicine, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Delete from Medicine Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root_del_medicine, bg='black', width=820, height=330)
    DetailsFrame.place(x=90, y=150)

    # Label and entry for Medicine ID
    Label(DetailsFrame, text='Medicine ID', font=('Georgia', 14), fg='white', bg='black').place(x=220, y=100)
    midentry = Entry(DetailsFrame, font=('Georgia', 14), width=20)
    midentry.place(x=375, y=100)

    # Button to delete the medicine entry
    delete_button = Button(DetailsFrame, text='Delete Medicine', command=delete_medicine,
                           font=('Georgia', 14), bg='light blue', fg='black')
    delete_button.place(relx=0.5, y=220, anchor='center')

    # Function when back button is pressed
    def backpage():
        root_del_medicine.destroy()
        delete_medicine()  # Adjust this to navigate back to the appropriate page if needed

    # Button for going back to the previous page
    backbutton = Button(root_del_medicine, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back to home button is pressed
    def backtohome():
        root_del_medicine.destroy()
        introscreen()  # Adjust this to navigate back to the home page if needed

    # Button for going back to the home page
    home_page_button = Button(root_del_medicine, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root_del_medicine.mainloop()

# Delete customer record
def deletebycustomer():
    root_del_customer = Tk()
    root_del_customer.geometry('1000x525')
    root_del_customer.title('Delete Customer')
    root_del_customer.resizable(0, 0)
    root_del_customer.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root_del_customer, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def delete_customer():
        cid = cidentry.get()  # Get the customer_id from the entry field

        # Check if Customer ID is in the correct format (e.g., C002)
        if not re.match(r'^C\d{3}$', cid):
            messagebox.showerror('Error!', 'Customer ID format is invalid. It should be in the format Cxxx (e.g., C002).')
            return

        if cid == '':
            messagebox.showerror('Error!', 'Please enter a Customer ID to delete.')
            return
        else:
            # Check if Customer ID exists in the CUSTOMER table
            try:
                check_query = "SELECT COUNT(*) FROM CUSTOMER WHERE customer_id=:1"
                result = dbms.fetch_query(check_query, (cid,))
                
                # Check if result is valid and contains data
                if result and result[0][0] > 0:
                    customer_count = result[0][0]
                else:
                    messagebox.showerror('Error!', 'Customer ID does not exist in the database.')
                    cidentry.delete(0, END)
                    return
            except Exception as e:
                messagebox.showerror('Error!', f'Error checking Customer ID: {e}')
                cidentry.delete(0, END)
                return

            # If all checks pass, proceed with deletion
            try:
                query = "DELETE FROM CUSTOMER WHERE customer_id = :1"
                dbms.execute_query(query, (cid,))
                messagebox.showinfo('Success!', f'Customer ID {cid} deleted successfully.')
                cidentry.delete(0, END)
            except Exception as e:
                messagebox.showerror('Delete Failed', str(e))


    # Create top frame for displaying title
    Topframe = Frame(root_del_customer, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Delete from Customer Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root_del_customer, bg='black', width=820, height=330)
    DetailsFrame.place(x=90, y=150)

    # Label and entry for Customer ID
    Label(DetailsFrame, text='Customer ID', font=('Georgia', 14), fg='white', bg='black').place(x=220, y=100)
    cidentry = Entry(DetailsFrame, font=('Georgia', 14), width=20)
    cidentry.place(x=375, y=100)

    # Button to delete the customer entry
    delete_button = Button(DetailsFrame, text='Delete Customer', command=delete_customer,
                           font=('Georgia', 14), bg='light blue', fg='black')
    delete_button.place(relx=0.5, y=220, anchor='center')

    # Function when back button is pressed
    def backpage():
        root_del_customer.destroy()
        delete_medicine()  # Adjust this to navigate back to the appropriate page if needed

    # Button for going back to the previous page
    backbutton = Button(root_del_customer, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back to home button is pressed
    def backtohome():
        root_del_customer.destroy()
        introscreen()  # Adjust this to navigate back to the home page if needed

    # Button for going back to the home page
    home_page_button = Button(root_del_customer, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root_del_customer.mainloop()

# Delete prescription record
def deletebyprescription():
    root_del_prescription = Tk()
    root_del_prescription.geometry('1000x525')
    root_del_prescription.title('Delete Prescription')
    root_del_prescription.resizable(0, 0)
    root_del_prescription.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root_del_prescription, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def delete_prescription():
        pid = pidentry.get()  # Get the prescription_id from the entry field

        # Check if Prescription ID is in the correct format (e.g., P001)
        if not re.match(r'^P\d{3}$', pid):
            messagebox.showerror('Error!', 'Prescription ID format is invalid. It should be in the format Pxxx (e.g., P001).')
            return

        if pid == '':
            messagebox.showerror('Error!', 'Please enter a Prescription ID to delete.')
            return
        else:
            # Check if Prescription ID exists in the PRESCRIPTION table
            try:
                check_query = "SELECT COUNT(*) FROM PRESCRIPTION WHERE prescription_id=:1"
                result = dbms.fetch_query(check_query, (pid,))
                
                # Check if result is valid and contains data
                if result and result[0][0] > 0:
                    prescription_count = result[0][0]
                else:
                    messagebox.showerror('Error!', 'Prescription ID does not exist in the database.')
                    pidentry.delete(0, END)
                    return
            except Exception as e:
                messagebox.showerror('Error!', f'Error checking Prescription ID: {e}')
                pidentry.delete(0, END)
                return

            # If all checks pass, proceed with deletion
            try:
                query = "DELETE FROM PRESCRIPTION WHERE prescription_id = :1"
                dbms.execute_query(query, (pid,))
                messagebox.showinfo('Success!', f'Prescription ID {pid} deleted successfully.')
                pidentry.delete(0, END)
            except Exception as e:
                messagebox.showerror('Delete Failed', str(e))


    # Create top frame for displaying title
    Topframe = Frame(root_del_prescription, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Delete from Prescription Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root_del_prescription, bg='black', width=820, height=330)
    DetailsFrame.place(x=90, y=150)

    # Label and entry for Prescription ID
    Label(DetailsFrame, text='Prescription ID', font=('Georgia', 14), fg='white', bg='black').place(x=220, y=100)
    pidentry = Entry(DetailsFrame, font=('Georgia', 14), width=20)
    pidentry.place(x=375, y=100)

    # Button to delete the prescription entry
    delete_button = Button(DetailsFrame, text='Delete Prescription', command=delete_prescription,
                           font=('Georgia', 14), bg='light blue', fg='black')
    delete_button.place(relx=0.5, y=220, anchor='center')

    # Function when back button is pressed
    def backpage():
        root_del_prescription.destroy()
        delete_medicine()  # Adjust this to navigate back to the appropriate page if needed

    # Button for going back to the previous page
    backbutton = Button(root_del_prescription, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back to home button is pressed
    def backtohome():
        root_del_prescription.destroy()
        introscreen()  # Adjust this to navigate back to the home page if needed

    # Button for going back to the home page
    home_page_button = Button(root_del_prescription, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root_del_prescription.mainloop()

# Delete sales record
def deletebysales():
    root_del_sales = Tk()
    root_del_sales.geometry('1000x525')
    root_del_sales.title('Delete Sale')
    root_del_sales.resizable(0, 0)
    root_del_sales.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root_del_sales, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def delete_sale():
        sale_id = saleidentry.get()  # Get the sale_id from the entry field

        # Check if Sale ID is in the correct format (e.g., S003)
        if not re.match(r'^S\d{3}$', sale_id):
            messagebox.showerror('Error!', 'Sale ID format is invalid. It should be in the format Sxxx (e.g., S003).')
            return

        if sale_id == '':
            messagebox.showerror('Error!', 'Please enter a Sale ID to delete.')
        else:
            # Check if Sale ID exists in the SALES table
            try:
                check_query = "SELECT COUNT(*) FROM SALES WHERE sale_id=:1"
                result = dbms.fetch_query(check_query, (sale_id,))  # Use fetch_query instead of execute_query for retrieval
                if result[0][0] == 0:
                    messagebox.showerror('Error!', 'Sale ID does not exist in the database.')
                    saleidentry.delete(0, END)
                    return
            except Exception as e:
                messagebox.showerror('Error!', f'Error checking Sale ID: {e}')
                saleidentry.delete(0, END)
                return

            # If all checks pass, proceed with deletion
            try:
                delete_query = "DELETE FROM SALES WHERE sale_id = :1"
                dbms.execute_query(delete_query, (sale_id,))
                messagebox.showinfo('Success!', f'Sale ID {sale_id} deleted successfully.')
                saleidentry.delete(0, END)
            except Exception as e:
                messagebox.showerror('Delete Failed', str(e))


    # Create top frame for displaying title
    Topframe = Frame(root_del_sales, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Delete from Sales Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root_del_sales, bg='black', width=820, height=330)
    DetailsFrame.place(x=90, y=150)

    # Label and entry for Sale ID
    Label(DetailsFrame, text='Sale ID', font=('Georgia', 14), fg='white', bg='black').place(x=220, y=100)
    saleidentry = Entry(DetailsFrame, font=('Georgia', 14), width=20)
    saleidentry.place(x=375, y=100)

    # Button to delete the sale entry
    delete_button = Button(DetailsFrame, text='Delete Sale', command=delete_sale,
                           font=('Georgia', 14), bg='light blue', fg='black')
    delete_button.place(relx=0.5, y=220, anchor='center')

    # Function when back button is pressed
    def backpage():
        root_del_sales.destroy()
        delete_medicine()  # Adjust this to navigate back to the appropriate page if needed

    # Button for going back to the previous page
    backbutton = Button(root_del_sales, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back to home button is pressed
    def backtohome():
        root_del_sales.destroy()
        introscreen()  # Adjust this to navigate back to the home page if needed

    # Button for going back to the home page
    home_page_button = Button(root_del_sales, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root_del_sales.mainloop()


# Delete sales items record
def deletebysalesitems():
    root_del_saleitems = Tk()
    root_del_saleitems.geometry('1000x525')
    root_del_saleitems.title('Delete Sale Item')
    root_del_saleitems.resizable(0, 0)
    root_del_saleitems.config(bg='gray')

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root_del_saleitems, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    def delete_sale_item():
        sale_item_id = saleitemidentry.get()  # Get the sale_item_id from the entry field

        # Check if Sale Item ID is in the correct format (e.g., SI002)
        if not re.match(r'^SI\d{3}$', sale_item_id):
            messagebox.showerror('Error!', 'Sale Item ID format is invalid. It should be in the format SIxxx (e.g., SI002).')
            return

        if sale_item_id == '':
            messagebox.showerror('Error!', 'Please enter a Sale Item ID to delete.')
        else:
            # Check if Sale Item ID exists in the SALES_ITEMS table
            try:
                check_query = "SELECT COUNT(*) FROM SALES_ITEMS WHERE sale_item_id=:1"
                result = dbms.fetch_query(check_query, (sale_item_id,))
                if result[0][0] == 0:
                    messagebox.showerror('Error!', 'Sale Item ID does not exist in the database.')
                    saleitemidentry.delete(0, END)
                    return
            except Exception as e:
                messagebox.showerror('Error!', f'Error checking Sale Item ID: {e}')
                saleitemidentry.delete(0, END)
                return

            # If all checks pass, proceed with deletion
            try:
                delete_query = "DELETE FROM SALES_ITEMS WHERE sale_item_id = :1"
                dbms.execute_query(delete_query, (sale_item_id,))
                messagebox.showinfo('Success!', f'Sale Item ID {sale_item_id} deleted successfully.')
                saleitemidentry.delete(0, END)
            except Exception as e:
                messagebox.showerror('Delete Failed', str(e))


    # Create top frame for displaying title
    Topframe = Frame(root_del_saleitems, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Delete from Sales Items Table', font=('Georgia', 23, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=25, width=900)

    DetailsFrame = Frame(root_del_saleitems, bg='black', width=820, height=330)
    DetailsFrame.place(x=90, y=150)

    # Label and entry for Sale Item ID
    Label(DetailsFrame, text='Sale Item ID', font=('Georgia', 14), fg='white', bg='black').place(x=220, y=100)
    saleitemidentry = Entry(DetailsFrame, font=('Georgia', 14), width=20)
    saleitemidentry.place(x=375, y=100)

    # Button to delete the sale item entry
    delete_button = Button(DetailsFrame, text='Delete Sale Item', command=delete_sale_item,
                           font=('Georgia', 14), bg='light blue', fg='black')
    delete_button.place(relx=0.5, y=220, anchor='center')

    # Function when back button is pressed
    def backpage():
        root_del_saleitems.destroy()
        delete_medicine()  # Adjust to navigate back to the appropriate page if needed

    # Button for going back to the previous page
    backbutton = Button(root_del_saleitems, text='Back', command=backpage, font=('Georgia', 18, 'bold'),
                        cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    backbutton.place(x=20, y=25, width=220)

    # Function when back to home button is pressed
    def backtohome():
        root_del_saleitems.destroy()
        introscreen()  # Adjust to navigate back to the home page if needed

    # Button for going back to the home page
    home_page_button = Button(root_del_saleitems, text='Back to home', command=backtohome, font=('Georgia', 18, 'bold'),
                              cursor='hand2', bd=0, bg='light blue', fg='black', activebackground='light blue')
    home_page_button.place(x=760, y=25, width=220)

    root_del_saleitems.mainloop()



#Deleting a medicine
def delete_medicine():
    #Create a tkinter page for the delete medicine page
    root5 = Tk()
    root5.geometry('1000x700+250+50') #Set window size
    root5.title('Delete Medicine Page') #Set window title
    root5.resizable(0,0) # Disable window resizing
    root5.config(bg='gray') #Set background colour

    #Function when back home button is pressed
    def backtohome():
        root5.destroy()
        introscreen()

    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root5, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Create top frame for displaying title
    Topframe = Frame(root5, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Delete by',font=('Georgia', 23,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=25,width=900)

    ButtonsFrame = Frame(root5,bg='black',width=520,height=500)
    ButtonsFrame.place(x=240,y=150)

    #Function when buttons are pressed for deleting into specific tables
    def delete_supplier():
        root5.destroy()
        deletebysupplier()
    
    def delete_medicine():
        root5.destroy()
        deletebymedicine()
    
    def delete_customer():
        root5.destroy()
        deletebycustomer()

    def delete_prescription():
        root5.destroy()
        deletebyprescription()

    def delete_sales():
        root5.destroy()
        deletebysales()
    
    def delete_sales_items():
        root5.destroy()
        deletebysalesitems()

    #Button for deleting medicine by supplier
    supplier_button = Button(ButtonsFrame,text='Supplier',command=delete_supplier,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=40,width=220)

    #Button for deleting medicine by medicine
    supplier_button = Button(ButtonsFrame,text='Medicine',command=delete_medicine,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=115,width=220)

    #Button for deleting medicine by customer
    supplier_button = Button(ButtonsFrame,text='Customer',command=delete_customer,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=190,width=220)

    #Button for deleting medicine by prescription
    supplier_button = Button(ButtonsFrame,text='Prescription',command=delete_prescription,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=265,width=220)

    #Button for deleting medicine by sales
    supplier_button = Button(ButtonsFrame,text='Sales',command=delete_sales,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=340,width=220)

    #Button for deleting medicine by sales
    supplier_button = Button(ButtonsFrame,text='Sales Items',command=delete_sales_items,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    supplier_button.place(x=150,y=415,width=220)

    #Button for going back to home page
    home_page_button = Button(root5,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root5.mainloop()

#Home page screen
def introscreen():
    #Create a tkinter page for the introduction page
    root1 = Tk()
    root1.geometry('1000x700+250+50') #Set window size
    root1.title('Home Page') #Set window title
    root1.resizable(0,0) # Disable window resizing
    root1.config(bg='gray') #Set background colour
    
    bgimg = Image.open(R"C:\Users\Nikhil\Downloads\SSN\College Files\Second Year\3rd Semester\Database Technology Lab\Mini Project\bgpic.jpg")
    bgtk = ImageTk.PhotoImage(bgimg)
    bglabel = Label(root1, image=bgtk, height=750, width=1000)
    bglabel.place(x=0, y=0)

    #Create top frame for displaying title
    Topframe = Frame(root1, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    ButtonsFrame = Frame(root1,bg='black',width=520,height=350)
    ButtonsFrame.place(x=240,y=200)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Ashok Pharmacy',font=('Georgia',28,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    Addresstext = Label(Topframe, text='Shop No 10, 1, Radhakrishnan St, Palaniappa Nagar, Valasaravakkam, Chennai, Tamil Nadu 600087',
                        font=('Georgia',13,'bold'),bg='black',fg='white',activebackground='black')
    Addresstext.place(x=20,y=70,width=950)
    
    #Function when check medicine button is pressed
    def check_med():
        root1.destroy()
        check_medicine()

    #Function when insert medicine button is pressed
    def insert_med():
        root1.destroy()
        insert_medicine()
    
    #Function when update medicine button is pressed
    def update_med():
        root1.destroy()
        update_medicine()
    
    #Function when delete medicine button is pressed
    def delete_med():
        root1.destroy()
        delete_medicine()

    Headingtext = Label(ButtonsFrame, text='Welcome Back',
                        font=('Georgia',20,'bold'),bg='black',fg='white',activebackground='black')
    Headingtext.place(x=10,y=30,width=520)

    #Button for checking medicines
    check_med_button = Button(ButtonsFrame,text='Check medicines',command=check_med,font=('Georgia',17,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    check_med_button.place(x=25,y=140,width=220)

    #Button for inserting medicines
    insert_med_button = Button(ButtonsFrame,text='Insert medicines',command=insert_med,font=('Georgia',17,'bold'),
                               cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    insert_med_button.place(x=275,y=140,width=220)

    #Button for updating medicines
    update_med_button = Button(ButtonsFrame,text='Update medicines',command=update_med,font=('Georgia',17,'bold'),
                               cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    update_med_button.place(x=25,y=250,width=220)

    #Button for deleting medicines
    delete_med_button = Button(ButtonsFrame,text='Delete medicines',command=delete_med,font=('Georgia',17,'bold'),
                               cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    delete_med_button.place(x=275,y=250,width=220)

    # Check near-expiry medicines and display in a message box
    near_expiry_meds = call_procedure_check_near_expiry(dbms)
    if near_expiry_meds:
        near_expiry_message = "Near Expiry Medicines:\n\n"
        for med in near_expiry_meds:
            near_expiry_message += f"Medicine Name: {med[0]}, Expiry Date: {med[1].strftime('%Y-%m-%d')}, Days Remaining: {med[2]}\n"
        messagebox.showinfo("Near Expiry Medicines", near_expiry_message)
    
    # Check low-stock medicines and display in a message box
    low_stock_meds = call_procedure_check_low_stock(dbms)
    if low_stock_meds:
        low_stock_message = "Low Stock Medicines:\n\n"
        for med in low_stock_meds:
            low_stock_message += f"Medicine Name: {med[0]}, Quantity: {med[1]}\n"
        messagebox.showinfo("Low Stock Medicines", low_stock_message)

    root1.mainloop()
    
# Function to call check_near_expiry procedure
def call_procedure_check_near_expiry(db_manager):
    try:
        # Directly use db_manager.cursor without calling it as a function
        expiry_meds = db_manager.cursor.var(cx_Oracle.CURSOR)  # Define cursor variable

        # Call the procedure with the OUT cursor
        db_manager.cursor.callproc("check_near_expiry", [expiry_meds])

        # Fetch all rows from the cursor returned by the procedure
        result_set = expiry_meds.getvalue().fetchall()  # Use getvalue() to retrieve cursor contents
        return result_set
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Database Error", str(e))
        return []


# Function to call check_low_stock procedure
def call_procedure_check_low_stock(db_manager):
    try:
        low_stock_meds = db_manager.cursor.var(cx_Oracle.CURSOR)
        db_manager.cursor.callproc("check_low_stock", [low_stock_meds])
        return low_stock_meds.getvalue()  # Fetch all rows from the cursor
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Database Error", str(e))
        return []

def login():
    # Handles the login button click
    username = username_entry.get()
    password = password_entry.get()
    
    if validate_login(username, password):
        messagebox.showinfo("Login Success", "Welcome!")
        login_window.destroy()  # Close login window on success
        introscreen()
    
def check_password_strength(password):
    # Regular expression to check password strength
    if (len(password) >= 8 and
        re.search(r'[A-Z]', password) and  # At least one uppercase letter
        re.search(r'[a-z]', password) and  # At least one lowercase letter
        re.search(r'[0-9]', password) and  # At least one digit
        re.search(r'[!@#$%^&*()_+]', password)):  # At least one special character
        return True
    return False

def create_account():
    # Handles the creation of a new account
    c_username = c_username_entry.get()
    c_password = c_password_entry.get()

    # Check if username already exists
    if dbms.fetch_query("SELECT * FROM LOGIN WHERE username = :1", (c_username,)):
        messagebox.showerror("Account Creation Failed", "Username already exists.")
        return
    
    # Check password strength
    if not check_password_strength(c_password):
        messagebox.showerror("Weak Password", "Password must be at least 8 characters long, contain uppercase and lowercase letters, a digit, and a special character.")
        return

    # Insert new credentials into the LOGIN table
    dbms.execute_query("INSERT INTO LOGIN (username, password) VALUES (:1, :2)", (c_username, c_password))

    messagebox.showinfo("Account Created", "Your account has been successfully created. Please log in.")
    create_login_window.destroy()
    show_login_window()

def validate_login(username, password):
    # Validates the username and password with the LOGIN table
    result = dbms.fetch_query("SELECT * FROM LOGIN WHERE username = :1 AND password = :2", (username, password))
    return bool(result)

def show_create_login_window():
    login_window.destroy()
    # Displays the window for creating a new login
    global create_login_window, c_username_entry, c_password_entry
    create_login_window = Tk()
    create_login_window.title("Create Account")
    create_login_window.geometry("800x300+350+200")
    create_login_window.configure(bg="black")  # Dark background

    Label(create_login_window, text="Create New Account", font=('Georgia', 16, 'bold'), bg="black", fg="white").pack(pady=10)

    # Username label and entry
    Label(create_login_window, text="Username:", font=('Georgia', 14), bg="black", fg="white").pack(pady=5)
    c_username_entry = Entry(create_login_window, font=('Georgia', 14), bg="#CCCCCC", fg="black")
    c_username_entry.pack(pady=5)

    # Password label and entry
    Label(create_login_window, text="Password:", font=('Georgia', 14), bg="black", fg="white").pack(pady=5)
    c_password_entry = Entry(create_login_window, show="*", font=('Georgia', 14), bg="#CCCCCC", fg="black")
    c_password_entry.pack(pady=5)

    # Create Account button
    create_account_button = Button(create_login_window, text="Create Account", command=create_account, font=('Georgia', 14, 'bold'), bg="#8ED1FC", fg="black", width=15)
    create_account_button.pack(pady=20)

def show_login_window():
    # Displays the login window
    global login_window, username_entry, password_entry
    login_window = Tk()
    login_window.title("Pharmacy Management System Login")
    login_window.geometry("800x400+350+200")
    login_window.configure(bg="black")  # Dark background

    Label(login_window, text="Login", font=('Georgia', 17, 'bold'), bg="black", fg="white").pack(pady=10)

    # Username label and entry
    Label(login_window, text="Username:", font=('Georgia', 14), bg="black", fg="white").pack(pady=5)
    username_entry = Entry(login_window, font=('Georgia', 14), bg="#CCCCCC", fg="black")
    username_entry.pack(pady=5)

    # Password label and entry
    Label(login_window, text="Password:", font=('Georgia', 14), bg="black", fg="white").pack(pady=5)
    password_entry = Entry(login_window, show="*", font=('Georgia', 14), bg="#CCCCCC", fg="black")
    password_entry.pack(pady=5)

    # Login button
    login_button = Button(login_window, text="Login", command=login, font=('Georgia', 14, 'bold'), bg="#8ED1FC", fg="black", width=15)
    login_button.place(relx=0.5, rely=0.65, anchor='center')

    # Create Account button
    create_account_button = Button(login_window, text="Create Account", command=show_create_login_window, font=('Georgia', 14, 'bold'), bg="#8ED1FC", fg="black", width=15)
    create_account_button.place(relx=0.5, rely=0.80, anchor='center')

    login_window.mainloop()

show_login_window()