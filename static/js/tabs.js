/**
 * Tab Management System
 */

let tabCounter = 0;

function createNewTab(language = 'python', name = null, code = null) {
    if (!editorState.monaco) {
        setTimeout(() => createNewTab(language, name, code), 100);
        return;
    }
    
    const tabId = `tab-${++tabCounter}`;
    const tabName = name || `Untitled-${tabCounter}`;
    
    // Create tab element
    const tab = document.createElement('div');
    tab.className = 'tab';
    tab.dataset.tabId = tabId;
    
    const icon = getLanguageIcon(language);
    tab.innerHTML = `
        <i class="fas ${icon} tab-icon"></i>
        <span class="tab-label">${tabName}</span>
        <span class="tab-modified hidden">●</span>
        <span class="tab-close" onclick="closeTab('${tabId}', event)">×</span>
    `;
    
    tab.onclick = (e) => {
        if (!e.target.classList.contains('tab-close')) {
            switchTab(tabId);
        }
    };
    
    // Insert before new tab button
    const container = document.getElementById('tabs-container');
    container.insertBefore(tab, container.querySelector('.new-tab-btn').nextSibling);
    
    // Create editor
    const editor = createEditorInstance(tabId, language, code);
    
    // Store tab data
    editorState.editors[tabId] = {
        editor: editor,
        language: language,
        name: tabName,
        modified: false
    };
    
    // Switch to new tab
    switchTab(tabId);
}

function switchTab(tabId) {
    if (editorState.activeTabId === tabId) return;
    
    // Update UI
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    const tab = document.querySelector(`[data-tab-id="${tabId}"]`);
    if (tab) tab.classList.add('active');
    
    // Update editors
    document.querySelectorAll('.editor-view').forEach(v => v.classList.remove('active'));
    const editorView = document.getElementById(`editor-${tabId}`);
    if (editorView) editorView.classList.add('active');
    
    editorState.activeTabId = tabId;
    
    // Update language dropdown
    if (editorState.editors[tabId]) {
        const langSelect = document.getElementById('lang-select');
        langSelect.value = editorState.editors[tabId].language;
        
        // Layout editor
        setTimeout(() => {
            editorState.editors[tabId].editor.layout();
            editorState.editors[tabId].editor.focus();
        }, 0);
        
        // Check for syntax errors
        checkSyntaxErrors(tabId);
    }
}

function closeTab(tabId, event) {
    if (event) event.stopPropagation();
    
    // Don't close last tab
    if (Object.keys(editorState.editors).length === 1) {
        return;
    }
    
    // Check if modified
    const tabData = editorState.editors[tabId];
    if (tabData && tabData.modified) {
        if (!confirm(`Close ${tabData.name}? Unsaved changes will be lost.`)) {
            return;
        }
    }
    
    // Remove tab UI
    const tab = document.querySelector(`[data-tab-id="${tabId}"]`);
    if (tab) tab.remove();
    
    // Dispose editor
    if (tabData) {
        tabData.editor.dispose();
        const editorView = document.getElementById(`editor-${tabId}`);
        if (editorView) editorView.remove();
        delete editorState.editors[tabId];
    }
    
    // Switch to another tab
    if (editorState.activeTabId === tabId) {
        const remainingTabId = Object.keys(editorState.editors)[0];
        switchTab(remainingTabId);
    }
}

function changeLanguage() {
    const tabId = editorState.activeTabId;
    if (!tabId || !editorState.editors[tabId]) return;
    
    const langSelect = document.getElementById('lang-select');
    const newLang = langSelect.value;
    const monacoLang = getMonacoLanguage(newLang);
    
    const editorData = editorState.editors[tabId];
    const editor = editorData.editor;
    
    // Change language
    editorState.monaco.editor.setModelLanguage(editor.getModel(), monacoLang);
    
    // Set template
    editor.setValue(templates[newLang] || '');
    
    // Update tab data
    editorData.language = newLang;
    editorData.modified = false;
    
    // Update tab icon
    updateTabDisplay(tabId);
    
    // Clear output
    const outputDiv = document.getElementById('output-container');
    outputDiv.textContent = `[Switched to ${newLang}]\n`;
}

function updateTabDisplay(tabId) {
    const tab = document.querySelector(`[data-tab-id="${tabId}"]`);
    const tabData = editorState.editors[tabId];
    
    if (!tab || !tabData) return;
    
    // Update icon
    const icon = getLanguageIcon(tabData.language);
    tab.querySelector('.tab-icon').className = `fas ${icon} tab-icon`;
    
    // Update modified indicator
    const modifiedSpan = tab.querySelector('.tab-modified');
    if (tabData.modified) {
        modifiedSpan.classList.remove('hidden');
    } else {
        modifiedSpan.classList.add('hidden');
    }
}

function getLanguageIcon(language) {
    const icons = {
        'python': 'fa-file-code',
        'javascript': 'fa-file-code',
        'cpp': 'fa-file-code',
        'csharp': 'fa-file-code',
        'java': 'fa-coffee',
        'sql': 'fa-database',
        'rust': 'fa-gear',
        'lua': 'fa-moon',
        'bash': 'fa-terminal',
        'zig': 'fa-bolt',
        'scala': 'fa-file-code',
        'go': 'fa-file-code'
    };
    return icons[language] || 'fa-file';
}

// Event listeners
document.getElementById('new-tab-btn').addEventListener('click', () => {
    createNewTab();
});

document.getElementById('lang-select').addEventListener('change', changeLanguage);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+N: New tab
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        createNewTab();
    }
    
    // Ctrl+W: Close tab
    if (e.ctrlKey && e.key === 'w') {
        e.preventDefault();
        if (editorState.activeTabId && Object.keys(editorState.editors).length > 1) {
            closeTab(editorState.activeTabId, null);
        }
    }
    
    // Ctrl+Tab: Next tab
    if (e.ctrlKey && e.key === 'Tab') {
        e.preventDefault();
        const tabIds = Object.keys(editorState.editors);
        const currentIndex = tabIds.indexOf(editorState.activeTabId);
        const nextIndex = (currentIndex + 1) % tabIds.length;
        switchTab(tabIds[nextIndex]);
    }
    
    // F5: Run code
    if (e.key === 'F5') {
        e.preventDefault();
        runCode();
    }
    
    // Ctrl+Shift+A: Toggle AI
    if (e.ctrlKey && e.shiftKey && e.key === 'A') {
        e.preventDefault();
        toggleAIPanel();
    }
});