# debug_workflow.py
from client import lm_client
from graph.state import create_initial_state, Stage, create_failed_state
from config import RESEARCHER_SYSTEM_PROMPT, TEMPERATURE_DEFAULT, MAX_TOKENS, DEBUG

def test_research():
    """Тестируем только шаг исследования"""
    print("=" * 60)
    print("🧪 ТЕСТ ШАГА RESEARCH")
    print("=" * 60)
    
    # Создаем состояние
    state = create_initial_state("Как начать заниматься спортом дома")
    
    print(f"\n📌 Тема: {state.topic}")
    print(f"📌 System prompt: {RESEARCHER_SYSTEM_PROMPT[:50]}...")
    print("-" * 40)
    
    # Простой промпт
    prompt = f"Проведи исследование по теме: {state.topic}. Напиши 3-5 предложений с ключевыми фактами."
    
    print(f"\n📤 Отправка запроса...")
    print(f"   Prompt: {prompt}")
    print(f"   Temperature: {TEMPERATURE_DEFAULT}")
    print(f"   Max tokens: {MAX_TOKENS}")
    print("-" * 40)
    
    try:
        response = lm_client.generate(
            prompt=prompt,
            system_prompt=RESEARCHER_SYSTEM_PROMPT,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE_DEFAULT
        )
        
        print(f"\n📥 Получен ответ:")
        print(f"   Тип: {type(response)}")
        print(f"   Длина: {len(response) if response else 0}")
        print(f"   Содержание: {repr(response[:200]) if response else 'EMPTY'}")
        
        if response and response.strip():
            print("\n✅ УСПЕХ! Ответ получен:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            return True
        else:
            print("\n❌ ОТВЕТ ПУСТОЙ!")
            return False
            
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_research()
    if success:
        print("\n🎉 Тест пройден! Проблема в другом месте.")
    else:
        print("\n❌ Тест не пройден! Проблема в client.py или LM Studio.")