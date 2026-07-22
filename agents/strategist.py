from client import lm_client
from graph.state import ContentState, Stage, create_failed_state
from config import (
    STRATEGIST_SYSTEM_PROMPT,
    STRATEGIST_PROMPT_TEMPLATE,
    TEMPERATURE_DEFAULT,
    MAX_TOKENS
)


class Strategist:
    """Агент-стратег: разрабатывает стратегию контента"""
    
    def __init__(self):
        self.name = "Strategist"
        self.system_prompt = STRATEGIST_SYSTEM_PROMPT
        self.template = STRATEGIST_PROMPT_TEMPLATE
    
    def process(self, state: ContentState) -> ContentState:
        """Разрабатывает стратегию на основе исследования"""
        print(f"\n🎯 {self.name} начинает работу...")
        print("-" * 40)
        
        if not state.research_material:
            return create_failed_state(state, "Нет материалов исследования")
        
        # Формируем промпт из шаблона
        prompt = self._build_prompt(state)
        
        try:
            response = lm_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=TEMPERATURE_DEFAULT,
                max_tokens=MAX_TOKENS
            )
            
            if response:
                state.strategy = response
                state.stage = Stage.STRATEGY
                print("✅ Стратегия разработана")
            else:
                return create_failed_state(state, "Не удалось создать стратегию")
                
        except Exception as e:
            return create_failed_state(state, f"Ошибка при создании стратегии: {e}")
        
        return state
    
    def _build_prompt(self, state: ContentState) -> str:
        """Формирует промпт из шаблона"""
        return self.template.format(
            topic=state.topic,
            audience=state.target_audience,
            research=state.research_material,
            content_type=state.content_type.value,
            tone=state.tone.value,
            style=state.style.value,
            length=state.length.value,
            keywords=', '.join(state.keywords) if state.keywords else 'не указаны'
        )