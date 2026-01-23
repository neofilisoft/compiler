/**
 * Terminal I/O Management
 */

const socket = io();
const outputDiv = document.getElementById('output-container');
const inputField = document.getElementById('term-input');

// Socket event listeners
socket.on('term_output', function(msg) {
    const text = msg.data;
    
    // Format output with syntax highlighting for errors
    let formattedText = text
        .replace(/(ERROR!|Error|error|Exception|Traceback|FAILED|Failed)/gi, '<span class="error-text">$1</span>')
        .replace(/(SyntaxError|TypeError|ValueError|RuntimeError|NameError|ReferenceError|IndentationError)/g, '<span class="error-text">$1</span>')
        .replace(/(Warning|WARNING|Deprecated)/gi, '<span class="warning-text">$1</span>')
        .replace(/(File ".+", line \d+)/g, '<span style="color: #ce9178;">$1</span>')
        .replace(/(\^+)/g, '<span class="error-text">$1</span>')
        .replace(/(Success|SUCCESS|Passed|PASSED)/gi, '<span class="success-text">$1</span>');
    
    outputDiv.insertAdjacentHTML('beforeend', formattedText);
    outputDiv.scrollTop = outputDiv.scrollHeight;
});

socket.on('term_stop', function(msg) {
    const statusClass = msg.success ? 'success-text' : 'error-text';
    outputDiv.insertAdjacentHTML('beforeend', `<span class="${statusClass}">${msg.data}</span>`);
    
    inputField.disabled = true;
    inputField.value = '';
    outputDiv.scrollTop = outputDiv.scrollHeight;
});

// Run code
function runCode() {
    const editorData = getActiveEditor();
    if (!editorData) {
        alert('No active editor');
        return;
    }
    
    const code = editorData.editor.getValue();
    const language = editorData.language;
    
    // Clear output
    outputDiv.innerHTML = '<span style="color: #007acc;">▶ Running...</span>\n\n';
    
    // Enable input
    inputField.disabled = false;
    inputField.focus();
    
    // Emit to server
    socket.emit('run_code', {
        code: code,
        language: language
    });
}

// Send input to process
function sendInput() {
    const text = inputField.value;
    if (!text) return;
    
    outputDiv.innerHTML += `<span style="color: #569cd6;">${text}</span>\n`;
    socket.emit('send_input', { input: text });
    inputField.value = '';
    outputDiv.scrollTop = outputDiv.scrollHeight;
}

// Event listeners
document.getElementById('run-btn').addEventListener('click', runCode);

inputField.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendInput();
    }
});

// Clear terminal (Ctrl+L)
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'l') {
        if (document.activeElement === inputField) {
            e.preventDefault();
            outputDiv.innerHTML = '';
        }
    }
});
