/**
 * AI Assistant Integration
 */

const aiPanel = document.getElementById('ai-panel');
const aiChatContent = document.getElementById('ai-chat-content');
const aiInput = document.getElementById('ai-input');
const aiProviderSelect = document.getElementById('ai-provider-select');

function toggleAIPanel() {
    aiPanel.classList.toggle('open');
    if (aiPanel.classList.contains('open')) {
        aiInput.focus();
    }
}

document.getElementById('ai-toggle-btn').addEventListener('click', toggleAIPanel);

function addAIMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `ai-message ${role}`;
    
    if (role === 'user') {
        messageDiv.innerHTML = `<strong>You:</strong><br>${escapeHtml(content)}`;
    } else {
        messageDiv.innerHTML = `<strong>AI:</strong><br>${formatAIResponse(content)}`;
    }
    
    aiChatContent.appendChild(messageDiv);
    aiChatContent.scrollTop = aiChatContent.scrollHeight;
}

function formatAIResponse(text) {
    // Convert code blocks
    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, function(match, lang, code) {
        return `<pre style="background: #1e1e1e; padding: 10px; border-radius: 5px; overflow-x: auto;"><code>${escapeHtml(code)}</code></pre>`;
    });
    
    // Convert inline code
    text = text.replace(/`([^`]+)`/g, '<code style="background: #3c3c3c; padding: 2px 5px; border-radius: 3px;">$1</code>');
    
    // Convert newlines to <br>
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function aiSendMessage() {
    const message = aiInput.value.trim();
    if (!message) return;
    
    const provider = aiProviderSelect.value;
    
    // Add user message
    addAIMessage('user', message);
    aiInput.value = '';
    
    // Get current code context
    const editorData = getActiveEditor();
    const context = editorData ? {
        language: editorData.language,
        code: editorData.editor.getValue()
    } : null;
    
    // Show loading
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'ai-message assistant';
    loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Thinking...';
    aiChatContent.appendChild(loadingDiv);
    aiChatContent.scrollTop = aiChatContent.scrollHeight;
    
    try {
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: provider,
                message: message,
                context: context
            })
        });
        
        const data = await response.json();
        
        // Remove loading
        loadingDiv.remove();
        
        if (data.success) {
            addAIMessage('assistant', data.response);
        } else {
            addAIMessage('assistant', `❌ Error: ${data.error}`);
        }
    } catch (error) {
        loadingDiv.remove();
        addAIMessage('assistant', `❌ Network error: ${error.message}`);
    }
}

async function aiExplainCode() {
    const editorData = getActiveEditor();
    if (!editorData) {
        alert('No code to explain');
        return;
    }
    
    const code = editorData.editor.getValue();
    const language = editorData.language;
    const provider = aiProviderSelect.value;
    
    if (!code.trim()) {
        alert('Editor is empty');
        return;
    }
    
    // Open AI panel
    if (!aiPanel.classList.contains('open')) {
        toggleAIPanel();
    }
    
    // Add message
    addAIMessage('user', `Explain this ${language} code`);
    
    // Show loading
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'ai-message assistant';
    loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing code...';
    aiChatContent.appendChild(loadingDiv);
    aiChatContent.scrollTop = aiChatContent.scrollHeight;
    
    try {
        const response = await fetch('/api/ai/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: provider,
                code: code,
                language: language
            })
        });
        
        const data = await response.json();
        loadingDiv.remove();
        
        if (data.success) {
            addAIMessage('assistant', data.response);
        } else {
            addAIMessage('assistant', `❌ Error: ${data.error}`);
        }
    } catch (error) {
        loadingDiv.remove();
        addAIMessage('assistant', `❌ Network error: ${error.message}`);
    }
}

async function aiFixError() {
    const editorData = getActiveEditor();
    if (!editorData) {
        alert('No code to fix');
        return;
    }
    
    const code = editorData.editor.getValue();
    const language = editorData.language;
    const provider = aiProviderSelect.value;
    
    // Get last error from terminal
    const terminalText = outputDiv.textContent;
    const errorMatch = terminalText.match(/(Error|Exception|Traceback)[\s\S]*$/i);
    const errorText = errorMatch ? errorMatch[0] : 'Unknown error';
    
    if (!errorText || errorText === 'Unknown error') {
        alert('No error found in terminal. Run the code first.');
        return;
    }
    
    // Open AI panel
    if (!aiPanel.classList.contains('open')) {
        toggleAIPanel();
    }
    
    // Add message
    addAIMessage('user', 'Fix this error in my code');
    
    // Show loading
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'ai-message assistant';
    loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Finding solution...';
    aiChatContent.appendChild(loadingDiv);
    aiChatContent.scrollTop = aiChatContent.scrollHeight;
    
    try {
        const response = await fetch('/api/ai/fix', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: provider,
                code: code,
                error: errorText,
                language: language
            })
        });
        
        const data = await response.json();
        loadingDiv.remove();
        
        if (data.success) {
            addAIMessage('assistant', data.response);
        } else {
            addAIMessage('assistant', `❌ Error: ${data.error}`);
        }
    } catch (error) {
        loadingDiv.remove();
        addAIMessage('assistant', `❌ Network error: ${error.message}`);
    }
}

// Enter to send in AI input
aiInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        aiSendMessage();
    }
});