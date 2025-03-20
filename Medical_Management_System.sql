REM Medical Management System Database

SET ECHO ON;

DROP TABLE IF EXISTS SALES_ITEMS;
DROP TABLE IF EXISTS SALES;
DROP TABLE IF EXISTS PRESCRIPTION;
DROP TABLE IF EXISTS MEDICINE;
DROP TABLE IF EXISTS SUPPLIER;
DROP TABLE IF EXISTS CUSTOMER cascade constraints;

REM Creating table SUPPLIER

CREATE TABLE SUPPLIER(
supplier_id VARCHAR2(10) PRIMARY KEY,
s_name VARCHAR2(50) NOT NULL,
contact_number INT,
email VARCHAR2(100),
address VARCHAR2(150)
);

REM Creating table MEDICINE

CREATE TABLE MEDICINE(
medicine_id VARCHAR2(10) PRIMARY KEY,
m_name VARCHAR2(20) NOT NULL,
brand VARCHAR2(20),
batch_number VARCHAR2(10),
expiry_date DATE,
quantity INT DEFAULT 0,
price DECIMAL(10,2) NOT NULL,
supplier_id VARCHAR2(10),
FOREIGN KEY (supplier_id) REFERENCES SUPPLIER(supplier_id)
);

REM Creating table CUSTOMER

CREATE TABLE CUSTOMER(
customer_id VARCHAR2(10) PRIMARY KEY,
c_name VARCHAR2(30) NOT NULL,
contact_number INT,
email VARCHAR2(40),
address VARCHAR2(50)
);

REM Creating table PRESCRIPTION

CREATE TABLE PRESCRIPTION(
prescription_id VARCHAR2(15) PRIMARY KEY,
customer_id VARCHAR2(10),
doctor_name VARCHAR2(25),
prescription_date DATE,
dosage VARCHAR2(30),
frequency VARCHAR2(40),
duration VARCHAR2(10),
additional_instructions VARCHAR2(75),
FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id)
);


REM Creating table SALES

CREATE TABLE SALES(
sale_id VARCHAR2(10) PRIMARY KEY,
customer_id VARCHAR2(10),
sale_date DATE NOT NULL,
total_amount DECIMAL(10,2) NOT NULL,
payment_method VARCHAR2(20),
FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id)
);

REM Creating table SALES_ITEMS

CREATE TABLE SALES_ITEMS (
sale_item_id VARCHAR2(10) PRIMARY KEY,
sale_id VARCHAR2(10),
medicine_id VARCHAR2(10),
quantity INT DEFAULT 1,
price_per_unit DECIMAL(10, 2),
subtotal DECIMAL(10,2),
FOREIGN KEY (sale_id) REFERENCES SALES(sale_id),
FOREIGN KEY (medicine_id) REFERENCES MEDICINE(medicine_id)
);


REM Inserting values into each table

REM Inserting into SUPPLIER Table

