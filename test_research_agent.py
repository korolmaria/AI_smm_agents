from langfuse import Langfuse
from client import lm_client
from config import (
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_HOST,
    LANGFUSE_DEBUG,
    RESEARCHER_SYSTEM_PROMPT
)
import time
import uuid

# Инициализация Langfuse
langfuse = Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST,
    debug=True
)

def flush_and_wait():
    """Сброс буфера с ожиданием"""
    print("\n📤 [LANGFUSE] Сброс буфера...")
    langfuse.flush()
    print("✅ [LANGFUSE] Буфер сброшен!")
    time.sleep(2)  # Даем время на отправку


def test_research():
    """Тест агента исследователя без декораторов"""
    
    print("=" * 60)
    print("🧪 ТЕСТ АГЕНТА ИССЛЕДОВАТЕЛЯ С LANGFUSE")
    print("=" * 60)
    
    # Создаем trace напрямую
    trace_id = str(uuid.uuid4())
    trace = langfuse.trace(
        id=trace_id,
        name="test_research_agent",
        input={"topic": "Как начать заниматься спортом дома"},
        metadata={
            "test_name": "research_agent_test",
            "timestamp": time.time()
        }
    )
    
    print(f"\n🔍 Trace ID: {trace.id}")
    
    # Создаем span для исследования
    span = trace.span(
        name="research_span",
        input={
            "topic": "Как начать заниматься спортом дома",
            "system_prompt": RESEARCHER_SYSTEM_PROMPT[:100] + "..." if RESEARCHER_SYSTEM_PROMPT else "None"
        },
        metadata={
            "start_time": time.time()
        }
    )
    print("🔍 [LANGFUSE] Span создан: research_span")
    
    # Формируем промпт
    topic = "Как начать заниматься спортом дома"
    prompt = f"Проведи исследование по теме: {topic}. Напиши 5-7 предложений с ключевыми фактами, статистикой и трендами."
    
    print(f"\n📤 Отправка запроса к LM Studio...")
    print(f"   Тема: {topic}")
    
    start_time = time.time()
    
    try:
        # Запрос к LM Studio
        response = lm_client.generate(
            prompt=prompt,
            system_prompt=RESEARCHER_SYSTEM_PROMPT or "Ты - исследователь. Отвечай кратко и структурированно.",
            max_tokens=500,
            temperature=0.3
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        if response and response.strip():
            print(f"✅ Ответ получен ({len(response)} символов)")
            print(f"   Время: {duration_ms:.0f} мс")
            
            # Обновляем span с результатом
            span.update(
                output={
                    "research": response[:500],
                    "length": len(response),
                    "success": True
                },
                metadata={
                    "duration_ms": duration_ms,
                    "status": "success"
                }
            )
            span.end()
            print("🔍 [LANGFUSE] Span завершен: research_span")
            
            # Обновляем trace
            trace.update(
                output={
                    "status": "success",
                    "research_length": len(response)
                },
                metadata={
                    "test_complete": True,
                    "timestamp": time.time()
                }
            )
            print(f"🔍 [LANGFUSE] Trace обновлен: {trace.id}")
            
        else:
            error_msg = "Не удалось получить ответ от модели"
            span.update(
                output={"error": error_msg, "success": False},
                metadata={"duration_ms": duration_ms, "status": "error"}
            )
            span.end()
            trace.update(
                output={"status": "failed", "error": error_msg},
                metadata={"test_complete": True}
            )
            response = None
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка: {error_msg}")
        
        span.update(
            output={"error": error_msg, "success": False},
            metadata={"duration_ms": (time.time() - start_time) * 1000, "status": "error"}
        )
        span.end()
        trace.update(
            output={"status": "failed", "error": error_msg},
            metadata={"test_complete": True}
        )
        response = None
    
    # Сброс буфера
    flush_and_wait()
    
    print("\n" + "=" * 60)
    if response:
        print("✅ ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
        print(f"\n📄 РЕЗУЛЬТАТ ИССЛЕДОВАНИЯ:")
        print("-" * 40)
        print(response)
        print("-" * 40)
    else:
        print("❌ ТЕСТ ЗАВЕРШЕН С ОШИБКОЙ")
    
    print(f"\n🔍 Trace ID: {trace.id}")
    print(f"🔗 Ссылка: https://cloud.langfuse.com/traces/{trace.id}")
    print("=" * 60)
    
    return response


if __name__ == "__main__":
    test_research()