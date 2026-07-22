# test_langfuse.py
from langfuse.decorators import observe
from langfuse_client import flush_langfuse
from client import lm_client
import time

@observe(name="test_workflow_decorator")
def test_workflow():
    """Тест с декораторами"""
    print("=" * 60)
    print("🧪 ТЕСТ LANGFUSE С ДЕКОРАТОРАМИ")
    print("=" * 60)
    
    @observe(name="test_sub_function")
    def test_sub():
        print("🔍 [LANGFUSE] Span: test_sub_function")
        
        response = lm_client.generate(
            prompt="Скажи 'Привет, мир!' в одной фразе.",
            max_tokens=20,
            temperature=0.3
        )
        
        print(f"✅ Ответ: {response}")
        return response
    
    result = test_sub()
    
    flush_langfuse()
    
    print("\n" + "=" * 60)
    print("✅ Тест завершен!")
    print("📊 Проверь в Langfuse: https://cloud.langfuse.com/traces")
    print("=" * 60)

if __name__ == "__main__":
    test_workflow()