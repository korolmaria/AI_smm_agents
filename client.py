# client.py
import requests
import json
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
        
        print(f"\n📤 [CLIENT] Отправка запроса...")
        print(f"   URL: {self.base_url}/chat/completions")
        print(f"   Temperature: {temperature}")
        print(f"   Max tokens: {max_tokens}")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            print(f"📥 [CLIENT] HTTP Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ [CLIENT] Ошибка: {response.text}")
                response.raise_for_status()
            
            result = response.json()
            
            # Проверяем структуру ответа
            if "choices" not in result:
                print(f"❌ [CLIENT] Неверный ответ: {result}")
                return ""
            
            if not result["choices"]:
                print(f"❌ [CLIENT] Нет choices в ответе")
                return ""
            
            content = result["choices"][0]["message"]["content"]
            print(f"✅ [CLIENT] Ответ получен ({len(content)} символов)")
            return content
            
        except requests.exceptions.Timeout:
            print("❌ [CLIENT] Таймаут подключения")
            return ""
        except requests.exceptions.ConnectionError:
            print(f"❌ [CLIENT] Не удалось подключиться к {self.base_url}")
            print("   Проверьте: запущен ли LM Studio и включен ли Server")
            return ""
        except requests.exceptions.HTTPError as e:
            print(f"❌ [CLIENT] HTTP ошибка: {e}")
            return ""
        except Exception as e:
            print(f"❌ [CLIENT] Неизвестная ошибка: {e}")
            import traceback
            traceback.print_exc()
            return ""

# Создаем глобальный экземпляр клиента
lm_client = LMStudioClient()