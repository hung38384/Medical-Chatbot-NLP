import json
import os
import re

class EntityRecognizer:
    def __init__(self):
        data_path = os.path.join(os.path.dirname(__file__), "../data/entities.json")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Chuyển danh sách các câu thành từ điển thực thể
        self.entities = {}  # {entity_type: [value1, value2, ...]}
        for item in data:
            for ent in item.get("entities", []):
                ent_type = ent["entity"]
                ent_val = ent["value"]
                if ent_type not in self.entities:
                    self.entities[ent_type] = []
                if ent_val not in self.entities[ent_type]:
                    self.entities[ent_type].append(ent_val)

    def extract_entities(self, message):
        result = {}
        for entity, values in self.entities.items():
            for val in values:
                # Sử dụng re.escape để tránh lỗi nếu val có ký tự đặc biệt
                if re.search(re.escape(val.lower()), message.lower()):
                    result[entity] = val
        return result