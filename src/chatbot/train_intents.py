from nlp_processor import NLPProcessor

if __name__ == "__main__":
    print("Huấn luyện mô hình phân loại intent...")
    processor = NLPProcessor()
    processor.train_intent_classifier()
    print("Huấn luyện hoàn tất.")