"""
Configuration file for NOC
"""
import os

APP_VERSION = "3.0.0"
APP_NAME = "Neofilisoft Open Compiler"

# Flask Configuration
SECRET_KEY = 'noc_secret_key_2024'
FLASK_PORT = 5000
DEBUG_MODE = False

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMP_BUILD_DIR = os.path.join(BASE_DIR, 'temp_build')
EXTENSIONS_DIR = os.path.join(BASE_DIR, 'extensions')

# Language Support
SUPPORTED_LANGUAGES = [
    'python', 'cpp', 'csharp', 'java', 'javascript', 
    'sql', 'rust', 'lua', 'bash', 'zig', 'scala', 'go'
]

# Compiler Paths (Windows)
COMPILER_PATHS = {
    'cpp': 'g++',
    'csharp': 'csc',
    'java': 'javac',
    'rust': 'rustc',
    'go': 'go',
    'zig': 'zig',
    'scala': 'scala',
    'bash': r'C:\Program Files\Git\bin\bash.exe',  # Git Bash on Windows
    'bash_wsl': r'C:\Windows\System32\bash.exe'     # WSL
}

# AI API Configuration (to be filled by user)
AI_CONFIG = {
    'openai': {
        'api_key': '',  # User should set: os.environ.get('OPENAI_API_KEY', '')
        'model': 'gpt-4',
        'enabled': False
    },
    'gemini': {
        'api_key': '',  # User should set: os.environ.get('GEMINI_API_KEY', '')
        'model': 'gemini-pro',
        'enabled': False
    },
    'claude': {
        'api_key': '',  # User should set: os.environ.get('ANTHROPIC_API_KEY', '')
        'model': 'claude-3-sonnet-20240229',
        'enabled': False
    }
}

MONACO_SETTINGS = {
    'theme': 'vs-dark',
    'fontSize': 14,
    'minimap': True,
    'wordWrap': 'on',
    'autoSave': True,
    'formatOnPaste': True,
    'formatOnType': True
}

EXTENSIONS_ENABLED = True
DEFAULT_EXTENSIONS = [
    'cpp_extension',
    'csharp_extension', 
    'debugger_sdk'
]