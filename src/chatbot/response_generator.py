import random
import json

class ResponseGenerator:
    def __init__(self, intents_file_path):
        with open(intents_file_path, "r", encoding="utf-8") as f:
            self.intents_data = json.load(f)
        # Chuyển thành dict để tra cứu nhanh
        self.intent_to_responses = {
            intent["tag"]: intent["responses"]
            for intent in self.intents_data
        }

    def generate_response(self, intent, conversation_state):
        entities = conversation_state.get("entities", {})

        # Nếu intent có trong JSON, trả lời ngẫu nhiên 1 câu
        if intent in self.intent_to_responses:
            return random.choice(self.intent_to_responses[intent])

        # Nếu không có, trả lời mặc định
        return "Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể nói rõ hơn được không?"