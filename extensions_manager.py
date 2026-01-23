"""
Extensions Manager
Plugin system for language-specific features
"""
import os
import importlib
from config import EXTENSIONS_DIR, DEFAULT_EXTENSIONS, EXTENSIONS_ENABLED

class ExtensionsManager:
    def __init__(self):
        self.extensions = {}
        self.enabled = EXTENSIONS_ENABLED
        
        if self.enabled:
            self._load_extensions()
    
    def _load_extensions(self):
        """Load all extensions from extensions directory"""
        if not os.path.exists(EXTENSIONS_DIR):
            os.makedirs(EXTENSIONS_DIR)
            return
        
        for ext_name in DEFAULT_EXTENSIONS:
            try:
                # Import extension module
                module = importlib.import_module(f'extensions.{ext_name}')
                
                # Get extension class
                ext_class_name = ''.join(word.capitalize() for word in ext_name.split('_'))
                ext_class = getattr(module, ext_class_name)
                
                # Instantiate
                self.extensions[ext_name] = ext_class()
                print(f"✓ Loaded extension: {ext_name}")
                
            except Exception as e:
                print(f"✗ Failed to load extension {ext_name}: {e}")
    
    def get_extension(self, name):
        """Get extension by name"""
        return self.extensions.get(name)
    
    def get_all_extensions(self):
        """Get all loaded extensions"""
        return self.extensions
    
    def call_extension_method(self, ext_name, method_name, *args, **kwargs):
        """Call a method on an extension"""
        ext = self.get_extension(ext_name)
        if ext and hasattr(ext, method_name):
            method = getattr(ext, method_name)
            return method(*args, **kwargs)
        return None


class BaseExtension:
    """Base class for all extensions"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
    
    def get_info(self):
        """Return extension information"""
        return {
            'name': self.name,
            'version': self.version
        }
    
    def on_code_change(self, code, language):
        """Called when code changes"""
        pass
    
    def on_compile(self, code, language):
        """Called before compilation"""
        pass
    
    def on_run(self, code, language):
        """Called before execution"""
        pass
    
    def get_diagnostics(self, code, language):
        """Return syntax/semantic diagnostics"""
        return []


# Extension Manager Singleton
extensions_manager = ExtensionsManager()