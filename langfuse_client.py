# langfuse_client.py
from langfuse import Langfuse
from config import (
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_HOST,
    LANGFUSE_DEBUG
)

# Инициализация Langfuse
langfuse = None

if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    try:
        langfuse = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
            debug=LANGFUSE_DEBUG
        )
        print("✅ Langfuse инициализирован")
        print(f"   Host: {LANGFUSE_HOST}")
        print(f"   Public Key: {LANGFUSE_PUBLIC_KEY[:10]}...")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации Langfuse: {e}")
else:
    print("⚠️ Langfuse ключи не найдены. Логирование отключено.")

def get_langfuse():
    return langfuse

def flush_langfuse():
    if langfuse:
        try:
            print("📤 [LANGFUSE] Принудительный сброс буфера...")
            langfuse.flush()
            print("✅ [LANGFUSE] Буфер сброшен!")
            return True
        except Exception as e:
            print(f"⚠️ Ошибка сброса Langfuse: {e}")
            return False
    return False