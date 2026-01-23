/**
 * Monaco Editor Management
 */

const editorState = {
    editors: {},
    activeTabId: null,
    monaco: null
};

const templates = {
    python: "# Python Example\nprint('Hello from NOC!')\nname = input('What is your name? ')\nprint(f'Nice to meet you, {name}!')",
    cpp: "#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << \"Hello from C++!\" << endl;\n    return 0;\n}",
    csharp: "using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine(\"Hello from C#!\");\n    }\n}",
    java: "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello from Java!\");\n    }\n}",
    javascript: "// Node.js Example\nconsole.log('Hello from Node.js!');\n\nconst readline = require('readline').createInterface({\n    input: process.stdin,\n    output: process.stdout\n});\n\nreadline.question('What is your name? ', name => {\n    console.log(`Nice to meet you, ${name}!`);\n    readline.close();\n});",
    sql: "-- SQLite In-Memory Database\nCREATE TABLE Users (ID INT, Name TEXT);\nINSERT INTO Users VALUES (1, 'Neo'), (2, 'Trinity');\nSELECT * FROM Users;",
    rust: "fn main() {\n    println!(\"Hello from Rust!\");\n}",
    lua: "print('Hello from Lua!')\nprint('Enter your name:')\nlocal name = io.read()\nprint('Nice to meet you, ' .. name .. '!')",
    bash: "#!/bin/bash\n\necho 'Hello from Bash!'\necho 'Current directory:'\npwd\necho ''\necho 'Files:'\nls -la",
    zig: "const std = @import(\"std\");\n\npub fn main() void {\n    std.debug.print(\"Hello from Zig!\\n\", .{});\n}",
    scala: "object Main extends App {\n    println(\"Hello from Scala!\")\n}",
    go: "package main\n\nimport \"fmt\"\n\nfunc main() {\n    fmt.Println(\"Hello from Go!\")\n}"
};

function getMonacoLanguage(lang) {
    const mappings = {
        'cpp': 'cpp',
        'csharp': 'csharp',
        'javascript': 'javascript',
        'bash': 'shell',
        'python': 'python',
        'java': 'java',
        'sql': 'sql',
        'rust': 'rust',
        'lua': 'lua',
        'zig': 'zig',
        'scala': 'scala',
        'go': 'go'
    };
    return mappings[lang] || lang;
}

function initializeMonaco() {
    require.config({ 
        paths: { 
            'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.34.1/min/vs' 
        }
    });
    
    require(['vs/editor/editor.main'], function() {
        editorState.monaco = monaco;
        
        // Configure diagnostics
        monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
            noSemanticValidation: false,
            noSyntaxValidation: false
        });
        
        monaco.languages.typescript.typescriptDefaults.setDiagnosticsOptions({
            noSemanticValidation: false,
            noSyntaxValidation: false
        });
        
        // Create first tab
        createNewTab();
    });
}

function createEditorInstance(tabId, language, initialCode) {
    const container = document.createElement('div');
    container.className = 'editor-view';
    container.id = `editor-${tabId}`;
    document.getElementById('editor-container').appendChild(container);
    
    const editor = editorState.monaco.editor.create(container, {
        value: initialCode || templates[language] || '',
        language: getMonacoLanguage(language),
        theme: 'vs-dark',
        automaticLayout: true,
        fontSize: 14,
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        glyphMargin: true,
        folding: true,
        lineNumbersMinChars: 3,
        lineDecorationsWidth: 10,
        renderLineHighlight: 'all',
        quickSuggestions: true,
        suggestOnTriggerCharacters: true,
        parameterHints: { enabled: true },
        formatOnType: true,
        formatOnPaste: true
    });
    
    // Listen to content changes
    editor.onDidChangeModelContent(() => {
        updateTabModifiedState(tabId, true);
        checkSyntaxErrors(tabId);
    });
    
    // Listen to cursor position changes
    editor.onDidChangeCursorPosition((e) => {
        // Can show line/column in status bar
    });
    
    return editor;
}

function checkSyntaxErrors(tabId) {
    const editorData = editorState.editors[tabId];
    if (!editorData) return;
    
    const editor = editorData.editor;
    const model = editor.getModel();
    
    // Get Monaco's built-in markers (errors/warnings)
    const markers = editorState.monaco.editor.getModelMarkers({ resource: model.uri });
    
    updateProblemsPanel(markers, tabId);
}

function updateProblemsPanel(markers, tabId) {
    const problemsList = document.getElementById('problems-list');
    const problemCount = document.getElementById('problem-count');
    const problemsPanel = document.getElementById('problems-panel');
    
    if (!markers || markers.length === 0) {
        problemsList.innerHTML = '<div style="padding: 15px; color: #858585; text-align: center;">No problems detected</div>';
        problemCount.textContent = '0';
        problemsPanel.classList.remove('show');
        return;
    }
    
    problemsPanel.classList.add('show');
    problemCount.textContent = markers.length;
    
    problemsList.innerHTML = '';
    markers.forEach(marker => {
        const item = document.createElement('div');
        item.className = 'problem-item';
        
        const severity = marker.severity === 8 ? 'error' : 'warning';
        const icon = severity === 'error' ? 'fa-times-circle' : 'fa-exclamation-triangle';
        
        item.innerHTML = `
            <i class="fas ${icon} problem-icon ${severity}"></i>
            <div class="problem-content">
                <div class="problem-message">${marker.message}</div>
                <div class="problem-location">Line ${marker.startLineNumber}, Column ${marker.startColumn}</div>
            </div>
        `;
        
        // Click to jump to error
        item.onclick = () => {
            const editor = editorState.editors[tabId].editor;
            editor.revealLineInCenter(marker.startLineNumber);
            editor.setPosition({
                lineNumber: marker.startLineNumber,
                column: marker.startColumn
            });
            editor.focus();
        };
        
        problemsList.appendChild(item);
    });
}

function toggleProblemsPanel() {
    const panel = document.getElementById('problems-panel');
    panel.classList.toggle('show');
}

function getActiveEditor() {
    if (!editorState.activeTabId) return null;
    return editorState.editors[editorState.activeTabId];
}

function updateTabModifiedState(tabId, isModified) {
    const tabData = editorState.editors[tabId];
    if (tabData) {
        tabData.modified = isModified;
        updateTabDisplay(tabId);
    }
}