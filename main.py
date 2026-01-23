"""
Main Entry Point for NOC (Neofilisoft Open Compiler)
"""
import threading
import time
import subprocess
import sys
import importlib

# Ensure dependencies
def ensure_dependencies():
    required_packages = [
        'flask', 
        'flask-socketio', 
        'PySide6', 
        'pywebview'
    ]
    
    for package in required_packages:
        try:
            importlib.import_module(package.lower().replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])

ensure_dependencies()

from app import start_server
from config import APP_NAME, APP_VERSION, FLASK_PORT

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    import webbrowser

def main():
    print(f"Starting {APP_NAME} v{APP_VERSION}...")
    
    # Start Flask server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(1.5)
    
    url = f'http://127.0.0.1:{FLASK_PORT}'
    
    # Launch UI
    if WEBVIEW_AVAILABLE:
        print("Launching desktop window...")
        webview.create_window(
            APP_NAME,
            url,
            width=1400,
            height=900,
            background_color='#1e1e1e',
            resizable=True,
            frameless=False
        )
        webview.start()
    else:
        print("pywebview not available. Opening in browser...")
        webbrowser.open(url)
        
        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == '__main__':
    main()