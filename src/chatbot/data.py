from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    doctors = relationship("Doctor", back_populates="department")
    
    def __repr__(self):
        return f"Department(id={self.id}, name='{self.name}')"


class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    specialization = Column(String(100), nullable=True)
    work_days = Column(String(100), nullable=True)  # Stored as comma-separated values: "1,3,5" for Monday, Wednesday, Friday
    
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    
    def __repr__(self):
        return f"Doctor(id={self.id}, name='{self.name}', department='{self.department.name if self.department else 'None'}')"


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(String(200), nullable=True)
    medical_history = Column(Text, nullable=True)
    
    appointments = relationship("Appointment", back_populates="patient")
    
    def __repr__(self):
        return f"Patient(id={self.id}, name='{self.name}', phone='{self.phone}')"


class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    appointment_datetime = Column(DateTime, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled, rescheduled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    department = relationship("Department")
    
    def __repr__(self):
        return f"Appointment(id={self.id}, patient='{self.patient.name if self.patient else 'None'}', doctor='{self.doctor.name if self.doctor else 'None'}', datetime='{self.appointment_datetime}')"


class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True)
    
    doctor = relationship("Doctor")
    
    def __repr__(self):
        return f"TimeSlot(id={self.id}, doctor='{self.doctor.name if self.doctor else 'None'}', start='{self.start_time}', available={self.is_available})"


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    current_intent = Column(String(50), nullable=True)
    context = Column(Text, nullable=True)  # Stored as JSON
    last_bot_message = Column(Text, nullable=True)
    last_user_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    patient = relationship("Patient")
    
    def __repr__(self):
        return f"Conversation(id={self.id}, session='{self.session_id}', patient_id={self.patient_id}, intent='{self.current_intent}')"


# Database initialization function
def init_db(db_url="sqlite:///medical_appointment.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine


# Create session factory
def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


# Insert sample data for testing
def insert_sample_data(session):
    # Add departments
    departments = [
        Department(name="Thần kinh", description="Chuyên điều trị các bệnh liên quan đến hệ thần kinh"),
        Department(name="Tim mạch", description="Chuyên điều trị các bệnh về tim và mạch máu"),
        Department(name="Da liễu", description="Chuyên điều trị các bệnh về da"),
        Department(name="Nội tiết", description="Chuyên điều trị các bệnh về nội tiết"),
        Department(name="Nhi", description="Chuyên khám và chữa bệnh cho trẻ em"),
        Department(name="Tai mũi họng", description="Chuyên điều trị các bệnh về tai, mũi, họng")
    ]
    session.add_all(departments)
    
    # Add doctors
    doctors = [
        Doctor(name="Lê Minh Đức", department_id=2, specialization="Tim mạch", work_days="2,4,6"),
        Doctor(name="Phạm Thị Hoa", department_id=2, specialization="Tim mạch, Mạch máu", work_days="1,3,5"),
        Doctor(name="Nguyễn Văn Bình", department_id=1, specialization="Thần kinh", work_days="1,2,3,4,5"),
        Doctor(name="Trần Ngọc Mai", department_id=3, specialization="Da liễu", work_days="1,3,5,6"),
        Doctor(name="Hoàng Thị Lan", department_id=4, specialization="Nội tiết, Tiểu đường", work_days="2,4,6")
    ]
    session.add_all(doctors)
    
    session.commit()


if __name__ == "__main__":
    engine = init_db()
    session = get_session(engine)
    insert_sample_data(session)
    print("Database initialized with sample data.")