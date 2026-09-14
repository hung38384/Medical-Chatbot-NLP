import json
import re
from nlp_processor import NLPProcessor
from response_generator import ResponseGenerator
from data_access import find_doctor_by_specialty, get_disease_info
from database.database import insert_patient, get_patient_by_phone, schedule_appointment, find_doctor_by_specialty, get_department_id_by_name

class DialogueManager:
    def __init__(self):
        self.nlp = NLPProcessor()
        self.response_generator = ResponseGenerator("data/intents.json")

        self.conversation_state = {
            "current_intent": None,
            "entities": {},
            "context": {},
            "history": []
        }

        self.intent_mapping = {
            "greeting": "greeting",
            "greeting_appointment": "appointment_request",
            "appointment_request": "appointment_request",
            "appointment_info": "appointment_info",
            "reschedule_appointment": "reschedule_appointment",
            "cancel_appointment": "cancel_appointment",
            "department_info": "department_info",
            "doctor_info": "doctor_info",
            "symptom_description": "symptom_description",
            "provide_schedule": "provide_schedule",
            "provide_name": "provide_name",
            "provide_phone": "provide_phone",
            "select_department": "select_department",
            "select_doctor": "select_doctor",
            "confirm_appointment": "confirm_appointment",
            "schedule_info": "schedule_info",
            "document_info": "document_info",
            "cost_info": "cost_info",
            "insurance_info": "insurance_info",
            "thank_you": "thank_you",
            "farewell": "farewell"
        }

        self.dialogue_states = {
            "greeting": self._handle_simple_response,
            "farewell": self._handle_simple_response,
            "thank_you": self._handle_simple_response,
            "appointment_request": self._handle_appointment_request,
            "appointment_info": self._handle_simple_response,
            "cancel_appointment": self._handle_simple_response,
            "reschedule_appointment": self._handle_reschedule_appointment,
            "department_info": self._handle_simple_response,
            "doctor_info": self._handle_simple_response,
            "symptom_description": self._handle_simple_response,
            "provide_schedule": self._handle_simple_response,
            "provide_phone": self._handle_simple_response,
            "select_department": self._handle_simple_response,
            "select_doctor": self._handle_simple_response,
            "confirm_appointment": self._handle_simple_response,
            "schedule_info": self._handle_simple_response,
            "document_info": self._handle_simple_response,
            "cost_info": self._handle_simple_response,
            "insurance_info": self._handle_simple_response,
            "fallback": self._handle_fallback,
            "appointment_request": self._handle_appointment_request,
            "provide_name": self._handle_provide_name,
            "provide_name": self._handle_simple_response,
            "provide_phone": self._handle_provide_phone,
            "confirm_appointment": self._handle_confirm_appointment
        }

    def process_message(self, message):
        self.conversation_state["history"].append({"role": "user", "message": message})

        # Nhận diện intent từ NLPProcessor
        intent_result = self.nlp.predict_intent(message)
        raw_intent = intent_result["intent"]
        intent = self.intent_mapping.get(raw_intent, "fallback")
        self.conversation_state["current_intent"] = intent

        # Nhận diện entities
        entities = self.nlp.extract_entities(message)
        self.conversation_state["entities"].update(entities)

        # 🌟 Thêm xử lý thủ công nếu NLP không nhận ra ngày
        if "date" not in self.conversation_state["entities"]:
            match = re.search(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", message)
            if match:
                self.conversation_state["entities"]["date"] = match.group(1)

        # 🌟 Thêm xử lý nếu người dùng nhắc đến chuyên khoa mà NLP không nhận ra
        if "department" not in self.conversation_state["entities"]:
            # Bạn có thể thêm đoạn trích xuất tên chuyên khoa từ các từ phổ biến (tùy bạn muốn nâng cấp)
            pass

        # Chọn hàm xử lý tương ứng
        handler = self.dialogue_states.get(intent, self._handle_fallback)
        response = handler(self, message)

        self.conversation_state["history"].append({"role": "bot", "message": response})
        return response

    def _handle_appointment_request(self, dialogue_manager, user_input):
        entities = self.conversation_state["entities"]

    # Kiểm tra thông tin bắt buộc
        required_entities = ["department", "date"]
        missing = [e for e in required_entities if e not in entities]

        if missing:
            if "department" in missing:
                return "Bạn muốn khám chuyên khoa nào?"
            if "date" in missing:
                return "Bạn muốn khám vào ngày nào?"

    # Đã có chuyên khoa và ngày khám -> hỏi tên người dùng
        return "Vui lòng cung cấp họ tên của bạn để tiếp tục đặt lịch."

    def _handle_reschedule_appointment(self, dialogue_manager, user_input):
        if "date" not in self.conversation_state["entities"]:
            return "Bạn muốn đổi lịch khám sang ngày nào?"
        return self.response_generator.generate_response("reschedule_appointment", self.conversation_state)

    def _handle_simple_response(self, dialogue_manager, user_input):
         intent = self.conversation_state["current_intent"]

            # 🌟 Nếu intent là 'select_department' mà NLP không gán entity thì tự thêm
         if intent == "select_department" and "department" not in self.conversation_state["entities"]:
                self.conversation_state["entities"]["department"] = user_input.strip()

         return self.response_generator.generate_response(intent, self.conversation_state)
    
    def _handle_fallback(self, dialogue_manager, user_input):
        return self.response_generator.generate_response("fallback", self.conversation_state)

    def save_state(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_state, f, ensure_ascii=False, indent=4)

    def load_state(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.conversation_state = json.load(f)
        except FileNotFoundError:
            print(f"Không tìm thấy file trạng thái tại {file_path}")

    def handle_intent(intent, entities):
        if intent == "tìm_bác_sĩ":
            specialty = entities.get("chuyên_khoa")
            doctors = find_doctor_by_specialty(specialty)
            if doctors:
                return f"Các bác sĩ chuyên khoa {specialty}:\n" + "\n".join([d["name"] for d in doctors])
            return "Hiện tại không tìm thấy bác sĩ chuyên khoa này."

        if intent == "tra_cứu_bệnh":
            disease = entities.get("bệnh")
            info = get_disease_info(disease)
            if info:
                return f"Triệu chứng: {info['symptoms']}\nĐiều trị: {info['treatment']}"
            return "Xin lỗi, tôi chưa có thông tin về bệnh này."

        return "Tôi chưa xử lý được yêu cầu này."
    
    def get_response(self, message):
        return self.process_message(message)
    

    def _handle_provide_name(self, dialogue_manager, user_input):
        cleaned_name = user_input.strip()

        # Danh sách các mẫu thường gặp cần loại bỏ
        patterns = [
            r"^(tôi là\s*)",
            r"^(tên tôi là\s*)",
            r"^(tôi tên là\s*)",
            r"^(anh là\s*)",
            r"^(chị là\s*)",
            r"^(em là\s*)",
            r"^(mình là\s*)",
            r"^(cháu là\s*)",
            r"^(con là\s*)"
        ]

        for pattern in patterns:
            cleaned_name = re.sub(pattern, "", cleaned_name, flags=re.IGNORECASE)

        cleaned_name = cleaned_name.strip().title()  # Viết hoa đầu từ cho đẹp

        self.conversation_state["entities"]["name"] = cleaned_name
        return "Cảm ơn bạn. Tiếp theo, vui lòng cho tôi biết số điện thoại của bạn?"

    def _handle_provide_phone(self, dialogue_manager, user_input):
        # Dùng regex để trích xuất số điện thoại Việt Nam (bắt đầu bằng 0, 10-11 số)
        phone_match = re.search(r'0\d{9,10}', user_input)
        if phone_match:
            phone = phone_match.group()
            self.conversation_state["entities"]["phone"] = phone
            return "Bạn có muốn xác nhận đặt lịch không? Vui lòng trả lời 'có' hoặc 'không'."
        else:
            return "Tôi chưa nhận được số điện thoại hợp lệ. Bạn vui lòng cung cấp lại?"

    def _handle_confirm_appointment(self, dialogue_manager, user_input):
        if user_input.strip().lower() not in ["có", "yes", "vâng", "đúng"]:
            return "Đặt lịch đã bị hủy."

        entities = self.conversation_state["entities"]
        name = entities.get("name")
        phone = entities.get("phone")
        department = entities.get("department")
        date = entities.get("date")
        time = entities.get("time", "08:00")

        if not all([name, phone, department, date]):
            missing_info = []
            if not name: missing_info.append("tên")
            if not phone: missing_info.append("số điện thoại")
            if not department: missing_info.append("chuyên khoa")
            if not date: missing_info.append("ngày khám")

            missing_str = ", ".join(missing_info[:-1]) + f" và {missing_info[-1]}" if len(missing_info) > 1 else missing_info[0]
            return f"Vui lòng cung cấp thêm {missing_str} để tôi có thể hoàn tất việc đặt lịch cho bạn."

        # Kiểm tra hoặc thêm bệnh nhân
        patient = get_patient_by_phone(phone)
        if not patient:
            insert_patient(name, phone)
            patient = get_patient_by_phone(phone)
        patient_id = patient[0]

        # Lấy bác sĩ đầu tiên của chuyên khoa
        doctors = find_doctor_by_specialty(department)
        if not doctors:
            return f"Hiện tại không có bác sĩ nào thuộc chuyên khoa {department}."
        doctor_id = doctors[0]["id"]

        # Lấy ID khoa
        department_id = get_department_id_by_name(department)
        if not department_id:
            # print("✅ DEBUG schedule with:", patient_id, doctor_id, department_id, date, time)
            return f"Không tìm thấy khoa '{department}' trong hệ thống."

        # Lưu lịch hẹn
        schedule_appointment(patient_id, doctor_id, department_id, date, time)
        return f"✅ Đặt lịch thành công cho {name} vào ngày {date} lúc {time} với bác sĩ chuyên khoa {department}."