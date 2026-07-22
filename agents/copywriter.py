from client import lm_client
from graph.state import ContentState, Stage, create_failed_state
from config import (
    COPYWRITER_SYSTEM_PROMPT,
    COPYWRITER_PROMPT_TEMPLATE,
    TEMPERATURE_CREATIVE,
    TEMPERATURE_DEFAULT,
    MAX_TOKENS
)


class Copywriter:
    """Агент-копирайтер: создает контент"""
    
    def __init__(self):
        self.name = "Copywriter"
        self.system_prompt = COPYWRITER_SYSTEM_PROMPT
        self.template = COPYWRITER_PROMPT_TEMPLATE
    
    def process(self, state: ContentState) -> ContentState:
        """Создает контент на основе стратегии"""
        print(f"\n✍️ {self.name} начинает работу...")
        print("-" * 40)
        
        if not state.strategy:
            return create_failed_state(state, "Нет стратегии для создания контента")
        
        # Проверяем фидбек
        feedback_note = ""
        if state.editor_feedback:
            feedback_note = f"\n\nУЧТИ ЗАМЕЧАНИЯ РЕДАКТОРА:\n{state.editor_feedback}"
            print(f"📝 Учитываем фидбек редактора (попытка {state.attempt_number})")
        
        # Формируем промпт
        prompt = self._build_prompt(state, feedback_note)
        
        try:
            # Для творчества используем более высокую температуру
            temperature = TEMPERATURE_CREATIVE if not state.editor_feedback else TEMPERATURE_DEFAULT
            response = lm_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=temperature,
                max_tokens=MAX_TOKENS
            )
            
            if response:
                state.draft = response
                state.stage = Stage.CONTENT
                print("✅ Черновик создан")
            else:
                return create_failed_state(state, "Не удалось создать контент")
                
        except Exception as e:
            return create_failed_state(state, f"Ошибка при создании контента: {e}")
        
        return state
    
    def _build_prompt(self, state: ContentState, feedback_note: str) -> str:
        """Формирует промпт из шаблона"""
        return self.template.format(
            topic=state.topic,
            strategy=state.strategy,
            feedback=feedback_note,
            content_type=state.content_type.value,
            tone=state.tone.value,
            style=state.style.value,
            length=state.length.value,
            audience=state.target_audience
        )