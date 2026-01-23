"""
Compiler and Code Execution Handler
"""
import subprocess
import os
import platform
from config import TEMP_BUILD_DIR, COMPILER_PATHS
from utils import ensure_directory, get_bash_path, get_language_extension

class CompilerHandler:
    def __init__(self):
        self.temp_dir = ensure_directory(TEMP_BUILD_DIR)
        
    def compile_and_run(self, code, language):
        """
        Compile (if needed) and return command to run
        Returns: (success, command, error_message)
        """
        try:
            if language == 'python':
                return self._handle_python(code)
            elif language == 'javascript':
                return self._handle_javascript(code)
            elif language == 'lua':
                return self._handle_lua(code)
            elif language == 'sql':
                return self._handle_sql(code)
            elif language == 'bash':
                return self._handle_bash(code)
            elif language == 'cpp':
                return self._handle_cpp(code)
            elif language == 'csharp':
                return self._handle_csharp(code)
            elif language == 'java':
                return self._handle_java(code)
            elif language == 'go':
                return self._handle_go(code)
            elif language == 'rust':
                return self._handle_rust(code)
            elif language == 'zig':
                return self._handle_zig(code)
            elif language == 'scala':
                return self._handle_scala(code)
            else:
                return False, None, f"Language '{language}' not supported"
        except Exception as e:
            return False, None, str(e)
    
    def _write_file(self, filename, content):
        """Write content to file"""
        path = os.path.join(self.temp_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def _handle_python(self, code):
        path = self._write_file('script.py', code)
        return True, ['python', '-u', path], None
    
    def _handle_javascript(self, code):
        path = self._write_file('script.js', code)
        return True, ['node', path], None
    
    def _handle_lua(self, code):
        path = self._write_file('script.lua', code)
        return True, ['lua', path], None
    
    def _handle_bash(self, code):
        path = self._write_file('script.sh', code)
        bash_path = get_bash_path()
        
        if not bash_path:
            return False, None, "Bash not found. Install Git Bash or WSL."
        
        if platform.system() == 'Windows' and 'System32' in bash_path:
            # WSL - convert path
            wsl_path = path.replace('\\', '/').replace('C:', '/mnt/c')
            return True, [bash_path, '-c', f'bash {wsl_path}'], None
        else:
            return True, [bash_path, path], None
    
    def _handle_sql(self, code):
        """SQLite in-memory database"""
        sql_runner = f'''
import sqlite3
import sys

try:
    con = sqlite3.connect(":memory:")
    cur = con.cursor()
    script = """{code}"""
    cur.executescript(script)
    
    # If there's a SELECT, fetch and display results
    if "SELECT" in script.upper():
        for row in cur.fetchall():
            print(row)
    
    con.commit()
except Exception as e:
    print(f"SQL Error: {{e}}")
    sys.exit(1)
finally:
    con.close()
'''
        path = self._write_file('sql_runner.py', sql_runner)
        return True, ['python', '-u', path], None
    
    def _handle_cpp(self, code):
        src = self._write_file('main.cpp', code)
        exe = os.path.join(self.temp_dir, 'main.exe')
        
        # Compile
        result = subprocess.run(
            ['g++', src, '-o', exe],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False, None, f"Compilation Error:\n{result.stderr}"
        
        return True, [exe], None
    
    def _handle_csharp(self, code):
        src = self._write_file('Program.cs', code)
        exe = os.path.join(self.temp_dir, 'Program.exe')
        
        # Compile
        result = subprocess.run(
            ['csc', f'/out:{exe}', src],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False, None, f"Compilation Error:\n{result.stdout}"
        
        return True, [exe], None
    
    def _handle_java(self, code):
        src = self._write_file('Main.java', code)
        
        # Compile
        result = subprocess.run(
            ['javac', src],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False, None, f"Compilation Error:\n{result.stderr}"
        
        return True, ['java', '-cp', self.temp_dir, 'Main'], None
    
    def _handle_go(self, code):
        src = self._write_file('main.go', code)
        return True, ['go', 'run', src], None
    
    def _handle_rust(self, code):
        src = self._write_file('main.rs', code)
        exe = os.path.join(self.temp_dir, 'main.exe')
        
        # Compile
        result = subprocess.run(
            ['rustc', src, '-o', exe],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False, None, f"Compilation Error:\n{result.stderr}"
        
        return True, [exe], None
    
    def _handle_zig(self, code):
        src = self._write_file('main.zig', code)
        return True, ['zig', 'run', src], None
    
    def _handle_scala(self, code):
        src = self._write_file('Main.scala', code)
        return True, ['scala', src], None