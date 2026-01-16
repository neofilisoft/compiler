from flask import Flask, render_template
from flask_socketio import SocketIO
import subprocess
import os
import sys
import threading
import time

try:
    import webview
except ImportError:
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

current_process = None
process_lock = threading.Lock()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

app.template_folder = resource_path('templates')

@app.route('/')
def index():
    return render_template('index.html')

def read_output(process):
    try:
        for c in iter(lambda: process.stdout.read(1), ''):
            socketio.emit('term_output', {'data': c})
    except Exception as e:
        print(f"Reader Error: {e}")
    finally:
        if process.stdout:
            process.stdout.close()
        socketio.emit('term_stop', {'data': '\n[Program Finished]'})

@socketio.on('run_code')
def handle_run_code(data):
    global current_process
    code = data.get('code')
    script_path = resource_path("temp_script.py")
   
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        with process_lock:
            if current_process and current_process.poll() is None:
                current_process.kill()

            current_process = subprocess.Popen(
                ['python', '-u', script_path], 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                startupinfo=startupinfo
            )
        t = threading.Thread(target=read_output, args=(current_process,))
        t.daemon = True
        t.start()
        
    except Exception as e:
        socketio.emit('term_output', {'data': f"System Error: {str(e)}"})

@socketio.on('send_input')
def handle_input(data):
    global current_process
    user_input = data.get('input')
    
    with process_lock:
        if current_process and current_process.poll() is None:
            try:
                current_process.stdin.write(user_input + "\n")
                current_process.stdin.flush()
            except Exception as e:
                print(f"Input Error: {e}")

def start_server():
    socketio.run(app, port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    time.sleep(1)

    try:
        webview.create_window(
            'NOC - Neofilisoft Open Compiler (Real-time)', 
            'http://127.0.0.1:5000',
            width=1000, height=700,
            background_color='#1e1e1e'
        )
        webview.start()
    except ImportError:
        import webbrowser
        webbrowser.open('http://127.0.0.1:5000')
        while True: time.sleep(1)