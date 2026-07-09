const chatWindow = document.getElementById("chat-window");
const typingIndicator = document.getElementById("typing-indicator");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

function addMessage(text, sender) {
  const bubble = document.createElement("div");
  bubble.className = `msg ${sender}`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(message) {
  typingIndicator.hidden = false;
  sendBtn.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Ocurrió un error inesperado.");
    }

    addMessage(data.reply, "agent");
  } catch (err) {
    addMessage(
      "No se pudo conectar con el agente. Por favor, intentá de nuevo en unos segundos.",
      "error"
    );
    console.error(err);
  } finally {
    typingIndicator.hidden = true;
    sendBtn.disabled = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";
  sendMessage(message);
});

// Al cargar la página, el agente saluda primero.
window.addEventListener("DOMContentLoaded", () => {
  sendMessage("");
});
