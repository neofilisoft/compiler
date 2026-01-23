"""
AI Assistant Integration
Supports: ChatGPT (OpenAI), Gemini (Google), Claude (Anthropic)
"""
import os
from config import AI_CONFIG

class AIAssistant:
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'gemini': GeminiProvider(),
            'claude': ClaudeProvider()
        }
        
    def get_available_providers(self):
        """Return list of enabled AI providers"""
        return [
            name for name, config in AI_CONFIG.items() 
            if config.get('enabled', False)
        ]
    
    def chat(self, provider, message, context=None):
        """
        Send message to AI provider
        Args:
            provider: 'openai', 'gemini', or 'claude'
            message: User message
            context: Optional code context
        Returns:
            (success, response, error)
        """
        if provider not in self.providers:
            return False, None, f"Unknown provider: {provider}"
        
        if not AI_CONFIG[provider].get('enabled', False):
            return False, None, f"{provider} is not enabled. Check config.py"
        
        return self.providers[provider].send_message(message, context)
    
    def explain_code(self, provider, code, language):
        """Ask AI to explain code"""
        prompt = f"Explain this {language} code:\n\n```{language}\n{code}\n```"
        return self.chat(provider, prompt)
    
    def fix_error(self, provider, code, error, language):
        """Ask AI to fix code error"""
        prompt = f"Fix this error in {language} code:\n\nCode:\n```{language}\n{code}\n```\n\nError:\n{error}"
        return self.chat(provider, prompt)
    
    def generate_code(self, provider, description, language):
        """Ask AI to generate code"""
        prompt = f"Write {language} code for: {description}"
        return self.chat(provider, prompt)


class OpenAIProvider:
    """ChatGPT (OpenAI) Integration"""
    
    def send_message(self, message, context=None):
        try:
            import openai
            
            api_key = AI_CONFIG['openai']['api_key']
            if not api_key:
                return False, None, "OpenAI API key not configured"
            
            openai.api_key = api_key
            
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": message})
            
            response = openai.ChatCompletion.create(
                model=AI_CONFIG['openai']['model'],
                messages=messages
            )
            
            return True, response.choices[0].message.content, None
            
        except ImportError:
            return False, None, "OpenAI library not installed. Run: pip install openai"
        except Exception as e:
            return False, None, str(e)


class GeminiProvider:
    """Google Gemini Integration"""
    
    def send_message(self, message, context=None):
        try:
            import google.generativeai as genai
            
            api_key = AI_CONFIG['gemini']['api_key']
            if not api_key:
                return False, None, "Gemini API key not configured"
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(AI_CONFIG['gemini']['model'])
            
            full_prompt = message
            if context:
                full_prompt = f"{context}\n\n{message}"
            
            response = model.generate_content(full_prompt)
            return True, response.text, None
            
        except ImportError:
            return False, None, "Google AI library not installed. Run: pip install google-generativeai"
        except Exception as e:
            return False, None, str(e)


class ClaudeProvider:
    """Anthropic Claude Integration"""
    
    def send_message(self, message, context=None):
        try:
            import anthropic
            
            api_key = AI_CONFIG['claude']['api_key']
            if not api_key:
                return False, None, "Claude API key not configured"
            
            client = anthropic.Anthropic(api_key=api_key)
            
            full_message = message
            if context:
                full_message = f"{context}\n\n{message}"
            
            response = client.messages.create(
                model=AI_CONFIG['claude']['model'],
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": full_message}
                ]
            )
            
            return True, response.content[0].text, None
            
        except ImportError:
            return False, None, "Anthropic library not installed. Run: pip install anthropic"
        except Exception as e:
            return False, None, str(e)


# Singleton instance
ai_assistant = AIAssistant()