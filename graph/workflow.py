from typing import Dict, Any, Optional
from .state import (
    ContentState, 
    Stage, 
    create_initial_state, 
    create_success_state,
    create_failed_state,
    QualityDecision
)
from agents import Strategist, Copywriter, Editor, Publisher
from client import lm_client
from config import (
    TEMPERATURE_DEFAULT,
    MAX_TOKENS,
    MAX_RETRIES,
    DEBUG
)


class Workflow:
    """Workflow с условными переходами и агентами"""
    
    def __init__(self):
        self.max_retries = MAX_RETRIES
        
        # Инициализируем агентов
        self.strategist = Strategist()
        self.copywriter = Copywriter()
        self.editor = Editor()
        self.publisher = Publisher()
    
    def run(self, topic: str) -> ContentState:
        """Запуск workflow"""
        print(f"\n🚀 Запуск workflow для темы: {topic}")
        print("=" * 60)
        
        # Создаем начальное состояние
        state = create_initial_state(topic)
        state.total_steps = 6
        
        # Шаг 1: Исследование
        state = self._do_research(state)
        if state.error:
            return state
        
        # Шаг 2: Стратег
        state = self.strategist.process(state)
        if state.error:
            return state
        
        # Основной цикл
        while state.attempt_number < self.max_retries:
            state.attempt_number += 1
            print(f"\n🔄 Попытка {state.attempt_number} из {self.max_retries}")
            
            # Шаг 3: Копирайтер
            state = self.copywriter.process(state)
            if state.error:
                return state
            
            # Шаг 4: Редактор
            state = self.editor.process(state)
            if state.error:
                return state
            
            # Шаг 5: Проверка решения
            if state.quality_decision == QualityDecision.APPROVE:
                print("✅ Контент одобрен! Отправляем на публикацию.")
                
                # Шаг 6: Паблишер
                state = self.publisher.process(state)
                if state.error:
                    return state
                
                state = create_success_state(state)
                break
                
            elif state.quality_decision == QualityDecision.RETRY:
                print("🔄 Контент требует доработки. Отправляем обратно копирайтеру.")
                state.stage = Stage.CONTENT
                continue
            else:
                state = create_failed_state(state, "Не удалось пройти проверку качества")
                break
        
        if not state.is_complete and not state.error:
            state = create_failed_state(
                state, 
                f"Превышено количество попыток ({self.max_retries})"
            )
            print(f"\n❌ Превышено количество попыток. Workflow завершен с ошибкой.")
        
        return state
    
    def _do_research(self, state: ContentState) -> ContentState:
        """Шаг 1: Исследование (упрощенная версия)"""
        print(f"\n📌 Шаг 1: RESEARCH (исследование)")
        print("-" * 40)
        
        # Используем простой промпт напрямую
        prompt = f"Проведи исследование по теме: {state.topic}. Напиши 3-5 предложений с ключевыми фактами."
        
        print(f"🔄 Отправка запроса...")
        
        try:
            response = lm_client.generate(
                prompt=prompt,
                system_prompt="Ты - исследователь. Отвечай кратко и структурированно.",
                max_tokens=500,
                temperature=TEMPERATURE_DEFAULT
            )
            
            print(f"📥 Ответ получен: {response[:50] if response else 'EMPTY'}...")
            
            if response and response.strip():
                state.research_material = response
                state.stage = Stage.RESEARCH
                print("✅ Исследование завершено")
                print(f"📄 {response[:200]}...")
            else:
                print("❌ Получен пустой ответ от модели")
                return create_failed_state(state, "Не удалось получить ответ от модели (пустой ответ)")
                
        except Exception as e:
            print(f"❌ Ошибка при исследовании: {e}")
            import traceback
            traceback.print_exc()
            return create_failed_state(state, f"Ошибка при исследовании: {e}")
        
        return state