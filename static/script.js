const chatbox = document.getElementById('chatbox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

function appendMessage(who, text, typing = false) {
  const messageWrapper = document.createElement('div');
  messageWrapper.className = `message ${who}`;

  const p = document.createElement('p');
  p.innerText = (who === 'user' ? 'You: ' : 'Bot: ');

  if (typing) {
    const span = document.createElement('span');
    span.className = "typing";
    span.innerText = "..."; // typing dots
    p.appendChild(span);
  } else {
    p.innerText += text;
  }

  messageWrapper.appendChild(p);
  chatbox.appendChild(messageWrapper);
  chatbox.scrollTop = chatbox.scrollHeight;

  return p; // return paragraph for later updates
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;
  
  appendMessage('user', text);
  userInput.value = '';

  // show typing indicator
  const botMsg = appendMessage('bot', '', true);

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    botMsg.innerText = 'Bot: ';
    if (!res.ok) {
      botMsg.innerText += 'Error: ' + (data.response || res.statusText);
      return;
    }

    // typing effect for bot response
    const responseText = data.response;
    let i = 0;
    const interval = setInterval(() => {
      if (i < responseText.length) {
        botMsg.innerText += responseText.charAt(i);
        chatbox.scrollTop = chatbox.scrollHeight;
        i++;
      } else {
        clearInterval(interval);
      }
    }, 30); // speed of typing effect

  } catch (err) {
    botMsg.innerText = 'Bot: Network error. Please check connection.';
  }
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMessage();
});

