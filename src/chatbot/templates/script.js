document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (message === "") return;

    appendMessage("user", message);
    userInput.value = "";
    userInput.focus();

    appendMessage("bot", "Đang xử lý...");

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      const data = await res.json();
      removeLastBotMessage(); // Remove "Đang xử lý..."
      appendMessage("bot", data.response);
    } catch (error) {
      removeLastBotMessage();
      appendMessage("bot", "❌ Có lỗi xảy ra. Vui lòng thử lại.");
    }
  });

  function appendMessage(sender, text) {
    const msg = document.createElement("div");
    msg.classList.add("chat-message");
    msg.classList.add(sender === "user" ? "user-message" : "bot-message");
    msg.innerText = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function removeLastBotMessage() {
    const messages = document.querySelectorAll(".bot-message");
    if (messages.length > 0) {
      messages[messages.length - 1].remove();
    }
  }
});