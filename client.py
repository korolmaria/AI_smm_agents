import requests
import time
from typing import Optional
from config import (
    LM_STUDIO_URL, 
    LM_STUDIO_API_KEY, 
    MAX_TOKENS, 
    TEMPERATURE_DEFAULT,
    TOP_P
)

class LMStudioClient:
    def __init__(self, base_url: str = LM_STUDIO_URL):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LM_STUDIO_API_KEY}"
        }
    
    def generate(self, 
                 prompt: str,
                 system_prompt: Optional[str] = None,
                 max_tokens: int = MAX_TOKENS,
                 temperature: float = TEMPERATURE_DEFAULT,
                 top_p: float = TOP_P) -> str:
        """Отправка запроса к LM Studio"""
        
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            return content
            
        except requests.exceptions.Timeout:
            error_msg = f"Таймаут подключения к {self.base_url}"
            print(f"❌ {error_msg}")
            return ""
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка: {error_msg}")
            return ""

# Создаем глобальный экземпляр клиента
lm_client = LMStudioClient()