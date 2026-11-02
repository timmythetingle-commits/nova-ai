const form = document.getElementById('chatForm');
const input = document.getElementById('messageInput');
const send = document.getElementById('sendButton');
const messages = document.getElementById('messages');
const newChat = document.getElementById('newChat');
let busy = false;
let history = [];

function addMessage(text, role) {
  document.getElementById('welcome')?.remove();
  const row = document.createElement('div');
  row.className = `message ${role}`;
  if (role === 'assistant') {
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = '✦';
    row.appendChild(avatar);
  }
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  row.appendChild(bubble);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return bubble;
}

async function submitMessage(raw) {
  const message = raw.trim();
  if (!message || busy) return;
  busy = true;
  send.disabled = true;
  input.value = '';
  input.style.height = 'auto';
  addMessage(message, 'user');
  const bubble = addMessage('Thinking…', 'assistant');
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message, history: history.slice(-20)}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Something went wrong.');
    bubble.textContent = data.reply;
    history.push({role: 'user', content: message}, {role: 'assistant', content: data.reply});
    history = history.slice(-20);
  } catch (error) {
    bubble.textContent = `Sorry, I couldn't reply. ${error.message}`;
  } finally {
    busy = false;
    send.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', event => {event.preventDefault(); submitMessage(input.value);});
input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (!busy) form.requestSubmit();
  }
});
input.addEventListener('input', () => {input.style.height = 'auto';input.style.height = `${Math.min(input.scrollHeight,130)}px`;});
document.querySelectorAll('[data-prompt]').forEach(button => {
  button.addEventListener('click', () => submitMessage(button.dataset.prompt));
});
newChat.addEventListener('click', () => {window.location.reload();});