INSERT INTO SUPPLIER (supplier_id, s_name, contact_number, email, address)
VALUES
    ('S005', 'Ramesh Kumar', 9876543210, 'ramesh.kumar@example.com', '123, Kottivakkam, Chennai, Tamil Nadu'),
    ('S012', 'Kavitha Nair', 9654321098, 'kavitha.nair@example.com', '456, R.S. Puram, Coimbatore, Tamil Nadu'),
    ('S021', 'Arunachalam V', 9843214567, 'arunachalam.v@example.com', '789, Simmakkal, Madurai, Tamil Nadu'),
    ('S009', 'Lakshmi S', 9887654321, 'lakshmi.s@example.com', '321, Kilpauk, Chennai, Tamil Nadu'),
    ('S014', 'Mohan Raj', 9776543210, 'mohan.raj@example.com', '654, Tirunelveli Road, Tirunelveli, Tamil Nadu'),
    ('S001', 'Anjali Devi', 9567890123, 'anjali.devi@example.com', '111, Perundurai, Erode, Tamil Nadu'),
    ('S017', 'Suresh Babu', 9443216789, 'suresh.babu@example.com', '222, Thiru Vi Ka Nagar, Tiruchirappalli, Tamil Nadu'),
    ('S018', 'Vani Duraisamy', 9334567890, 'vani.duraisamy@example.com', '333, Marappalam, Salem, Tamil Nadu'),
    ('S004', 'Ganesh Prasad', 9198765432, 'ganesh.prasad@example.com', '444, Alangulam, Dindigul, Tamil Nadu'),
    ('S011', 'Aarti Sundar', 9654321987, 'aarti.sundar@example.com', '555, Ekkatuthangal, Vellore, Tamil Nadu'),
    ('S022', 'Karthik Subramanian', 9478561230, 'karthik.subramanian@example.com', '666, Thanjavur Road, Thanjavur, Tamil Nadu'),
    ('S023', 'Vidhya Ramesh', 9345678901, 'vidhya.ramesh@example.com', '777, Karur Bypass Road, Karur, Tamil Nadu'),
    ('S003', 'Rajesh Kannan', 9845621789, 'rajesh.kannan@example.com', '888, Kanyakumari Road, Kanyakumari, Tamil Nadu'),
    ('S015', 'Sankar Raghavan', 9654321098, 'sankar.raghavan@example.com', '999, Palayamkottai, Thoothukudi, Tamil Nadu'),
    ('S019', 'Naveen Kumar', 9567890234, 'naveen.kumar@example.com', '101, Dindigul Main Road, Namakkal, Tamil Nadu'),
    ('S006', 'Srinivasan Mani', 9445698743, 'srinivasan.mani@example.com', '202, Thiruvalluvar Street, Pudukkottai, Tamil Nadu'),
    ('S020', 'Priya Natarajan', 9334567890, 'priya.natarajan@example.com', '303, Veeravanallur, Tiruppur, Tamil Nadu'),
    ('S008', 'Balaji Reddy', 9198765432, 'balaji.reddy@example.com', '404, Pollachi Road, Pollachi, Tamil Nadu'),
    ('S002', 'Deepika Saravanan', 9887654321, 'deepika.saravanan@example.com', '505, Aruppukottai, Tamil Nadu'),
    ('S016', 'Vikram Selvam', 9478561234, 'vikram.selvam@example.com', '606, Kallakurichi, Virudhunagar, Tamil Nadu'),
    ('S010', 'Aditi Raghavan', 9345678901, 'aditi.raghavan@example.com', '707, Chengalpattu Road, Chengalpattu, Tamil Nadu'),
    ('S013', 'Gayathri Menon', 9567890123, 'gayathri.menon@example.com', '808, Thiruvallur, Perambalur, Tamil Nadu'),
    ('S024', 'Harish Karthik', 9443216789, 'harish.karthik@example.com', '909, Sathy Road, Karamadai, Tamil Nadu'),
    ('S007', 'Manoj Krishnan', 9345126780, 'manoj.krishnan@example.com', '888, Gandhi Road, Thanjavur, Tamil Nadu'),
    ('S025', 'Vasanth Kumar', 9743214567, 'vasanth.kumar@example.com', '010, Thiruvalankadu, Cuddalore, Tamil Nadu');


REM Inserting into MEDICINE Table

