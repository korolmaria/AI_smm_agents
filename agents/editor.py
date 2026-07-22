import re
from client import lm_client
from graph.state import ContentState, Stage, QualityDecision, create_failed_state
from config import (
    EDITOR_SYSTEM_PROMPT,
    EDITOR_EDIT_PROMPT_TEMPLATE,
    EDITOR_QUALITY_PROMPT_TEMPLATE,
    TEMPERATURE_PRECISE,
    MAX_TOKENS_EDIT,
    MAX_TOKENS
)


class Editor:
    """Агент-редактор: правит, оценивает и дает фидбек"""
    
    def __init__(self):
        self.name = "Editor"
        self.system_prompt = EDITOR_SYSTEM_PROMPT
        self.edit_template = EDITOR_EDIT_PROMPT_TEMPLATE
        self.quality_template = EDITOR_QUALITY_PROMPT_TEMPLATE
    
    def process(self, state: ContentState) -> ContentState:
        """Редактирует и проверяет качество контента"""
        print(f"\n📝 {self.name} начинает работу...")
        print("-" * 40)
        
        text_to_edit = state.draft or state.edited_draft
        if not text_to_edit:
            return create_failed_state(state, "Нет текста для редактирования")
        
        # Шаг 1: Редактируем текст
        state = self._edit_text(state, text_to_edit)
        if state.error:
            return state
        
        # Шаг 2: Проверяем качество
        state = self._quality_check(state)
        
        return state
    
    def _edit_text(self, state: ContentState, text: str) -> ContentState:
        """Редактирует текст"""
        print("🔍 Редактирование текста...")
        
        prompt = self.edit_template.format(text=text)
        
        try:
            response = lm_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=TEMPERATURE_PRECISE,
                max_tokens=MAX_TOKENS_EDIT
            )
            
            if response:
                state.edited_draft = response
                state.stage = Stage.EDITING
                print("✅ Текст отредактирован")
            else:
                return create_failed_state(state, "Не удалось отредактировать текст")
                
        except Exception as e:
            return create_failed_state(state, f"Ошибка при редактировании: {e}")
        
        return state
    
    def _quality_check(self, state: ContentState) -> ContentState:
        """Проверяет качество текста и принимает решение"""
        print("⭐ Проверка качества...")
        
        text = state.edited_draft or state.draft
        prompt = self.quality_template.format(text=text)
        
        try:
            response = lm_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=TEMPERATURE_PRECISE,
                max_tokens=500
            )
            
            if not response:
                state.quality_decision = QualityDecision.RETRY
                state.editor_feedback = "Ошибка оценки, отправляем на доработку"
                return state
            
            # Парсим решение
            self._parse_quality_response(state, response)
            state.stage = Stage.QUALITY_CHECK
            
            print(f"📊 Оценка: {state.quality_score}/10")
            print(f"✅ Решение: {state.quality_decision.value}")
            
        except Exception as e:
            state.quality_decision = QualityDecision.RETRY
            state.editor_feedback = f"Ошибка при проверке: {e}"
        
        return state
    
    def _parse_quality_response(self, state: ContentState, response: str):
        """Парсит ответ редактора - улучшенная версия"""
        
        # 1. Ищем среднюю оценку (разные форматы)
        score_patterns = [
            r'СРЕДНЯЯ ОЦЕНКА:\s*(\d+\.?\d*)',
            r'Средняя оценка:\s*(\d+\.?\d*)',
            r'средняя оценка:\s*(\d+\.?\d*)',
            r'Оценка:\s*(\d+\.?\d*)',
            r'(\d+\.?\d+)\s*/\s*10',
            r'(\d+)\s*из\s*10',
        ]
        
        score = None
        for pattern in score_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                break
        
        if score is not None:
            state.quality_score = score
        else:
            # Если не нашли оценку - ищем ключевые слова
            if "APPROVE" in response.upper():
                state.quality_score = 8.0
            elif "RETRY" in response.upper():
                state.quality_score = 5.0
            else:
                state.quality_score = 5.0
        
        # 2. Извлекаем рекомендации
        feedback = None
        feedback_patterns = [
            r'РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:\s*(.*?)(?=ФИНАЛЬНОЕ РЕШЕНИЕ|$)',
            r'Рекомендации:\s*(.*?)(?=Финальное решение|$)',
            r'СЛАБЫЕ СТОРОНЫ:\s*(.*?)(?=Рекомендации|ФИНАЛЬНОЕ|$)',
        ]
        
        for pattern in feedback_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                feedback = match.group(1).strip()[:500]
                break
        
        if feedback:
            state.editor_feedback = feedback
        else:
            # Если не нашли рекомендации - берем последние 300 символов
            state.editor_feedback = response[-300:] if len(response) > 300 else response
        
        # 3. Определяем решение
        if "APPROVE" in response.upper():
            state.quality_decision = QualityDecision.APPROVE
        else:
            state.quality_decision = QualityDecision.RETRY
        
        # 4. Если оценка >= 7, но решение RETRY - исправляем
        if state.quality_score >= 7.0 and state.quality_decision == QualityDecision.RETRY:
            state.quality_decision = QualityDecision.APPROVE
        
        # 5. Если оценка < 7, но решение APPROVE - исправляем
        if state.quality_score < 7.0 and state.quality_decision == QualityDecision.APPROVE:
            state.quality_decision = QualityDecision.RETRY