const chatbox = document.getElementById('chatbox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

function appendMessage(who, text) {
  const p = document.createElement('p');
  p.className = who;
  p.innerText = (who === 'user' ? 'You: ' : 'Bot: ') + text;
  chatbox.appendChild(p);
  chatbox.scrollTop = chatbox.scrollHeight;
}

sendBtn.addEventListener('click', async () => {
  const text = userInput.value.trim();
  if (!text) return;
  appendMessage('user', text);
  userInput.value = '';
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    if (!res.ok) {
      appendMessage('bot', 'Error: ' + (data.response || res.statusText));
      return;
    }
    appendMessage('bot', data.response);
  } catch (err) {
    appendMessage('bot', 'Network error. Please check connection.');
  }
});

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendBtn.click();
});
