
// Generate a unique session ID
const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendExample(message) {
    document.getElementById('messageInput').value = message;
    sendMessage();
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input and disable button
    input.value = '';
    sendButton.disabled = true;
    
    // Show loading indicator
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
                context: {}
            })
        });
        
        const data = await response.json();
        
        // Remove loading indicator
        removeMessage(loadingId);
        
        // Add assistant response
        addAssistantMessage(data);
        
    } catch (error) {
        removeMessage(loadingId);
        addMessage('Error: ' + error.message, 'assistant');
    } finally {
        sendButton.disabled = false;
        input.focus();
    }
}

function addMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${sender}`;
    messageDiv.innerHTML = `
        <div class="message-bubble">${escapeHtml(text)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addLoadingMessage() {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    const loadingId = 'loading_' + Date.now();
    messageDiv.id = loadingId;
    messageDiv.className = 'message message-assistant';
    messageDiv.innerHTML = `
        <div class="message-bubble">
            <span class="loading"></span>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
    return loadingId;
}

function removeMessage(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function addAssistantMessage(data) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    
    let html = `<div class="message-bubble">${escapeHtml(data.natural_language_answer)}`;
    
    if (data.sql_query && !data.sql_query.startsWith('-- No matching')) {
        html += `<div class="sql-query"><strong>SQL Query:</strong>\n${escapeHtml(data.sql_query)}</div>`;
    }
    
    html += `<div class="metadata">
        ⚡ ${data.latency_ms}ms • 
        🎯 ${data.token_usage.total_tokens} tokens • 
        📊 ${data.provider} (${data.model})
    </div>`;
    
    html += '</div>';
    messageDiv.innerHTML = html;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Focus input on load
document.getElementById('messageInput').focus();