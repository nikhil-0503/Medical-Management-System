from tkinter import * 
from tkinter import messagebox,ttk,Tk, Frame, Label, ttk, Scrollbar, VERTICAL, HORIZONTAL
from PIL import Image, ImageTk
from customtkinter import *
import cx_Oracle

#Establishing Oracle SQL Connectivity
class DatabaseManager:
    def __init__(self):
        try:
            self.connection = cx_Oracle.connect(mode=cx_Oracle.SYSDBA)
            self.cursor = self.connection.cursor()
            print("Database connection established successfully.")
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

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

#Creating object for Database to Python link
dbms = DatabaseManager()

#Viewing records in supplier
def checkbysupplier():
     # Create a tkinter window for viewing records in the supplier table
    root18 = Tk()
    root18.geometry('1000x700')  # Set window size
    root18.title('Checking Medicines in Supplier Page')  # Set window title
    root18.resizable(0, 0)  # Disable window resizing
    root18.config(bg='gray')  # Set background color

    # Create top frame for displaying the title
    Topframe = Frame(root18, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)
    Introtext = Label(Topframe, text='Viewing Supplier Table', font=('Georgia', 24, 'bold'),bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=0, width=900)
    DetailsFrame = Frame(root18, bg='black', width=1000, height=540)
    DetailsFrame.place(x=0, y=120)

    records = dbms.fetch_query("SELECT * FROM SUPPLIER")

    style = ttk.Style()
    style.configure("Treeview", font=("Georgia", 11))  
    style.configure("Treeview.Heading", font=("Georgia", 12, "bold"))  

    columns = ("Supplier ID", "Supplier Name", "Contact", "Email", "Address")
    tree = ttk.Treeview(DetailsFrame, columns=columns, show="headings", style="Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=1000 // len(columns), anchor="center")  
    tree.place(x=0, y=30, width=980, height=480)

    v_scroll = Scrollbar(DetailsFrame, orient=VERTICAL, command=tree.yview)
    h_scroll = Scrollbar(DetailsFrame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.place(x=980, y=30, height=480)
    h_scroll.place(x=0, y=480, width=980)

    for record in records:
        tree.insert("", "end", values=record)
    
    #Function when back button is pressed
    def backpage():
        root18.destroy()
        check_medicine()

    #Button for going back to previous page
    backbutton = Button(root18,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root18.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root18,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root18.mainloop()

#Viewing records in medicine
def checkbymedicine():
    #Create a tkinter page for viewing records in medicine page
    root19 = Tk()
    root19.geometry('1000x700') #Set window size
    root19.title('Checking Medicines in Medicine Page') #Set window title
    root19.resizable(0,0) # Disable window resizing
    root19.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root19, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Medicine Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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
    backbutton = Button(root19,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root19.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root19,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root19.mainloop()

#Viewing records in customer
def checkbycustomer():
    #Create a tkinter page for viewing records in customer page
    root20 = Tk()
    root20.geometry('1000x700') #Set window size
    root20.title('Checking Medicines in Customer Page') #Set window title
    root20.resizable(0,0) # Disable window resizing
    root20.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root20, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Customer Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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
    root21.geometry('1000x700') #Set window size
    root21.title('Checking Medicines in Prescription Page') #Set window title
    root21.resizable(0,0) # Disable window resizing
    root21.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root21, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Prescription Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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
    root22.geometry('1000x700') #Set window size
    root22.title('Checking Medicines in Sales Page') #Set window title
    root22.resizable(0,0) # Disable window resizing
    root22.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root22, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Sales Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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
    root23.geometry('1000x700') #Set window size
    root23.title('Checking Medicines in Sales Items Page') #Set window title
    root23.resizable(0,0) # Disable window resizing
    root23.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root23, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Viewing Sales Items Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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

#Checking the medicines available
def check_medicine():
    #Create a tkinter page for the check medicine page
    root2 = Tk()
    root2.geometry('1000x700') #Set window size
    root2.title('Check Medicine Page') #Set window title
    root2.resizable(0,0) # Disable window resizing
    root2.config(bg='gray') #Set background colour

    #Function when back home button is pressed
    def backtohome():
        root2.destroy()
        introscreen()
    
    #Create top frame for displaying title
    Topframe = Frame(root2, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Check table for',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    ButtonsFrame = Frame(root2,bg='black',width=520,height=500)
    ButtonsFrame.place(x=240,y=150)

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
    prescription_button = Button(ButtonsFrame,text='Prescription',command=check_prescription,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    prescription_button.place(x=150,y=265,width=220)

    #Button for inserting medicine by sales
    sales_button = Button(ButtonsFrame,text='Sales',command=check_sales,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    sales_button.place(x=150,y=340,width=220)

    #Button for inserting medicine by sales
    salesitems_button = Button(ButtonsFrame,text='Sales Items',command=check_sales_items,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    salesitems_button.place(x=150,y=415,width=220)

    #Button for going back to home page
    home_page_button = Button(root2,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root2.mainloop()

#Inserting in supplier
def insertbysupplier():
    #Create a tkinter page for the insert in supplier page
    root6 = Tk()
    root6.geometry('1000x700') #Set window size
    root6.title('Insert in Supplier Page') #Set window title
    root6.resizable(0,0) # Disable window resizing
    root6.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root6, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Supplier Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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
        se = sidentry.get()
        sne = snameentry.get()
        ne = numberentry.get()
        ee = emailentry.get()
        ae = addressentry.get()

        if se == '' or sne == '' or ne == '' or ee == '' or ae == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
        elif len(ne) > 10 or len(ne) < 10 or str(ne)[0] == '0':
            messagebox.showerror('Error!', 'Enter a valid mobile number.')
            resetfield()
        else:
            query = "SELECT supplier_id FROM SUPPLIER WHERE supplier_id = :1"
            params = (se,)
            c = dbms.fetch_query(query, params)
            
            if c:
                # Display an error message if the supplier ID already exists
                messagebox.showerror('Insert Error!', f'Supplier ID {se} already exists!')
                resetfield()
            else:
                # Only insert if no duplicates are found
                query = "INSERT INTO SUPPLIER (supplier_id, s_name, contact_number, email, address) VALUES (:1, :2, :3, :4, :5)"
                params = (se, sne, ne, ee, ae)
                dbms.execute_query(query, params)
                dbms.execute_query("COMMIT")
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
    #Create a tkinter page for the insert in medicine page
    root7 = Tk()
    root7.geometry('1000x700') #Set window size
    root7.title('Insert in Medicine Page') #Set window title
    root7.resizable(0,0) # Disable window resizing
    root7.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root7, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Medicine Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root7,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

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
        global me, mne, bre, be, ee, qe, pe, se
        me = midentry.get()  # Medicine ID
        mne = mnameentry.get()  # Medicine Name
        bre = brandentry.get()  # Brand
        be = batchnoentry.get()  # Batch Number
        ee = expdateentry.get()  # Expiry Date
        qe = qtyentry.get()  # Quantity
        pe = priceentry.get()  # Price
        se = sidentry.get()  # Supplier ID

        # Check if all fields are filled
        if me == '' or mne == '' or bre == '' or be == '' or ee == '' or qe == '' or pe == '' or se == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
        else:
            # Check if the medicine ID already exists
            query = "SELECT medicine_id FROM MEDICINE WHERE medicine_id = :1"
            params = (me,)
            c = dbms.fetch_query(query, params)

            if c:
                # Display an error message if the medicine ID already exists
                messagebox.showerror('Insert Error!', f'Medicine ID {me} already exists!')
                resetfield()
            else:
                # Only insert if no duplicates are found
                query = "INSERT INTO MEDICINE (medicine_id, m_name, brand, batch_number, expiry_date, quantity, price, supplier_id) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)"
                params = (me, mne, bre, be, ee, qe, pe, se)
                dbms.execute_query(query, params)
                dbms.execute_query("COMMIT")
                messagebox.showinfo('Success!', 'Record inserted successfully into Medicine Table!')
                resetfield()

    # Labels and entry fields for inserting data by medicine
    midtext = Label(DetailsFrame, text='Medicine ID', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    midtext.place(x=20, y=50)
    mnametext = Label(DetailsFrame, text='Medicine Name', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    mnametext.place(x=20, y=130)
    brandtext = Label(DetailsFrame, text='Brand', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    brandtext.place(x=20, y=210)
    batchnotext = Label(DetailsFrame, text='Batch Number', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    batchnotext.place(x=20, y=290)
    expdatetext = Label(DetailsFrame, text='Expiry Date', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    expdatetext.place(x=450, y=50)
    qtytext = Label(DetailsFrame, text='Quantity', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    qtytext.place(x=450, y=130)
    pricetext = Label(DetailsFrame, text='Price', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    pricetext.place(x=450, y=210)
    sidtext = Label(DetailsFrame, text='Supplier ID', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
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


    EnterButton = Button(DetailsFrame,text='Enter',command=insertdetails,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    EnterButton.place(x=150,y=440,width=220)

    #Function when back button is pressed
    def backpage():
        root7.destroy()
        insert_medicine()

    #Button for going back to previous page
    backbutton = Button(root7,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root7.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root7,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root7.mainloop()

#Inserting in customer
def insertbycustomer():
    #Create a tkinter page for the insert in customer page
    root8 = Tk()
    root8.geometry('1000x700') #Set window size
    root8.title('Insert in Customer Page') #Set window title
    root8.resizable(0,0) # Disable window resizing
    root8.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root8, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Customer Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root8,bg='black',width=520,height=520)
    DetailsFrame.place(x=240,y=150)

    def resetfield():
        cidentry.delete(0, END)
        cnameentry.delete(0, END)
        numberentry.delete(0, END)
        emailentry.delete(0, END)
        addressentry.delete(0, END)

    def insertdetails():
        global ce, cne, ne, ee, ae
        ce = cidentry.get()  # Customer ID
        cne = cnameentry.get()  # Customer Name
        ne = numberentry.get()  # Contact Number
        ee = emailentry.get()  # Email
        ae = addressentry.get()  # Address

        # Check if all fields are filled
        if ce == '' or cne == '' or ne == '' or ee == '' or ae == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
        elif len(ne) > 10 or len(ne) < 10 or str(ne)[0] == '0':
            messagebox.showerror('Error!', 'Enter a valid mobile number.')
            resetfield()
        else:
            # Check if the customer ID already exists
            query = "SELECT customer_id FROM CUSTOMER WHERE customer_id = :1"
            params = (ce,)
            c = dbms.fetch_query(query, params)

            if c:
                # Display an error message if the customer ID already exists
                messagebox.showerror('Insert Error!', f'Customer ID {ce} already exists!')
                resetfield()
            else:
                # Only insert if no duplicates are found
                query = "INSERT INTO CUSTOMER (customer_id, c_name, contact_number, email, address) VALUES (:1, :2, :3, :4, :5)"
                params = (ce, cne, ne, ee, ae)
                dbms.execute_query(query, params)
                dbms.execute_query("COMMIT")
                messagebox.showinfo('Success!', 'Record inserted successfully into Customer Table!')
                resetfield()


    # Labels and entry fields for inserting data by customer
    cidtext = Label(DetailsFrame, text='Customer ID', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    cidtext.place(x=20, y=50)
    cnametext = Label(DetailsFrame, text='Customer Name', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    cnametext.place(x=20, y=130)
    numbertext = Label(DetailsFrame, text='Contact Number', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    numbertext.place(x=20, y=210)
    emailtext = Label(DetailsFrame, text='Email', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    emailtext.place(x=20, y=290)
    addresstext = Label(DetailsFrame, text='Address', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    addresstext.place(x=20, y=370)

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

    EnterButton = Button(DetailsFrame,text='Enter',command=insertdetails,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    EnterButton.place(x=150,y=440,width=220)

    #Function when back button is pressed
    def backpage():
        root8.destroy()
        insert_medicine()

    #Button for going back to previous page
    backbutton = Button(root8,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root8.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root8,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root8.mainloop()

#Inserting in prescription
def insertbyprescription():
    #Create a tkinter page for the insert in prescription page
    root9 = Tk()
    root9.geometry('1000x700') #Set window size
    root9.title('Insert in Prescription Page') #Set window title
    root9.resizable(0,0) # Disable window resizing
    root9.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root9, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Prescription Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root9,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

    def resetfield():
        pidentry.delete(0, END)
        cidentry.delete(0, END)
        docnameentry.delete(0, END)
        dateentry.delete(0, END)
        dosageentry.delete(0, END)
        freqentry.delete(0, END)
        durationentry.delete(0, END)
        addinentry.delete(0, END)

    def insertdetails():
        global pe, ce, dne, pde, doe, fe, due, ae
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
        else:
            # Check if the prescription ID already exists
            query = "SELECT prescription_id FROM PRESCRIPTION WHERE prescription_id = :1"
            params = (pe,)
            c = dbms.fetch_query(query, params)

            if c:
                # Display an error message if the prescription ID already exists
                messagebox.showerror('Insert Error!', f'Prescription ID {pe} already exists!')
                resetfield()
            else:
                # Only insert if no duplicates are found
                query = "INSERT INTO PRESCRIPTION (prescription_id, customer_id, doctor_name, prescription_date, dosage, frequency, duration, additional_instructions) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)"
                params = (pe, ce, dne, pde, doe, fe, due, ae)
                dbms.execute_query(query, params)
                dbms.execute_query("COMMIT")
                messagebox.showinfo('Success!', 'Record inserted successfully into Prescription Table!')
                resetfield()


    # Labels and entry fields for inserting data by prescription
    pidtext = Label(DetailsFrame, text='Prescription ID', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    pidtext.place(x=20, y=50)
    cidtext = Label(DetailsFrame, text='Customer ID', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    cidtext.place(x=20, y=130)
    docnametext = Label(DetailsFrame, text='Doctor Name', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    docnametext.place(x=20, y=210)
    datetext = Label(DetailsFrame, text='Prescription Date', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    datetext.place(x=20, y=290)
    dosagetext = Label(DetailsFrame, text='Dosage', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    dosagetext.place(x=450, y=50)
    freqtext = Label(DetailsFrame, text='Frequency', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    freqtext.place(x=450, y=130)
    durationtext = Label(DetailsFrame, text='Duration', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    durationtext.place(x=450, y=210)
    addintext = Label(DetailsFrame, text='Additional Instructions', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    addintext.place(x=450, y=290)


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


    EnterButton = Button(DetailsFrame,text='Enter',command=insertdetails,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    EnterButton.place(x=150,y=440,width=220)

    #Function when back button is pressed
    def backpage():
        root9.destroy()
        insert_medicine()

    #Button for going back to previous page
    backbutton = Button(root9,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root9.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root9,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root9.mainloop()

#Inserting in sales
def insertbysales():
    #Create a tkinter page for the insert in sales page
    root10 = Tk()
    root10.geometry('1000x700') #Set window size
    root10.title('Insert in Sales Page') #Set window title
    root10.resizable(0,0) # Disable window resizing
    root10.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root10, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Sales Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root10,bg='black',width=520,height=520)
    DetailsFrame.place(x=240,y=150)

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

        # Check if all fields are filled
        if se == '' or ce == '' or sde == '' or te == '' or pe == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
        else:
            # Check if the sale ID already exists
            query = "SELECT sale_id FROM SALES WHERE sale_id = :1"
            params = (se,)
            c = dbms.fetch_query(query, params)

            if c:
                # Display an error message if the sale ID already exists
                messagebox.showerror('Insert Error!', f'Sale ID {se} already exists!')
                resetfield()
            else:
                # Only insert if no duplicates are found
                query = "INSERT INTO SALES (sale_id, customer_id, sale_date, total_amount, payment_method) VALUES (:1, :2, :3, :4, :5)"
                params = (se, ce, sde, te, pe)
                dbms.execute_query(query, params)
                dbms.execute_query("COMMIT")
                messagebox.showinfo('Success!', 'Record inserted successfully into Sales Table!')
                resetfield()

    # Labels and entry fields for inserting data by sales
    sidtext = Label(DetailsFrame, text='Sale ID', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    sidtext.place(x=20, y=50)
    cidtext = Label(DetailsFrame, text='Customer ID', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    cidtext.place(x=20, y=130)
    sdatetext = Label(DetailsFrame, text='Sale Date', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    sdatetext.place(x=20, y=210)
    totamttext = Label(DetailsFrame, text='Total Amount', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    totamttext.place(x=20, y=290)
    paytext = Label(DetailsFrame, text='Payment Method', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    paytext.place(x=20, y=370)

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

    EnterButton = Button(DetailsFrame,text='Enter',command=insertdetails,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    EnterButton.place(x=150,y=440,width=220)

    #Function when back button is pressed
    def backpage():
        root10.destroy()
        insert_medicine()

    #Button for going back to previous page
    backbutton = Button(root10,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root10.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root10,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root10.mainloop()

#Inserting in sales items
def insertbysalesitems():
    #Create a tkinter page for the insert in sales items page
    root11 = Tk()
    root11.geometry('1000x700') #Set window size
    root11.title('Insert in Sales Items Page') #Set window title
    root11.resizable(0,0) # Disable window resizing
    root11.config(bg='gray') #Set background colour

    #Create top frame for displaying title
    Topframe = Frame(root11, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert into Sales Items Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root11,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

    def resetfield():
        saidentry.delete(0, END)
        sidentry.delete(0, END)
        midentry.delete(0, END)
        qtyentry.delete(0, END)
        priceentry.delete(0, END)

    def insertdetails():
        global sie, se, me, qe, pe, ste
        sie = saidentry.get()  # Sale Item ID
        se = sidentry.get()    # Sale ID
        me = midentry.get()    # Medicine ID
        qe = qtyentry.get()     # Quantity
        pe = priceentry.get()   # Price per unit
        ste = int(qe) * int(pe)  # Subtotal

        # Check if all fields are filled
        if sie == '' or se == '' or me == '' or qe == '' or pe == '':
            messagebox.showerror('Error!', 'Enter all the required values.')
            resetfield()
        else:
            # Check if the sale_item_id already exists
            query = "SELECT sale_item_id FROM SALES_ITEMS WHERE sale_item_id = :1"
            params = (sie,)
            c = dbms.fetch_query(query, params)

            if c:  # If the query returns any results, the sale_item_id exists
                messagebox.showerror('Insert Error!', f'Sale Item ID {sie} already exists!')
                resetfield()
            else:
                # Only insert if no duplicates are found
                query = "INSERT INTO SALES_ITEMS (sale_item_id, sale_id, medicine_id, quantity, price_per_unit, subtotal) VALUES (:1, :2, :3, :4, :5, :6)"
                params = (sie, se, me, qe, pe, ste)
                dbms.execute_query(query, params)
                dbms.execute_query("COMMIT")
                messagebox.showinfo('Success!', 'Record inserted successfully into Sales Items Table!')
                resetfield()

    # Labels and entry fields for inserting data by sales items
    saidtext = Label(DetailsFrame, text='Sale Item ID', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    saidtext.place(x=20, y=50)
    sidtext = Label(DetailsFrame, text='Sale ID', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    sidtext.place(x=20, y=130)
    midtext = Label(DetailsFrame, text='Medicine ID', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    midtext.place(x=20, y=210)
    qtytext = Label(DetailsFrame, text='Quantity', font=('Georgia', 18, 'bold', 'italic')
                     , bg='black', fg='white', activebackground='black')
    qtytext.place(x=450, y=50)
    pricetext = Label(DetailsFrame, text='Price Per Unit', font=('Georgia', 18, 'bold', 'italic')
                      , bg='black', fg='white', activebackground='black')
    pricetext.place(x=450, y=130)

    saidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='white')
    saidentry.place(x=20, y=80, width=350)
    sidentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='white')
    sidentry.place(x=20, y=160, width=350)
    midentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='white')
    midentry.place(x=20, y=240, width=350)
    qtyentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='white')
    qtyentry.place(x=450, y=80, width=350)
    priceentry = Entry(DetailsFrame, font=("Georgia", 16, 'bold'), bg='white', fg='white')
    priceentry.place(x=450, y=160, width=350)
    

    EnterButton = Button(DetailsFrame,text='Enter',command=insertdetails,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    EnterButton.place(x=150,y=440,width=220)

    #Function when back button is pressed
    def backpage():
        root11.destroy()
        insert_medicine()

    #Button for going back to previous page
    backbutton = Button(root11,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root11.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root11,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root11.mainloop()

#Inserting a medicine
def insert_medicine():
    #Create a tkinter page for the insert medicine page
    root3 = Tk()
    root3.geometry('1000x700') #Set window size
    root3.title('Insert Medicine Page') #Set window title
    root3.resizable(0,0) # Disable window resizing
    root3.config(bg='gray') #Set background colour

    #Function when back home button is pressed
    def backtohome():
        root3.destroy()
        introscreen()
    
    #Create top frame for displaying title
    Topframe = Frame(root3, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Insert by',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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
    root12.geometry('1000x700')
    root12.title('Update Supplier Page')
    root12.resizable(0, 0)
    root12.config(bg='gray')

    def reset_fields():
        sidentry.delete(0, END)
        snameentry.delete(0, END)
        numberentry.delete(0, END)
        emailentry.delete(0, END)
        addressentry.delete(0, END)

    def update_supplier_details():
        sid = sidentry.get()  # Supplier ID (primary key for identification)
        sname = snameentry.get()  # Supplier Name
        contact_number = numberentry.get()  # Contact Number
        email = emailentry.get()  # Email
        address = addressentry.get()  # Address

        if sid == '':
            messagebox.showerror('Error!', 'Please enter a valid Supplier ID to update.')
            reset_fields()
        elif not (sname and contact_number and email and address):
            messagebox.showerror('Error!', 'Please fill in all fields to update the supplier record.')
            reset_fields()
        elif len(contact_number) != 10 or not contact_number.isdigit():
            messagebox.showerror('Error!', 'Please enter a valid 10-digit contact number.')
            reset_fields()
        else:
            try:
                query = """
                    UPDATE SUPPLIER
                    SET s_name=:1, contact_number=:2, email=:3, address=:4
                    WHERE supplier_id=:5
                """
                params = (sname, contact_number, email, address, sid)
                dbms.execute_query(query, params)
                messagebox.showinfo('Success!', f'Supplier ID {sid} updated successfully.')
                reset_fields()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                reset_fields()
            
    #Create top frame for displaying title
    Topframe = Frame(root12, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Update into Supplier Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root12,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

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
                           font=('Georgia', 16), bg='light blue', fg='black', width=20)
    update_button.place(x=250, y=350)

    #Function when back button is pressed
    def backpage():
        root12.destroy()
        update_medicine()

    #Button for going back to previous page
    backbutton = Button(root12,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root12.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root12,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root12.mainloop()

#updating in medicine
def updatebymedicine():
    root13 = Tk()
    root13.geometry('1000x700')
    root13.title('Update Medicine Page')
    root13.resizable(0, 0)
    root13.config(bg='gray')

    def reset_fields():
        midentry.delete(0, END)
        mnameentry.delete(0, END)
        brandentry.delete(0, END)
        batchnoentry.delete(0, END)
        expdateentry.delete(0, END)
        qtyentry.delete(0, END)
        priceentry.delete(0, END)
        sidentry.delete(0, END)

    def update_medicine_details():
        me = midentry.get()  # Medicine ID (primary key for identification)
        mne = mnameentry.get()  # Medicine Name
        bre = brandentry.get()  # Brand
        be = batchnoentry.get()  # Batch Number
        ee = expdateentry.get()  # Expiry Date
        qe = qtyentry.get()  # Quantity
        pe = priceentry.get()  # Price
        se = sidentry.get()  # Supplier ID

        if me == '':
            messagebox.showerror('Error!', 'Please enter a valid Medicine ID to update.')
            reset_fields()
        elif not (mne and bre and be and ee and qe and pe and se):
            messagebox.showerror('Error!', 'Please fill in all fields for updating the medicine details.')
            reset_fields()
        else:
            try:
                query = """
                    UPDATE MEDICINE 
                    SET m_name=:1, brand=:2, batch_number=:3, expiry_date=:4, quantity=:5, price=:6, supplier_id=:7 
                    WHERE medicine_id=:8
                """
                params = (mne, bre, be, ee, qe, pe, se, me)
                dbms.execute_query(query, params)
                messagebox.showinfo('Success!', f'Medicine ID {me} updated successfully.')
                reset_fields()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                reset_fields()
            
    #Create top frame for displaying title
    Topframe = Frame(root13, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Update into Medicine Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root13,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

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
                           font=('Georgia', 16), bg='light blue', fg='black', width=20)
    update_button.place(x=250, y=500)

    #Function when back button is pressed
    def backpage():
        root13.destroy()
        update_medicine()

    #Button for going back to previous page
    backbutton = Button(root13,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root13.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root13,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root13.mainloop()

#Updating in customer
def updatebycustomer():
    root14 = Tk()
    root14.geometry('1000x700')
    root14.title('Update Customer Page')
    root14.resizable(0, 0)
    root14.config(bg='gray')

    def reset_fields():
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

        if cid == '':
            messagebox.showerror('Error!', 'Please enter a valid Customer ID to update.')
            reset_fields()
        elif not (cname and contact_number and email and address):
            messagebox.showerror('Error!', 'Please fill in all fields to update the customer record.')
            reset_fields()
        elif len(contact_number) != 10 or not contact_number.isdigit():
            messagebox.showerror('Error!', 'Please enter a valid 10-digit contact number.')
            reset_fields()
        else:
            try:
                query = """
                    UPDATE CUSTOMER
                    SET c_name=:1, contact_number=:2, email=:3, address=:4
                    WHERE customer_id=:5
                """
                params = (cname, contact_number, email, address, cid)
                dbms.execute_query(query, params)
                messagebox.showinfo('Success!', f'Customer ID {cid} updated successfully.')
                reset_fields()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                reset_fields()
            
    #Create top frame for displaying title
    Topframe = Frame(root14, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Update into Customer Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root14,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

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
                           font=('Georgia', 16), bg='light blue', fg='black', width=20)
    update_button.place(x=250, y=350)

    #Function when back button is pressed
    def backpage():
        root14.destroy()
        update_medicine()

    #Button for going back to previous page
    backbutton = Button(root14,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root14.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root14,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root14.mainloop()

#Updating in prescription
def updatebyprescription():
    root15 = Tk()
    root15.geometry('1000x700')
    root15.title('Update Prescription Page')
    root15.resizable(0, 0)
    root15.config(bg='gray')

    def reset_fields():
        pidentry.delete(0, END)
        cidentry.delete(0, END)
        docnameentry.delete(0, END)
        dateentry.delete(0, END)
        dosageentry.delete(0, END)
        freqentry.delete(0, END)
        durationentry.delete(0, END)
        addinentry.delete(0, END)

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
            reset_fields()
        elif not (ce and dne and pde and doe and fe and due and ae):
            messagebox.showerror('Error!', 'Please fill in all fields to update the prescription.')
            reset_fields()
        else:
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
                reset_fields()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                reset_fields()
    
    #Create top frame for displaying title
    Topframe = Frame(root15, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Update into Prescription Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root15,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

    # Create entry fields and labels for the prescription update form
    Label(DetailsFrame, text='Prescription ID', font=('Georgia', 14),fg='white', bg='black').place(x=160, y=50)
    pidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    pidentry.place(x=395, y=50)

    Label(DetailsFrame, text='New Customer ID', font=('Georgia', 14),fg='white', bg='black').place(x=160, y=100)
    cidentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    cidentry.place(x=395, y=100)

    Label(DetailsFrame, text='New Doctor Name', font=('Georgia', 14),fg='white', bg='black').place(x=160, y=150)
    docnameentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    docnameentry.place(x=395, y=150)

    Label(DetailsFrame, text='New Prescription Date', font=('Georgia', 14),fg='white', bg='black').place(x=160, y=200)
    dateentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    dateentry.place(x=395, y=200)

    Label(DetailsFrame, text='New Dosage', font=('Georgia', 14),fg='white', bg='black').place(x=160, y=250)
    dosageentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    dosageentry.place(x=395, y=250)

    Label(DetailsFrame, text='New Frequency', font=('Georgia', 14),fg='white', bg='black').place(x=160, y=300)
    freqentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    freqentry.place(x=395, y=300)

    Label(DetailsFrame, text='New Duration', font=('Georgia', 14),fg='white', bg='black').place(x=160, y=350)
    durationentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    durationentry.place(x=395, y=350)

    Label(DetailsFrame, text='New Additional Instructions', font=('Georgia', 14),fg='white', bg='black').place(x=160, y=400)
    addinentry = Entry(DetailsFrame, font=('Georgia', 14), width=30)
    addinentry.place(x=395, y=400)

    # Button to trigger the update operation
    update_button = Button(DetailsFrame, text='Update Prescription', command=update_prescription_details,
                           font=('Georgia', 16), bg='light blue', fg='black', width=20)
    update_button.place(x=250, y=500)

    #Function when back button is pressed
    def backpage():
        root15.destroy()
        update_medicine()

    #Button for going back to previous page
    backbutton = Button(root15,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root15.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root15,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root15.mainloop()

#Updating in sales
def updatebysales():
    root16 = Tk()
    root16.geometry('1000x700')
    root16.title('Update Sales Page')
    root16.resizable(0, 0)
    root16.config(bg='gray')

    def reset_fields():
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

        if sid == '':
            messagebox.showerror('Error!', 'Please enter a valid Sale ID to update.')
            reset_fields()
        elif not (cid and sdate and total_amt and payment_method):
            messagebox.showerror('Error!', 'Please fill in all fields to update the sale record.')
            reset_fields()
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
                reset_fields()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                reset_fields()
            
    #Create top frame for displaying title
    Topframe = Frame(root16, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Update into Sales Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root16,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

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
    update_button = Button(DetailsFrame, text='Update Sales', command=update_sales_details,
                           font=('Georgia', 16), bg='light blue', fg='black', width=20)
    update_button.place(x=250, y=350)

    #Function when back button is pressed
    def backpage():
        root16.destroy()
        update_medicine()

    #Button for going back to previous page
    backbutton = Button(root16,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root16.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root16,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root16.mainloop()

#Updating in sales items
def updatebysalesitems():
    root17 = Tk()
    root17.geometry('1000x700')
    root17.title('Update Sales Items Page')
    root17.resizable(0, 0)
    root17.config(bg='gray')

    def reset_fields():
        saidentry.delete(0, END)
        sidentry.delete(0, END)
        midentry.delete(0, END)
        qtyentry.delete(0, END)
        priceentry.delete(0, END)

    def update_sales_items_details():
        sale_item_id = saidentry.get()  # Sale Item ID (primary key for identification)
        sale_id = sidentry.get()  # Sale ID
        medicine_id = midentry.get()  # Medicine ID
        quantity = qtyentry.get()  # Quantity
        price_per_unit = priceentry.get()  # Price Per Unit

        if sale_item_id == '':
            messagebox.showerror('Error!', 'Please enter a valid Sale Item ID to update.')
            reset_fields()
        elif not (sale_id and medicine_id and quantity and price_per_unit):
            messagebox.showerror('Error!', 'Please fill in all fields to update the sales item record.')
            reset_fields()
        else:
            try:
                subtotal = int(quantity) * float(price_per_unit)  # Calculate subtotal
                query = """
                    UPDATE SALES_ITEMS
                    SET sale_id=:1, medicine_id=:2, quantity=:3, price_per_unit=:4, subtotal=:5
                    WHERE sale_item_id=:6
                """
                params = (sale_id, medicine_id, quantity, price_per_unit, subtotal, sale_item_id)
                dbms.execute_query(query, params)
                messagebox.showinfo('Success!', f'Sale Item ID {sale_item_id} updated successfully.')
                reset_fields()
            except Exception as e:
                messagebox.showerror('Update Failed', str(e))
                reset_fields()
            
    #Create top frame for displaying title
    Topframe = Frame(root17, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Update into Sales Items Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

    DetailsFrame = Frame(root17,bg='black',width=820,height=520)
    DetailsFrame.place(x=90,y=150)

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
                           font=('Georgia', 16), bg='light blue', fg='black', width=20)
    update_button.place(relx=0.5, y=400, anchor='center')

    #Function when back button is pressed
    def backpage():
        root17.destroy()
        update_medicine()

    #Button for going back to previous page
    backbutton = Button(root17,text='Back',command=backpage,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    backbutton.place(x=20,y=25,width=220)

    #Function when back home button is pressed
    def backtohome():
        root17.destroy()
        introscreen()

    #Button for going back to home page
    home_page_button = Button(root17,text='Back to home',command=backtohome,font=('Georgia',18,'bold'),
                              cursor='hand2',bd=0,bg='light blue',fg='black',activebackground='light blue')
    home_page_button.place(x=760,y=25,width=220)

    root17.mainloop()

#Updating a medicine
def update_medicine():
    #Create a tkinter page for the update medicine page
    root4 = Tk()
    root4.geometry('1000x700') #Set window size
    root4.title('Update Medicine Page') #Set window title
    root4.resizable(0,0) # Disable window resizing
    root4.config(bg='gray') #Set background colour

    #Function when back home button is pressed
    def backtohome():
        root4.destroy()
        introscreen()
    
    #Create top frame for displaying title
    Topframe = Frame(root4, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Update by',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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

    def delete_supplier():
        sid = sidentry.get()
        if sid == '':
            messagebox.showerror('Error!', 'Please enter a Supplier ID to delete.')
        else:
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
    Introtext = Label(Topframe, text='Delete from Supplier Table',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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

    def delete_medicine():
        mid = midentry.get()  # Get the medicine_id from the entry field
        if mid == '':
            messagebox.showerror('Error!', 'Please enter a Medicine ID to delete.')
        else:
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
    Introtext = Label(Topframe, text='Delete from Medicine Table', font=('Georgia', 24, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=0, width=900)

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

    def delete_customer():
        cid = cidentry.get()  # Get the customer_id from the entry field
        if cid == '':
            messagebox.showerror('Error!', 'Please enter a Customer ID to delete.')
        else:
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
    Introtext = Label(Topframe, text='Delete from Customer Table', font=('Georgia', 24, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=0, width=900)

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

    def delete_prescription():
        pid = pidentry.get()  # Get the prescription_id from the entry field
        if pid == '':
            messagebox.showerror('Error!', 'Please enter a Prescription ID to delete.')
        else:
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
    Introtext = Label(Topframe, text='Delete from Prescription Table', font=('Georgia', 24, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=0, width=900)

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

    def delete_sale():
        sale_id = saleidentry.get()  # Get the sale_id from the entry field
        if sale_id == '':
            messagebox.showerror('Error!', 'Please enter a Sale ID to delete.')
        else:
            try:
                query = "DELETE FROM SALES WHERE sale_id = :1"
                dbms.execute_query(query, (sale_id,))
                messagebox.showinfo('Success!', f'Sale ID {sale_id} deleted successfully.')
                saleidentry.delete(0, END)
            except Exception as e:
                messagebox.showerror('Delete Failed', str(e))

    # Create top frame for displaying title
    Topframe = Frame(root_del_sales, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Delete from Sales Table', font=('Georgia', 24, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=0, width=900)

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
def deletebysaleitems():
    root_del_saleitems = Tk()
    root_del_saleitems.geometry('1000x525')
    root_del_saleitems.title('Delete Sale Item')
    root_del_saleitems.resizable(0, 0)
    root_del_saleitems.config(bg='gray')

    def delete_sale_item():
        sale_item_id = saleitemidentry.get()  # Get the sale_item_id from the entry field
        if sale_item_id == '':
            messagebox.showerror('Error!', 'Please enter a Sale Item ID to delete.')
        else:
            try:
                query = "DELETE FROM SALES_ITEMS WHERE sale_item_id = :1"
                dbms.execute_query(query, (sale_item_id,))
                messagebox.showinfo('Success!', f'Sale Item ID {sale_item_id} deleted successfully.')
                saleitemidentry.delete(0, END)
            except Exception as e:
                messagebox.showerror('Delete Failed', str(e))

    # Create top frame for displaying title
    Topframe = Frame(root_del_saleitems, bg='black', width=1000, height=100)
    Topframe.place(x=0, y=0)

    # Title text for the introduction
    Introtext = Label(Topframe, text='Delete from Sales Items Table', font=('Georgia', 24, 'bold'), bg='black', fg='white', activebackground='black')
    Introtext.place(x=50, y=0, width=900)

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
    root5.geometry('1000x700') #Set window size
    root5.title('Delete Medicine Page') #Set window title
    root5.resizable(0,0) # Disable window resizing
    root5.config(bg='gray') #Set background colour

    #Function when back home button is pressed
    def backtohome():
        root5.destroy()
        introscreen()
    
    #Create top frame for displaying title
    Topframe = Frame(root5, bg='black',width=1000, height=100)
    Topframe.place(x=0,y=0)

    #Title text for the introduction
    Introtext = Label(Topframe, text='Delete by',font=('Georgia',24,'bold'),bg='black',fg='white',activebackground='black')
    Introtext.place(x=50,y=0,width=900)

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
    root1.geometry('1000x700') #Set window size
    root1.title('Home Page') #Set window title
    root1.resizable(0,0) # Disable window resizing
    root1.config(bg='gray') #Set background colour
    
    bgimg = Image.open('bgpic.jpg')
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

    root1.mainloop()

introscreen()