import sqlite3
import pandas as pd

conn = sqlite3.connect("medical_chatbot.db")
cursor = conn.cursor()

# Nạp dữ liệu từ doctors.csv
doctors_df = pd.read_csv("/Users/admin/Desktop/medical_appointment_chatbot/data/processed/doctors_cleaned.csv")
doctors_df.to_sql("doctors", conn, if_exists="replace", index=False)

# Nạp dữ liệu từ diseases.csv
diseases_df = pd.read_csv("/Users/admin/Desktop/medical_appointment_chatbot/data/processed/diseases_cleaned.csv")
diseases_df.to_sql("diseases", conn, if_exists="replace", index=False)


# Bảng bệnh nhân
cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT UNIQUE
)
''')

# Bảng chuyên khoa
cursor.execute('''
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT
)
''')

# Bảng bác sĩ
cursor.execute('''
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialty TEXT,
    availability TEXT
)
''')

# Bảng lịch hẹn
cursor.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    department_id INTEGER,
    date TEXT,
    time TEXT,
    status TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
)
''')

# Bảng triệu chứng
cursor.execute('''
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    department TEXT
)
''')

conn.commit()
conn.close()