"""
Utility functions for NOC
"""
import os
import sys
import platform

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def ensure_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_bash_path():
    """Get bash executable path based on OS"""
    system = platform.system()
    
    if system == 'Windows':
        # Check for Git Bash
        git_bash = r'C:\Program Files\Git\bin\bash.exe'
        if os.path.exists(git_bash):
            return git_bash
        
        # Check for WSL
        wsl_bash = r'C:\Windows\System32\bash.exe'
        if os.path.exists(wsl_bash):
            return wsl_bash
        
        return None
    else:
        # Linux/Mac
        return 'bash'

def get_language_extension(language):
    """Get file extension for language"""
    extensions = {
        'python': '.py',
        'cpp': '.cpp',
        'csharp': '.cs',
        'java': '.java',
        'javascript': '.js',
        'sql': '.sql',
        'rust': '.rs',
        'lua': '.lua',
        'bash': '.sh',
        'zig': '.zig',
        'scala': '.scala',
        'go': '.go'
    }
    return extensions.get(language, '.txt')

def get_monaco_language(language):
    """Get Monaco editor language identifier"""
    mappings = {
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
    }
    return mappings.get(language, language)

def sanitize_filename(name):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name