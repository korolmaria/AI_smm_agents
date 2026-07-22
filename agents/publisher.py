from client import lm_client
from graph.state import ContentState, Stage, create_failed_state
from config import (
    PUBLISHER_SYSTEM_PROMPT,
    PUBLISHER_PROMPT_TEMPLATE,
    TEMPERATURE_DEFAULT,
    MAX_TOKENS
)


class Publisher:
    """Агент-паблишер: готовит контент к публикации"""
    
    def __init__(self):
        self.name = "Publisher"
        self.system_prompt = PUBLISHER_SYSTEM_PROMPT
        self.template = PUBLISHER_PROMPT_TEMPLATE
    
    def process(self, state: ContentState) -> ContentState:
        """Готовит контент к публикации"""
        print(f"\n📤 {self.name} начинает работу...")
        print("-" * 40)
        
        text = state.edited_draft or state.draft
        if not text:
            return create_failed_state(state, "Нет текста для публикации")
        
        prompt = self._build_prompt(state, text)
        
        try:
            response = lm_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=TEMPERATURE_DEFAULT,
                max_tokens=400
            )
            
            if response:
                metadata = self._parse_metadata(response)
                state.publish_metadata = metadata
                state.published = True
                state.stage = Stage.PUBLISHING
                print("✅ Контент готов к публикации")
                print(f"📋 Мета-описание: {metadata.get('meta_description', '')[:50]}...")
                print(f"🏷️ Теги: {metadata.get('tags', '')}")
            else:
                return create_failed_state(state, "Не удалось подготовить метаданные")
                
        except Exception as e:
            return create_failed_state(state, f"Ошибка при публикации: {e}")
        
        return state
    
    def _build_prompt(self, state: ContentState, text: str) -> str:
        """Формирует промпт из шаблона"""
        # Обрезаем текст для промпта
        text_preview = text[:1000] + "..." if len(text) > 1000 else text
        
        return self.template.format(
            topic=state.topic,
            content_type=state.content_type.value,
            text=text_preview
        )
    
    def _parse_metadata(self, response: str) -> dict:
        """Парсит метаданные из ответа"""
        metadata = {}
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'ЗАГОЛОВОК:' in line:
                metadata['title'] = line.replace('ЗАГОЛОВОК:', '').strip()
            elif 'МЕТА-ОПИСАНИЕ:' in line:
                metadata['meta_description'] = line.replace('МЕТА-ОПИСАНИЕ:', '').strip()
            elif 'ТЕГИ:' in line:
                metadata['tags'] = line.replace('ТЕГИ:', '').strip()
            elif 'CTA:' in line:
                metadata['cta'] = line.replace('CTA:', '').strip()
        
        return metadata