INSERT INTO MEDICINE (medicine_id, m_name, brand, batch_number, expiry_date, quantity, price, supplier_id)
VALUES
    ('M005', 'Paracetamol', 'Acetaminophen', 'BATCH123', TO_DATE('2026-05-01', 'YYYY-MM-DD'), 100, 50.00, 'S023'),
    ('M018', 'Amoxicillin', 'Amoxil', 'BATCH543', TO_DATE('2025-09-15', 'YYYY-MM-DD'), 150, 120.00, 'S010'),
    ('M011', 'Ibuprofen', 'Advil', 'BATCH213', TO_DATE('2026-02-20', 'YYYY-MM-DD'), 200, 75.50, 'S018'),
    ('M002', 'Lisinopril', 'Prinivil', 'BATCH321', TO_DATE('2025-12-10', 'YYYY-MM-DD'), 90, 80.00, 'S002'),
    ('M024', 'Cetirizine', 'Zyrtec', 'BATCH999', TO_DATE('2026-04-05', 'YYYY-MM-DD'), 120, 45.00, 'S017'),
    ('M014', 'Metformin', 'Glucophage', 'BATCH888', TO_DATE('2025-08-30', 'YYYY-MM-DD'), 75, 60.00, 'S022'),
    ('M007', 'Amlodipine', 'Norvasc', 'BATCH456', TO_DATE('2026-01-25', 'YYYY-MM-DD'), 60, 100.00, 'S005'),
    ('M022', 'Omeprazole', 'Prilosec', 'BATCH111', TO_DATE('2025-07-18', 'YYYY-MM-DD'), 80, 55.00, 'S004'),
    ('M016', 'Simvastatin', 'Zocor', 'BATCH222', TO_DATE('2026-11-30', 'YYYY-MM-DD'), 50, 90.00, 'S015'),
    ('M001', 'Clopidogrel', 'Plavix', 'BATCH333', TO_DATE('2025-10-20', 'YYYY-MM-DD'), 40, 85.00, 'S019'),
    ('M025', 'Levothyroxine', 'Synthroid', 'BATCH777', TO_DATE('2026-08-14', 'YYYY-MM-DD'), 110, 70.00, 'S021'),
    ('M013', 'Doxycycline', 'Vibramycin', 'BATCH444', TO_DATE('2025-03-11', 'YYYY-MM-DD'), 30, 40.00, 'S006'),
    ('M003', 'Hydrochlorothiazide', 'Hydrodiuril', 'BATCH555', TO_DATE('2026-03-12', 'YYYY-MM-DD'), 95, 65.00, 'S014'),
    ('M019', 'Furosemide', 'Lasix', 'BATCH888', TO_DATE('2026-12-25', 'YYYY-MM-DD'), 70, 50.00, 'S012'),
    ('M008', 'Montelukast', 'Singulair', 'BATCH666', TO_DATE('2025-05-09', 'YYYY-MM-DD'), 85, 60.00, 'S009'),
    ('M012', 'Pantoprazole', 'Protonix', 'BATCH999', TO_DATE('2025-11-01', 'YYYY-MM-DD'), 150, 95.00, 'S008'),
    ('M004', 'Cetirizine', 'Zyrtec', 'BATCH444', TO_DATE('2026-10-30', 'YYYY-MM-DD'), 65, 45.00, 'S020'),
    ('M015', 'Venlafaxine', 'Effexor', 'BATCH777', TO_DATE('2025-06-17', 'YYYY-MM-DD'), 120, 150.00, 'S001'),
    ('M006', 'Escitalopram', 'Lexapro', 'BATCH555', TO_DATE('2026-09-09', 'YYYY-MM-DD'), 75, 80.00, 'S003'),
    ('M020', 'Sertraline', 'Zoloft', 'BATCH222', TO_DATE('2025-02-02', 'YYYY-MM-DD'), 50, 70.00, 'S011'),
    ('M009', 'Bupropion', 'Wellbutrin', 'BATCH888', TO_DATE('2026-12-05', 'YYYY-MM-DD'), 80, 65.00, 'S016'),
    ('M010', 'Azithromycin', 'Zithromax', 'BATCH112', TO_DATE('2025-08-15', 'YYYY-MM-DD'), 100, 90.00, 'S005'),
    ('M017', 'Atorvastatin', 'Lipitor', 'BATCH334', TO_DATE('2026-04-22', 'YYYY-MM-DD'), 85, 75.00, 'S010'),
    ('M021', 'Gabapentin', 'Neurontin', 'BATCH556', TO_DATE('2025-10-05', 'YYYY-MM-DD'), 70, 120.00, 'S012'),
    ('M023', 'Losartan', 'Cozaar', 'BATCH778', TO_DATE('2026-02-18', 'YYYY-MM-DD'), 60, 65.00, 'S018');



REM Inserting into CUSTOMER TABLE

