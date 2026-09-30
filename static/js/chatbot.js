/**
 * SecureVote — Chatbot Widget Controller
 *
 * Manages the floating chatbot widget: open/close toggle,
 * message sending via AJAX, and response rendering.
 */

let chatbotOpen = false;

/**
 * Toggle the chatbot panel open/closed.
 */
function toggleChatbot() {
    const panel = document.getElementById('chatbot-panel');
    const iconOpen = document.getElementById('chat-icon-open');
    const iconClose = document.getElementById('chat-icon-close');
    const ping = document.getElementById('chatbot-ping');

    chatbotOpen = !chatbotOpen;

    if (chatbotOpen) {
        panel.classList.remove('hidden');
        panel.style.animation = 'slideUp 0.3s ease-out';
        iconOpen.classList.add('hidden');
        iconClose.classList.remove('hidden');
        ping.classList.add('hidden');

        // Focus input
        setTimeout(() => {
            document.getElementById('chatbot-input').focus();
        }, 100);
    } else {
        panel.style.animation = 'none';
        panel.classList.add('hidden');
        iconOpen.classList.remove('hidden');
        iconClose.classList.add('hidden');
    }
}

/**
 * Send a chat message to the backend.
 */
function sendChatMessage(event) {
    if (event) event.preventDefault();

    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    const typingId = showTypingIndicator();

    // Get CSRF token
    const csrfToken = getCsrfToken();

    // Send to backend
    fetch('/chat/message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ message: message }),
    })
    .then(response => response.json())
    .then(data => {
        removeTypingIndicator(typingId);
        addMessage(data.reply, 'bot');
    })
    .catch(error => {
        console.error('Chatbot error:', error);
        removeTypingIndicator(typingId);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    });
}

/**
 * Send a pre-defined quick message.
 */
function sendQuickMessage(message) {
    const input = document.getElementById('chatbot-input');
    input.value = message;
    sendChatMessage(null);
}

/**
 * Add a message bubble to the chat area.
 */
function addMessage(content, sender) {
    const messagesContainer = document.getElementById('chatbot-messages');

    const bubble = document.createElement('div');
    bubble.className = sender === 'user' ? 'chat-bubble-user animate-slide-up' : 'chat-bubble-bot animate-slide-up';
    bubble.innerHTML = content;

    messagesContainer.appendChild(bubble);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Show a typing indicator in the chat.
 */
function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatbot-messages');
    const id = 'typing-' + Date.now();

    const indicator = document.createElement('div');
    indicator.id = id;
    indicator.className = 'chat-bubble-bot animate-slide-up';
    indicator.innerHTML = `
        <div class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 0ms;"></span>
            <span class="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 150ms;"></span>
            <span class="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 300ms;"></span>
        </div>
    `;

    messagesContainer.appendChild(indicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return id;
}

/**
 * Remove the typing indicator.
 */
function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) indicator.remove();
}

/**
 * Get the CSRF token from the DOM.
 */
function getCsrfToken() {
    // Try meta tag first, then hidden input
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');

    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;

    // Try cookie fallback
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') return value;
    }

    return '';
}
