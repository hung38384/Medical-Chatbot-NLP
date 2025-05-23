import json
import regex as re
import numpy as np
from datetime import datetime, timedelta
from pyvi import ViTokenizer, ViPosTagger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoModel, AutoTokenizer
import pickle
import os


class NLPProcessor:
    def __init__(self):
        # Đường dẫn tới các file dữ liệu
        self.intents_file = "/Users/admin/Desktop/medical_appointment_chatbot/data/intents.json"
        self.entities_file = "/Users/admin/Desktop/medical_appointment_chatbot/data/entities.json"
        self.model_dir = "models"
        self.intents_data = self._load_json_data(self.intents_file)
        self.entities_data = self._load_json_data(self.entities_file)
        self.intent_texts = []
        self.intent_tags = []
        for intent in self.intents_data:
            for pattern in intent['patterns']:
                self.intent_texts.append(self._preprocess_text(pattern))
                self.intent_tags.append(intent['tag'])
        
        # Tạo thư mục models nếu chưa tồn tại
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        
        # Đường dẫn tới các file model
        self.intent_classifier_path = os.path.join(self.model_dir, "intent_classifier.pkl")
        self.entity_extractor_path = os.path.join(self.model_dir, "entity_extractor.pkl")
        
        # Load dữ liệu intents và entities
        self.intents_data = self._load_json_data(self.intents_file)
        self.entities_data = self._load_json_data(self.entities_file)
        
        # Khởi tạo các model
        self.intent_vectorizer = None
        self.entity_patterns = self._compile_entity_patterns()
        
        # Thử load model nếu đã tồn tại, nếu chưa thì huấn luyện mới
        self._init_models()
        
        # Tokenizer và Model transformer cho tiếng Việt (PhoBERT)
        # Nếu chạy lần đầu tiên, sẽ tự động tải về
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
            self.transformer_model = AutoModel.from_pretrained("vinai/phobert-base")
        except:
            print("Sử dụng mô hình backup cho embedding")
            # Fallback to alternative model if PhoBERT cannot be loaded
            self.tokenizer = None
            self.transformer_model = None

    def _load_json_data(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found. Creating empty data structure.")
            return []
        except json.JSONDecodeError:
            print(f"Error: {file_path} contains invalid JSON.")
            return []

    def _init_models(self):
        # Thử load model intent classifier
        try:
            with open(self.intent_classifier_path, 'rb') as f:
                self.intent_vectorizer = pickle.load(f)
                print("Loaded intent classifier from file")
        except (FileNotFoundError, EOFError):
            print("Training new intent classifier")
            self.train_intent_classifier()
    
    def train_intent_classifier(self):
        # Huấn luyện model intent classifier
        texts = []
        tags = []
        for intent in self.intents_data:
            for pattern in intent['patterns']:
                texts.append(self._preprocess_text(pattern))
                tags.append(intent['tag'])
        # Tiền xử lý văn bản tiếng Việt
        preprocessed_texts = [self._preprocess_text(text) for text in texts]
        
        # Khởi tạo và huấn luyện TF-IDF vectorizer
        self.intent_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.intent_vectorizer.fit(self.intent_texts)
        
        # Lưu model
        with open(self.intent_classifier_path, 'wb') as f:
            pickle.dump(self.intent_vectorizer, f)
        
        print("Intent classifier trained and saved")

    def _compile_entity_patterns(self):
        # Tạo các pattern regex cho việc trích xuất entity
        patterns = {
            'name': r'[tT]ên (?:là|tôi là|của tôi là) ([\p{L}\s]+)',
            'phone': r'(?:số điện thoại|liên hệ|sđt|số|điện thoại)[^\d]*(0\d{9,10})',
            'date': r'(?:ngày|vào ngày|đặt ngày|ngày khám|lịch khám ngày) (\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)',
            'day_of_week': r'(?:vào|ngày) (thứ [2-7]|chủ nhật)',
            'time': r'(?:lúc|vào lúc|giờ|lịch) (\d{1,2}[:.]\d{2}|\d{1,2} giờ(?:[^\d](?:\d{1,2})? phút)?)',
            'doctor': r'(?:bác sĩ|bs|bs.|bác sỹ) ([\p{L}\s]+)',
            'department': r'(?:khoa|chuyên khoa|chuyên ngành) ([\p{L}\s]+)',
            'symptom': r'(?:bị|mắc|có triệu chứng|triệu chứng|cảm thấy) ([\p{L}\s,]+)'
        }
        
        # Biên dịch các regex
        compiled_patterns = {}
        for entity, pattern in patterns.items():
            compiled_patterns[entity] = re.compile(pattern, re.UNICODE)
        
        return compiled_patterns

    def _preprocess_text(self, text):
        # Tiền xử lý văn bản tiếng Việt
        # Chuyển về chữ thường
        text = text.lower()
        # Tokenize (tách từ) sử dụng pyvi thay vì underthesea
        tokens = ViTokenizer.tokenize(text).split()
        # Nối lại các token với khoảng trắng
        preprocessed_text = ' '.join(tokens)
        return preprocessed_text

    def _get_text_embedding(self, text):
        """Tạo embedding vector cho văn bản sử dụng PhoBERT"""
        if self.tokenizer is None or self.transformer_model is None:
            # Fallback to simple TF-IDF if transformer is not available
            return None
        
        # Tokenize và chuyển đổi thành tensor
        input_ids = torch.tensor([self.tokenizer.encode(text)])
        
        # Lấy embedding từ transformer model
        with torch.no_grad():
            outputs = self.transformer_model(input_ids)
            # Lấy vector embedding của token [CLS] (đại diện cho cả câu)
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
        
        return embedding

    def predict_intent(self, text):
        """Dự đoán intent của văn bản đầu vào"""
        preprocessed_text = self._preprocess_text(text)
        
        # Chuyển văn bản thành vector TF-IDF
        text_vector = self.intent_vectorizer.transform([preprocessed_text])
        
        # Tính toán cosine similarity với tất cả các intent trong dataset
        intent_vectors = self.intent_vectorizer.transform(self.intent_texts)
        similarities = cosine_similarity(text_vector, intent_vectors)[0]
        
        # Lấy intent có similarity cao nhất
        max_sim_idx = np.argmax(similarities)
        max_sim = similarities[max_sim_idx]
        
        # Nếu similarity quá thấp, có thể không nhận biết được intent
        if max_sim < 0.3:
            return {"intent": "unknown", "confidence": max_sim}
        
        predicted_intent = self.intent_tags[max_sim_idx]
        return {"intent": predicted_intent, "confidence": max_sim}

    def extract_entities(self, text):
        """Trích xuất các entity từ văn bản đầu vào"""
        entities = {}
        
        # Dùng các pattern regex để trích xuất entity
        for entity_type, pattern in self.entity_patterns.items():
            matches = pattern.search(text)
            if matches:
                entities[entity_type] = matches.group(1).strip()
        
        # Xử lý đặc biệt cho ngày tháng
        if 'date' in entities:
            try:
                date_str = entities['date']
                # Chuyển đổi thành đối tượng datetime
                if '/' in date_str:
                    day, month, year = date_str.split('/')
                elif '-' in date_str:
                    day, month, year = date_str.split('-')
                else:
                    day, month = date_str.split('/')
                    year = datetime.now().year
                
                # Xử lý năm 2 chữ số -> 4 chữ số
                if len(str(year)) == 2:
                    year = 2000 + int(year)
                
                # Chuẩn hóa định dạng ngày
                entities['date'] = f"{int(day):02d}/{int(month):02d}/{year}"
            except:
                pass
        
        # Xử lý ngày trong tuần
        if 'day_of_week' in entities:
            day_of_week = entities['day_of_week']
            # Map tên thứ thành số
            day_mapping = {
                "thứ 2": 0, "thứ hai": 0,
                "thứ 3": 1, "thứ ba": 1,
                "thứ 4": 2, "thứ tư": 2,
                "thứ 5": 3, "thứ năm": 3,
                "thứ 6": 4, "thứ sáu": 4,
                "thứ 7": 5, "thứ bảy": 5,
                "chủ nhật": 6, "cn": 6
            }
            
            dow_value = day_mapping.get(day_of_week.lower())
            if dow_value is not None:
                # Tính toán ngày cụ thể trong tuần
                today = datetime.now()
                current_dow = today.weekday()
                days_ahead = dow_value - current_dow
                
                if days_ahead <= 0:  # Nếu ngày đã qua trong tuần hiện tại
                    days_ahead += 7  # Chuyển sang tuần sau
                
                target_date = today + timedelta(days=days_ahead)
                entities['date'] = target_date.strftime("%d/%m/%Y")
        
        # Sử dụng POS tagging của pyvi thay vì NER từ underthesea
        if 'name' not in entities:
            try:
                # Dùng pyvi để pos tagging
                text_tokenized = ViTokenizer.tokenize(text)
                pos_tags = ViPosTagger.postagging(text_tokenized)
                
                # Tìm các từ có khả năng là tên người (Np - Proper noun)
                person_entities = []
                for i, tag in enumerate(pos_tags[1]):
                    if tag == 'Np':
                        person_entities.append(pos_tags[0][i].replace('_', ' '))
                
                if person_entities:
                    entities['name'] = ' '.join(person_entities)
            except Exception as e:
                print(f"Lỗi khi xử lý tên: {e}")
                pass
                
        return entities

    def get_response_for_intent(self, intent, entities=None, context=None):
        """Tạo câu trả lời dựa trên intent và entity được trích xuất"""
        # Đây chỉ là demo đơn giản, trong thực tế cần một cơ chế phức tạp hơn
        responses = {
            "greeting_appointment": [
                "Xin chào! Tôi là trợ lý ảo của phòng khám. Tôi có thể giúp bạn đặt lịch khám bệnh. Bạn vui lòng cho biết họ tên của mình?",
                "Chào bạn! Rất vui được hỗ trợ bạn đặt lịch khám. Bạn tên là gì ạ?"
            ],
            "appointment_request": [
                "Để đặt lịch khám, trước tiên tôi cần biết họ tên của bạn. Bạn vui lòng cho biết tên?",
                "Tôi sẽ giúp bạn đặt lịch khám. Trước tiên, xin cho biết tên đầy đủ của bạn?"
            ],
            "provide_name": [
                f"Cảm ơn {entities.get('name', 'bạn')}. Vui lòng cho biết số điện thoại để phòng khám có thể liên hệ với bạn?",
                f"Xin chào {entities.get('name', 'bạn')}. Bạn vui lòng cung cấp số điện thoại để tiện liên hệ nhé?"
            ],
            "provide_phone": [
                "Cảm ơn bạn đã cung cấp số điện thoại. Bạn đang gặp vấn đề gì về sức khỏe hoặc muốn khám chuyên khoa nào?",
                "Tôi đã ghi nhận số điện thoại của bạn. Bạn có thể cho biết triệu chứng hoặc vấn đề sức khỏe bạn đang gặp phải?"
            ],
            "symptom_description": [
                f"Với triệu chứng \"{entities.get('symptom', 'bạn đang gặp')}\", tôi gợi ý bạn nên khám tại khoa phù hợp. Bạn muốn được tư vấn thêm về chuyên khoa nào?",
                f"Tôi hiểu rồi. Với tình trạng \"{entities.get('symptom', 'của bạn')}\", bạn nên khám tại khoa chuyên môn. Bạn muốn đặt lịch khám ở khoa nào?"
            ],
            "select_department": [
                f"Bạn đã chọn khám tại khoa {entities.get('department', '')}. Bạn muốn đặt lịch vào ngày nào?",
                f"Tôi đã ghi nhận yêu cầu khám tại khoa {entities.get('department', '')}. Vui lòng cho biết thời gian bạn muốn đến khám?"
            ],
            "provide_schedule": [
                f"Vào {entities.get('date', 'ngày bạn chọn')}, phòng khám có các khung giờ trống: 9:00, 10:30, 14:00 và 15:30. Bạn muốn chọn giờ nào?",
                f"Ngày {entities.get('date', 'bạn yêu cầu')} còn các slot: 8:30, 10:00, 13:30 và 16:00. Bạn muốn đặt lịch vào giờ nào?"
            ],
            "unknown": [
                "Xin lỗi, tôi không hiểu ý bạn. Bạn có thể diễn đạt lại hoặc hỏi câu khác được không?",
                "Tôi chưa hiểu rõ yêu cầu của bạn. Bạn có thể nói rõ hơn được không?"
            ]
        }
        
        # Lấy mẫu câu trả lời cho intent, nếu không có thì dùng unknown
        intent_responses = responses.get(intent, responses["unknown"])
        
        # Chọn ngẫu nhiên một câu trả lời từ các mẫu
        return np.random.choice(intent_responses)

    def process_message(self, text, context=None):
        """Xử lý tin nhắn từ người dùng và trả về phản hồi"""
        # Dự đoán intent
        intent_result = self.predict_intent(text)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        
        # Trích xuất entity
        entities = self.extract_entities(text)
        
        # Tạo câu trả lời dựa trên intent và entity
        response = self.get_response_for_intent(intent, entities, context)
        
        # Trả về kết quả
        result = {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "response": response
        }
        
        return result


# Test code
if __name__ == "__main__":
    processor = NLPProcessor()
    
    # Test cases
    test_texts = [
        "Xin chào, tôi muốn đặt lịch khám bệnh",
        "Tôi tên là Nguyễn Văn An",
        "Số điện thoại của tôi là 0912345678",
        "Tôi bị đau đầu và chóng mặt mấy hôm nay",
        "Tôi muốn khám khoa Thần kinh",
        "Tôi muốn đặt lịch vào thứ 5 tuần sau"
    ]
    
    for text in test_texts:
        print("\nInput:", text)
        result = processor.process_message(text)
        print("Intent:", result["intent"], "- Confidence:", result["confidence"])
        print("Entities:", result["entities"])
        print("Response:", result["response"])