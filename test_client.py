# test_client.py
from client import lm_client
from config import LM_STUDIO_URL

print("=" * 60)
print("🧪 ТЕСТ ПОДКЛЮЧЕНИЯ К LM STUDIO")
print("=" * 60)
print(f"📍 URL: {LM_STUDIO_URL}\n")

# Тест 1: Простой запрос
print("📝 Тест 1: Простой запрос без системного промпта")
print("-" * 40)

response = lm_client.generate(
    prompt="Скажи 'Привет, мир!'",
    max_tokens=20,
    temperature=0.3
)

if response:
    print(f"✅ Ответ: {response}")
else:
    print("❌ Пустой ответ")

print("\n" + "=" * 60)

# Тест 2: Запрос с системным промптом
print("📝 Тест 2: Запрос с системным промптом")
print("-" * 40)

response = lm_client.generate(
    prompt="Что такое искусственный интеллект?",
    system_prompt="Ты - полезный ассистент. Отвечай кратко в 1-2 предложениях.",
    max_tokens=50,
    temperature=0.3
)

if response:
    print(f"✅ Ответ: {response}")
else:
    print("❌ Пустой ответ")

print("\n" + "=" * 60)
print("✅ Тест завершен")