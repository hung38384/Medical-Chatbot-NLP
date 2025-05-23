import json
import os
import re

class IntentClassifier:
    def __init__(self):
        data_path = os.path.join(os.path.dirname(__file__), "../data/intents.json")
        with open(data_path, "r", encoding="utf-8") as f:
            self.intents = json.load(f)

    def classify(self, message):
        message_lower = message.lower().strip() # Áp dụng strip
        for intent_obj in self.intents:
            for pattern in intent_obj["patterns"]:
                pattern_lower = pattern.lower().strip() # Áp dụng strip
                cond1 = pattern_lower in message_lower
                cond2 = message_lower in pattern_lower
                if cond1 or cond2:
                    return intent_obj["tag"]
        return "fallback"   