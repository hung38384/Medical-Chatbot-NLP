import pandas as pd

# Load dữ liệu đã được làm sạch
DOCTORS_PATH = "/Users/admin/Desktop/medical_appointment_chatbot/data/processed/diseases_cleaned.csv"
DISEASES_PATH = "/Users/admin/Desktop/medical_appointment_chatbot/data/processed/doctors_cleaned.csv"

# Có thể load một lần và cache lại nếu muốn tối ưu
doctors_df = pd.read_csv(DOCTORS_PATH)
diseases_df = pd.read_csv(DISEASES_PATH)

def find_doctor_by_specialty(specialty):
    matches = doctors_df[doctors_df['specialty'].str.contains(specialty, case=False, na=False)]
    return matches.to_dict(orient="records")

def get_disease_info(disease_name):
    row = diseases_df[diseases_df["name"].str.lower() == disease_name.lower()]
    if not row.empty:
        return row.iloc[0].to_dict()
    return None