INSERT INTO CUSTOMER (customer_id, c_name, contact_number, email, address)
VALUES
    ('C001', 'Rajesh Sharma', 9876543210, 'rajesh.sharma@example.com', '123, Anna Nagar, Chennai, Tamil Nadu'),
    ('C002', 'Sita Rao', 9988776655, 'sita.rao@example.com', '456, Kotturpuram, Chennai, Tamil Nadu'),
    ('C003', 'Vikram Singh', 9701234567, 'vikram.singh@example.com', '789, T. Nagar, Chennai, Tamil Nadu'),
    ('C004', 'Anjali Gupta', 9598765432, 'anjali.gupta@example.com', '321, Mylapore, Chennai, Tamil Nadu'),
    ('C005', 'Karan Mehta', 9843216789, 'karan.mehta@example.com', '654, Adyar, Chennai, Tamil Nadu'),
    ('C006', 'Pooja Verma', 9871234560, 'pooja.verma@example.com', '987, Saidapet, Chennai, Tamil Nadu'),
    ('C007', 'Rahul Jain', 9912345678, 'rahul.jain@example.com', '654, Kodambakkam, Chennai, Tamil Nadu'),
    ('C008', 'Suresh Babu', 9865432109, 'suresh.babu@example.com', '321, T. Nagar, Chennai, Tamil Nadu'),
    ('C009', 'Meena Reddy', 9809876543, 'meena.reddy@example.com', '432, Alwarpet, Chennai, Tamil Nadu'),
    ('C010', 'Nitin Sharma', 9798765432, 'nitin.sharma@example.com', '543, Tambaram, Chennai, Tamil Nadu'),
    ('C011', 'Aditi Raghavan', 9638527410, 'aditi.raghavan@example.com', '876, Mambalam, Chennai, Tamil Nadu'),
    ('C012', 'Sunita Menon', 9743214567, 'sunita.menon@example.com', '234, Velachery, Chennai, Tamil Nadu'),
    ('C013', 'Rajkumar Iyer', 9865321470, 'rajkumar.iyer@example.com', '345, Kottivakkam, Chennai, Tamil Nadu'),
    ('C014', 'Lakshmi Nair', 9765432109, 'lakshmi.nair@example.com', '456, Nungambakkam, Chennai, Tamil Nadu'),
    ('C015', 'Vivek Krishnan', 9812345670, 'vivek.krishnan@example.com', '567, Ashok Nagar, Chennai, Tamil Nadu'),
    ('C016', 'Priya Das', 9709876543, 'priya.das@example.com', '678, Sholinganallur, Chennai, Tamil Nadu'),
    ('C017', 'Niharika Ramesh', 9898765432, 'niharika.ramesh@example.com', '789, Ekkatuthangal, Chennai, Tamil Nadu'),
    ('C018', 'Ganesh Kumar', 9945678901, 'ganesh.kumar@example.com', '890, Kotturpuram, Chennai, Tamil Nadu'),
    ('C019', 'Srinivas Balakrishnan', 9901234567, 'srinivas.balakrishnan@example.com', '321, Thiruvanmiyur, Chennai, Tamil Nadu'),
    ('C020', 'Rita Choudhury', 9856789012, 'rita.choudhury@example.com', '432, Kottivakkam, Chennai, Tamil Nadu'),
    ('C021', 'Arvind Kumar', 9812347650, 'arvind.kumar@example.com', '543, Anna Nagar, Chennai, Tamil Nadu'),
    ('C022', 'Deepak Reddy', 9701253486, 'deepak.reddy@example.com', '654, T. Nagar, Chennai, Tamil Nadu'),
    ('C023', 'Samantha Joshi', 9897654321, 'samantha.joshi@example.com', '765, Besant Nagar, Chennai, Tamil Nadu'),
    ('C024', 'Akash Bhatia', 9912345678, 'akash.bhatia@example.com', '876, Kottivakkam, Chennai, Tamil Nadu'),
    ('C025', 'Gita Pillai', 9909876543, 'gita.pillai@example.com', '987, Mylapore, Chennai, Tamil Nadu');

REM Inserting into PRESCRIPTION Table

