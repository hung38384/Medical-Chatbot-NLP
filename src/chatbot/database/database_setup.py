import sqlite3
import pandas as pd
import os

db_path = os.path.join(os.path.dirname(__file__), "medical_chatbot.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Đường dẫn base tới thư mục gốc của project
base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Nạp dữ liệu từ doctors.csv
doctors_csv_path = os.path.join(base_path, "data/processed/doctors_cleaned.csv")
if os.path.exists(doctors_csv_path):
    doctors_df = pd.read_csv(doctors_csv_path)
    doctors_df.to_sql("doctors", conn, if_exists="replace", index=False)
else:
    print(f"Warning: Không tìm thấy {doctors_csv_path}")

# Nạp dữ liệu từ diseases.csv
diseases_csv_path = os.path.join(base_path, "data/processed/diseases_cleaned.csv")
if os.path.exists(diseases_csv_path):
    diseases_df = pd.read_csv(diseases_csv_path)
    diseases_df.to_sql("diseases", conn, if_exists="replace", index=False)
else:
    print(f"Warning: Không tìm thấy {diseases_csv_path}")


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

# Thêm dữ liệu mẫu cho khoa nếu chưa có
cursor.execute('SELECT COUNT(*) FROM departments')
if cursor.fetchone()[0] == 0:
    departments_data = [
        ("Nội khoa", "Khám và điều trị các bệnh nội khoa chung"),
        ("Ngoại khoa", "Khám và phẫu thuật các bệnh ngoại khoa"),
        ("Nhi khoa", "Khám và điều trị bệnh cho trẻ em"),
        ("Sản phụ khoa", "Khám thai và các bệnh phụ khoa"),
        ("Mắt", "Khám và điều trị các bệnh về mắt"),
        ("Răng hàm mặt", "Khám và điều trị nha khoa")
    ]
    cursor.executemany("INSERT INTO departments (name, description) VALUES (?, ?)", departments_data)

conn.commit()
conn.close()