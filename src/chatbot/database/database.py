import sqlite3
from datetime import datetime

DB_PATH = "/Users/admin/Desktop/medical_appointment_chatbot/src/chatbot/database/medical_chatbot.db"

# ------------------ Kết nối Database ------------------
def get_connection():
    return sqlite3.connect(DB_PATH)

# ------------------ Bệnh nhân ------------------
def insert_patient(name, phone):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        print(f"[DEBUG] Đang thêm bệnh nhân: {name} - {phone}")
        cursor.execute("INSERT INTO patients (name, phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        print("[DEBUG] Thêm bệnh nhân thành công.")
    except sqlite3.IntegrityError as e:
        print(f"[DB ERROR] Không thể chèn bệnh nhân: {e}")
    finally:
        conn.close()

def get_patient_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone FROM patients WHERE phone = ?", (phone,))
    patient = cursor.fetchone()
    conn.close()
    return patient

# ------------------ Khoa ------------------
def get_department_id_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM departments WHERE LOWER(name) = LOWER(?)", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def ensure_department_exists(name):
    if get_department_id_by_name(name) is None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()

# ------------------ Bác sĩ ------------------
def find_doctor_by_specialty(specialty):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM doctors WHERE LOWER(specialty) = LOWER(?)", (specialty,))
    doctors = cursor.fetchall()
    conn.close()
    return [{"id": d[0], "name": d[1]} for d in doctors]

def get_doctor_id_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM doctors WHERE LOWER(name) = LOWER(?)", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# ------------------ Lịch hẹn ------------------
def schedule_appointment(patient_id, doctor_id, department_id, date, time, status="pending"):
    if not all([patient_id, doctor_id, department_id, date, time]):
        raise ValueError("Thiếu thông tin cần thiết để đặt lịch.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, department_id, date, time, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (patient_id, doctor_id, department_id, date, time, status))
    conn.commit()
    conn.close()

def get_appointments_by_patient_id(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, d.name, dep.name, a.date, a.time, a.status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN departments dep ON a.department_id = dep.id
        WHERE a.patient_id = ?
    """, (patient_id,))
    appointments = cursor.fetchall()
    conn.close()
    return [
        {
            "appointment_id": a[0],
            "doctor_name": a[1],
            "department_name": a[2],
            "date": a[3],
            "time": a[4],
            "status": a[5]
        } for a in appointments
    ]

def cancel_appointment(appointment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()