INSERT INTO PRESCRIPTION (prescription_id, customer_id, doctor_name, prescription_date, dosage, frequency, duration, additional_instructions)
VALUES
    ('P001', 'C007', 'Dr. Lakshmi Narayanan', TO_DATE('2024-10-10', 'YYYY-MM-DD'), '500mg Paracetamol', 'Twice a day after meals', '5 days', 'Drink plenty of fluids and rest well.'),
    ('P002', 'C004', 'Dr. Aravind Kumar', TO_DATE('2024-10-11', 'YYYY-MM-DD'), '400mg Ibuprofen', 'As needed for pain, max 3 times a day', NULL, 'Apply ice packs on sore areas.'),
    ('P003', 'C010', 'Dr. Kavitha Priya', TO_DATE('2024-10-12', 'YYYY-MM-DD'), '500mg Amoxicillin', 'Three times daily', '7 days', 'Complete the course even if feeling better.'),
    ('P004', 'C001', 'Dr. Ramesh Babu', TO_DATE('2024-10-13', 'YYYY-MM-DD'), '10mg Cetirizine', 'Once daily at night', NULL, 'Avoid allergens when possible.'),
    ('P005', 'C003', 'Dr. Meena Devi', TO_DATE('2024-10-14', 'YYYY-MM-DD'), '500mg Metformin', 'Twice daily with meals', '30 days', 'Monitor your blood sugar levels regularly.'),
    ('P006', 'C012', 'Dr. Murugan Selvam', TO_DATE('2024-10-15', 'YYYY-MM-DD'), '5mg Amlodipine', 'Once daily in the morning', NULL, 'Monitor blood pressure weekly.'),
    ('P007', 'C015', 'Dr. Rajesh Natarajan', TO_DATE('2024-10-16', 'YYYY-MM-DD'), '40mg Pantoprazole', 'Daily before breakfast', '14 days', 'Avoid spicy and oily foods.'),
    ('P008', 'C022', 'Dr. Divya Manivannan', TO_DATE('2024-10-17', 'YYYY-MM-DD'), '50mg Losartan', 'Once daily in the morning', '60 days', 'Maintain a low-sodium diet.'),
    ('P009', 'C005', 'Dr. Rani Priya', TO_DATE('2024-10-18', 'YYYY-MM-DD'), '75mg Clopidogrel', 'Once daily', NULL, 'Avoid heavy lifting and intense physical activities.'),
    ('P010', 'C020', 'Dr. Kalaivani Rani', TO_DATE('2024-10-19', 'YYYY-MM-DD'), '10mg Montelukast', 'In the evening for 10 days', '10 days', 'Avoid allergens and stay hydrated.'),
    ('P011', 'C019', 'Dr. Vasanthi Sundar', TO_DATE('2024-10-20', 'YYYY-MM-DD'), '20mg Omeprazole', 'Once daily before breakfast', '14 days', 'Avoid alcohol and smoking.'),
    ('P012', 'C017', 'Dr. Mohana Priya', TO_DATE('2024-10-21', 'YYYY-MM-DD'), '100mg Doxycycline', 'Twice daily', '7 days', 'Avoid dairy products and sun exposure.'),
    ('P013', 'C023', 'Dr. Ganesh Kumar', TO_DATE('2024-10-22', 'YYYY-MM-DD'), '50mcg Levothyroxine', 'Once in the morning before meals', NULL, 'Recheck thyroid levels in 6 weeks.'),
    ('P014', 'C024', 'Dr. Selvi Lakshmi', TO_DATE('2024-10-23', 'YYYY-MM-DD'), '0.5mg Alprazolam', 'Once at night', NULL, 'Avoid operating heavy machinery and alcohol.'),
    ('P015', 'C013', 'Dr. Arul Mani', TO_DATE('2024-10-24', 'YYYY-MM-DD'), '10mg Lisinopril', 'Once daily', NULL, 'Monitor blood pressure daily.'),
    ('P016', 'C006', 'Dr. Bharathi Suresh', TO_DATE('2024-10-25', 'YYYY-MM-DD'), '25mg Hydrochlorothiazide', 'Once daily', '21 days', 'Limit salt intake and monitor for dehydration.'),
    ('P017', 'C008', 'Dr. Sundar Kumar', TO_DATE('2024-10-26', 'YYYY-MM-DD'), '20mg Simvastatin', 'At night', '30 days', 'Follow a low-fat diet and check cholesterol levels monthly.'),
    ('P018', 'C018', 'Dr. Mohan Venkatesh', TO_DATE('2024-10-27', 'YYYY-MM-DD'), '1000mg Metformin', 'Twice daily with meals', '30 days', 'Regularly check blood sugar levels.'),
    ('P019', 'C025', 'Dr. Ramesh Kannan', TO_DATE('2024-10-28', 'YYYY-MM-DD'), '200mg Ibuprofen', 'Every 6 hours as needed', NULL, 'Drink fluids to stay hydrated.'),
    ('P020', 'C014', 'Dr. Sudha Banu', TO_DATE('2024-10-29', 'YYYY-MM-DD'), '250mg Amoxicillin', 'Three times a day for 5 days', '5 days', 'Take with food and drink plenty of water.'),
    ('P021', 'C016', 'Dr. Lakshmi Karthik', TO_DATE('2024-10-30', 'YYYY-MM-DD'), '75mg Clopidogrel', 'Once daily', '90 days', 'Monitor for any unusual bleeding.'),
    ('P022', 'C021', 'Dr. Ganesh Prasad', TO_DATE('2024-10-31', 'YYYY-MM-DD'), '10mg Cetirizine', 'Before bed for allergy relief', NULL, 'Avoid allergens and stay indoors if possible.'),
    ('P023', 'C009', 'Dr. Arvind Raghavan', TO_DATE('2024-11-01', 'YYYY-MM-DD'), '10mg Montelukast', 'Daily for asthma management', '14 days', 'Follow up in one month.'),
    ('P024', 'C011', 'Dr. Kumar Raj', TO_DATE('2024-11-02', 'YYYY-MM-DD'), '20mg Atorvastatin', 'Once daily', '30 days', 'Follow a heart-healthy diet.'),
    ('P025', 'C002', 'Dr. Lakshmi Narayanan', TO_DATE('2024-11-03', 'YYYY-MM-DD'), '5mg Furosemide', 'Once daily in the morning', NULL, 'Monitor weight daily for fluid retention.');



