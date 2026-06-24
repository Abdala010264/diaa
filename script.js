const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const micBtn = document.getElementById('micBtn');
const camBtn = document.getElementById('camBtn');
let history = [];

function parseMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `msg ${sender === 'user' ? 'user-msg' : 'bot-msg'}`;
    div.innerHTML = sender === 'bot' ? parseMarkdown(text) : text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    addMessage(text, 'user');
    userInput.value = '';

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'msg bot-msg';
    loadingDiv.textContent = '⏳ جاري التفكير...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history })
        });
        const data = await res.json();
        loadingDiv.innerHTML = parseMarkdown(data.response);
        history.push({ role: 'user', content: text });
        history.push({ role: 'assistant', content: data.response });
    } catch {
        loadingDiv.textContent = '❌ حدث خطأ في الاتصال';
    }
}

function newChat() {
    chatBox.innerHTML = `
        <div class="welcome-msg">
            <div class="avatar">🌙</div>
            <p>أهلاً بك في الطيبات! كيف يمكنني مساعدتك اليوم؟</p>
        </div>
    `;
    userInput.value = '';
    history = [];
    userInput.focus();
}

sendBtn.addEventListener('click', sendMessage);
newChatBtn.addEventListener('click', newChat);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

micBtn.addEventListener('click', () => {
    alert('🎤 سيتم تفعيل المايك قريباً!');
});

camBtn.addEventListener('click', () => {
    alert('📷 سيتم تفعيل الكاميرا قريباً!');
});
