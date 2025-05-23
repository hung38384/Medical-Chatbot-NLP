from dialogue_manager import DialogueManager

def chat():
    print("🤖 Chatbot: Xin chào! Tôi có thể giúp gì cho bạn hôm nay?")
    print("💬 Gõ 'exit' hoặc 'quit' để kết thúc cuộc trò chuyện.\n")

    try:
        dialogue_manager = DialogueManager()
    except Exception as e:
        print("❌ Lỗi khi khởi tạo DialogueManager:", e)
        return

    while True:
        try:
            user_input = input("👤 Bạn: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("🤖 Chatbot: Tạm biệt! Chúc bạn một ngày tốt lành!")
                break

            if not user_input:
                print("⚠️ Vui lòng nhập gì đó...")
                continue

            response = dialogue_manager.process_message(user_input)
            print("🤖 Chatbot:", response)
            print()

        except Exception as e:
            print("❌ Đã xảy ra lỗi khi xử lý:", e)
            continue

if __name__ == "__main__":
    chat()