import pandas as pd
import unicodedata
import os
import logging

# Thiết lập logging
os.makedirs("../logs", exist_ok=True)
logging.basicConfig(
    filename='../logs/cleaning.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Hàm chuẩn hóa Unicode và xử lý văn bản
def normalize_text(text):
    if isinstance(text, str):
        text = text.strip().lower()
        return unicodedata.normalize('NFC', text)
    return text

def clean_doctors():
    input_path = "/Users/admin/Desktop/medical_appointment_chatbot/data/raw/doctors.csv"
    output_path = "/Users/admin/Desktop/medical_appointment_chatbot/data/processed/doctors_cleaned.csv"

    try:
        df = pd.read_csv(input_path)
        df = df.applymap(normalize_text)

        # Loại bỏ hàng null hoặc thiếu dữ liệu quan trọng
        df.dropna(subset=["name", "specialty", "schedule"], inplace=True)

        os.makedirs("/Users/admin/Desktop/medical_appointment_chatbot/data/processed", exist_ok=True)
        df.to_csv(output_path, index=False)
        logging.info("Doctors data cleaned and saved successfully.")

    except Exception as e:
        logging.error(f"Failed to clean doctors.csv: {e}")

def clean_diseases():
    input_path = "/Users/admin/Desktop/medical_appointment_chatbot/data/raw/diseases.csv"
    output_path = "/Users/admin/Desktop/medical_appointment_chatbot/data/processed/diseases_cleaned.csv"

    try:
        df = pd.read_csv(input_path)
        df = df.applymap(normalize_text)
        df.dropna(subset=["name", "symptoms", "treatment"], inplace=True)

        os.makedirs("/Users/admin/Desktop/medical_appointment_chatbot/data/processed", exist_ok=True)
        df.to_csv(output_path, index=False)
        logging.info("Diseases data cleaned and saved successfully.")

    except Exception as e:
        logging.error(f"Failed to clean diseases.csv: {e}")

def main():
    logging.info("Starting data cleaning process...")
    clean_doctors()
    clean_diseases()
    logging.info("Data cleaning pipeline completed.")

if __name__ == "__main__":
    main()