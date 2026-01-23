"""
Main Flask Application
"""
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import subprocess
import threading
import os
from config import SECRET_KEY, FLASK_PORT, TEMPLATE_DIR, STATIC_DIR
from compiler_handler import CompilerHandler
from ai_assistant import ai_assistant
from extensions_manager import extensions_manager
from utils import resource_path

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

compiler = CompilerHandler()
current_process = None
process_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI Assistant API endpoint"""
    data = request.json
    provider = data.get('provider', 'openai')
    message = data.get('message', '')
    context = data.get('context', None)
    
    success, response, error = ai_assistant.chat(provider, message, context)
    
    return jsonify({
        'success': success,
        'response': response,
        'error': error
    })

@app.route('/api/ai/explain', methods=['POST'])
def ai_explain_code():
    """AI code explanation"""
    data = request.json
    provider = data.get('provider', 'openai')
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    success, response, error = ai_assistant.explain_code(provider, code, language)
    
    return jsonify({
        'success': success,
        'response': response,
        'error': error
    })

@app.route('/api/ai/fix', methods=['POST'])
def ai_fix_error():
    """AI error fixing"""
    data = request.json
    provider = data.get('provider', 'openai')
    code = data.get('code', '')
    error = data.get('error', '')
    language = data.get('language', 'python')
    
    success, response, error = ai_assistant.fix_error(provider, code, error, language)
    
    return jsonify({
        'success': success,
        'response': response,
        'error': error
    })

@app.route('/api/extensions', methods=['GET'])
def get_extensions():
    """Get loaded extensions"""
    exts = extensions_manager.get_all_extensions()
    return jsonify({
        'extensions': [ext.get_info() for ext in exts.values()]
    })

@socketio.on('run_code')
def handle_run_code(data):
    """Execute code"""
    global current_process
    
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    # Compile/prepare code
    success, cmd, error = compiler.compile_and_run(code, language)
    
    if not success:
        socketio.emit('term_output', {'data': error})
        socketio.emit('term_stop', {'data': '\n[Execution Failed]', 'success': False})
        return
    
    # Setup subprocess
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        startupinfo.creationflags = subprocess.CREATE_NO_WINDOW
    
    try:
        with process_lock:
            # Kill previous process if exists
            if current_process and current_process.poll() is None:
                current_process.kill()
            
            # Start new process
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUNBUFFERED"] = "1"
            
            current_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=startupinfo,
                env=env
            )
        
        # Start output reader thread
        threading.Thread(
            target=read_output, 
            args=(current_process,), 
            daemon=True
        ).start()
        
    except FileNotFoundError:
        socketio.emit('term_output', {
            'data': f"Error: Compiler/interpreter for '{language}' not found in PATH."
        })
        socketio.emit('term_stop', {'data': ''})
    except Exception as e:
        socketio.emit('term_output', {'data': f"Execution Error: {str(e)}"})
        socketio.emit('term_stop', {'data': ''})

@socketio.on('send_input')
def handle_input(data):
    """Send input to running process"""
    global current_process
    user_input = data.get('input', '')
    
    with process_lock:
        if current_process and current_process.poll() is None:
            try:
                current_process.stdin.write(user_input + '\n')
                current_process.stdin.flush()
            except Exception as e:
                print(f"Input Error: {e}")

def read_output(process):
    """Read process output and emit to frontend"""
    has_error = False
    return_code = 0
    
    def flush_buffer(buf):
        if buf:
            socketio.emit('term_output', {'data': ''.join(buf)})
            socketio.sleep(0)
        return []
    
    try:
        buffer = []
        while True:
            line = process.stdout.readline()
            if not line:
                flush_buffer(buffer)
                break
            
            buffer.append(line)
            if line.endswith('\n') or len(buffer) > 50:
                buffer = flush_buffer(buffer)
                
    except Exception as e:
        print(f"Stdout error: {e}")
    
    try:
        if process.stderr:
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                has_error = True
                socketio.emit('term_output', {'data': line})
                socketio.sleep(0)
    except Exception as e:
        print(f"Stderr error: {e}")
    
    try:
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        return_code = process.wait()
    except Exception as e:
        print(f"Cleanup error: {e}")
    
    if return_code != 0 or has_error:
        socketio.emit('term_stop', {
            'data': '\n[Execution Failed]', 
            'success': False
        })
    else:
        socketio.emit('term_stop', {
            'data': '\n[Execution Successful]', 
            'success': True
        })

def start_server():
    """Start Flask-SocketIO server"""
    socketio.run(app, port=FLASK_PORT, debug=False, allow_unsafe_werkzeug=True)