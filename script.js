const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

function parseMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = "msg " + (sender === "user" ? "user-msg" : "bot-msg");
  if (sender === "bot") {
    div.innerHTML = parseMarkdown(text);
  } else {
    div.textContent = text;
  }
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;
  addMessage(text, "user");
  userInput.value = "";
  addMessage("...", "bot");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    chatBox.lastChild.innerHTML = parseMarkdown(data.response);
  } catch (err) {
    chatBox.lastChild.textContent = "حصل خطأ في الاتصال";
  }
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