REM Inserting into SALES Table

INSERT INTO SALES (sale_id, customer_id, sale_date, total_amount, payment_method)
VALUES
    ('S001', 'C007', TO_DATE('2024-10-10', 'YYYY-MM-DD'), 201.00, 'Credit Card'),
    ('S002', 'C004', TO_DATE('2024-10-11', 'YYYY-MM-DD'), 255.00, 'UPI'),
    ('S003', 'C010', TO_DATE('2024-10-12', 'YYYY-MM-DD'), 220.00, 'Cash'),
    ('S004', 'C001', TO_DATE('2024-10-13', 'YYYY-MM-DD'), 165.50, 'UPI'),
    ('S005', 'C003', TO_DATE('2024-10-14', 'YYYY-MM-DD'), 175.00, 'Debit Card'),
    ('S006', 'C012', TO_DATE('2024-10-15', 'YYYY-MM-DD'), 140.00, 'Cash'),
    ('S007', 'C015', TO_DATE('2024-10-16', 'YYYY-MM-DD'), 50.00, 'Cash'),
    ('S008', 'C022', TO_DATE('2024-10-17', 'YYYY-MM-DD'), 100.00, 'Cash'),
    ('S009', 'C005', TO_DATE('2024-10-18', 'YYYY-MM-DD'), 170.00, 'UPI'),
    ('S010', 'C020', TO_DATE('2024-10-19', 'YYYY-MM-DD'), 95.00, 'Debit Card');



REM Inserting into SALES_ITEMS Table

INSERT INTO SALES_ITEMS (sale_item_id, sale_id, medicine_id, quantity, price_per_unit, subtotal)
VALUES
    ('SI001', 'S001', 'M005', 1, 50.00, 50.00),
    ('SI002', 'S001', 'M011', 2, 75.50, 151.00),
    ('SI003', 'S002', 'M018', 1, 120.00, 120.00),
    ('SI004', 'S002', 'M024', 3, 45.00, 135.00),
    ('SI005', 'S003', 'M005', 2, 50.00, 100.00),
    ('SI006', 'S003', 'M018', 1, 120.00, 120.00),
    ('SI007', 'S004', 'M024', 2, 45.00, 90.00),  
    ('SI008', 'S004', 'M011', 1, 75.50, 75.50),  
    ('SI009', 'S005', 'M013', 3, 40.00, 120.00), 
    ('SI010', 'S005', 'M022', 1, 55.00, 55.00),  
    ('SI011', 'S006', 'M020', 2, 70.00, 140.00), 
    ('SI012', 'S007', 'M019', 1, 50.00, 50.00),
    ('SI013', 'S008', 'M007', 1, 100.00, 100.00),
    ('SI014', 'S009', 'M001', 2, 85.00, 170.00),
    ('SI015', 'S010', 'M012', 1, 95.00, 95.00);



SELECT * FROM SUPPLIER;
SELECT * FROM CUSTOMER;
SELECT * FROM MEDICINE;
SELECT * FROM PRESCRIPTION;
SELECT * FROM SALES;
SELECT * FROM SALES_ITEMS;