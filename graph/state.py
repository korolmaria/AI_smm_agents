from typing import TypedDict, List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field


class Stage(str, Enum):
    """Этапы workflow"""
    RESEARCH = "research"
    STRATEGY = "strategy"
    CONTENT = "content"
    EDITING = "editing"
    QUALITY_CHECK = "quality_check"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentType(str, Enum):
    """Типы контента"""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    VIDEO_SCRIPT = "video_script"
    NEWSLETTER = "newsletter"
    SOCIAL_POST = "social_post"
    WHITEPAPER = "whitepaper"
    CASE_STUDY = "case_study"


class Tone(str, Enum):
    """Тон общения"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    NEUTRAL = "neutral"


class Style(str, Enum):
    """Стиль написания"""
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"
    NARRATIVE = "narrative"
    DESCRIPTIVE = "descriptive"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"


class ContentLength(str, Enum):
    """Длина контента"""
    SHORT = "short"      # до 300 слов
    MEDIUM = "medium"    # 300-700 слов
    LONG = "long"        # 700-1500 слов
    EXTRA_LONG = "extra_long"  # более 1500 слов


class QualityDecision(str, Enum):
    """Решение по качеству"""
    APPROVE = "approve"
    RETRY = "retry"
    REJECT = "reject"


@dataclass
class ContentState:
    """
    Состояние контента в процессе workflow.
    Использует dataclass для удобной работы с типами.
    """
    
    # === ВХОДНЫЕ ДАННЫЕ ===
    topic: str = ""
    """Тема контента"""
    
    content_type: ContentType = ContentType.ARTICLE
    """Тип контента"""
    
    target_audience: str = "general"
    """Целевая аудитория"""
    
    keywords: List[str] = field(default_factory=list)
    """Ключевые слова для SEO"""
    
    # === ПАРАМЕТРЫ ГЕНЕРАЦИИ ===
    tone: Tone = Tone.PROFESSIONAL
    """Тон общения"""
    
    style: Style = Style.INFORMATIVE
    """Стиль написания"""
    
    length: ContentLength = ContentLength.MEDIUM
    """Длина контента"""
    
    language: str = "ru"
    """Язык контента"""
    
    # === ПРОМЕЖУТОЧНЫЕ РЕЗУЛЬТАТЫ ===
    research_material: Optional[str] = None
    """Материалы исследования"""
    
    strategy: Optional[str] = None
    """Стратегия контента"""
    
    draft: Optional[str] = None
    """Черновик контента"""
    
    edited_draft: Optional[str] = None
    """Отредактированный черновик"""
    
    publish_metadata: Optional[Dict[str, Any]] = None
    """Метаданные для публикации (SEO, теги, CTA)"""
    
    # === ФИДБЕК И ОЦЕНКИ ===
    editor_feedback: Optional[str] = None
    """Комментарии редактора для доработки"""
    
    quality_score: Optional[float] = None
    """Оценка качества (0-10)"""
    
    quality_breakdown: Optional[Dict[str, float]] = None
    """Детальная оценка по критериям"""
    
    quality_decision: Optional[QualityDecision] = None
    """Решение по качеству: approve/retry/reject"""
    
    # === СТАТУС И МЕТАДАННЫЕ ===
    stage: Stage = Stage.RESEARCH
    """Текущий этап workflow"""
    
    current_step: int = 0
    """Номер текущего шага"""
    
    total_steps: int = 6
    """Общее количество шагов в workflow"""
    
    attempt_number: int = 0
    """Номер попытки создания контента (при retry)"""
    
    max_retries: int = 3
    """Максимальное количество попыток"""
    
    error: Optional[str] = None
    """Сообщение об ошибке, если есть"""
    
    is_complete: bool = False
    """Завершен ли workflow"""
    
    published: bool = False
    """Опубликован ли контент"""
    
    # === ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ ===
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Дополнительные метаданные"""
    
    created_at: Optional[str] = None
    """Время создания"""
    
    updated_at: Optional[str] = None
    """Время последнего обновления"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует состояние в словарь"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentState":
        """Создает состояние из словаря"""
        state = cls()
        for key, value in data.items():
            if hasattr(state, key):
                # Преобразуем enum значения
                if key == "content_type" and value:
                    try:
                        state.content_type = ContentType(value)
                    except ValueError:
                        pass
                elif key == "tone" and value:
                    try:
                        state.tone = Tone(value)
                    except ValueError:
                        pass
                elif key == "style" and value:
                    try:
                        state.style = Style(value)
                    except ValueError:
                        pass
                elif key == "length" and value:
                    try:
                        state.length = ContentLength(value)
                    except ValueError:
                        pass
                elif key == "stage" and value:
                    try:
                        state.stage = Stage(value)
                    except ValueError:
                        pass
                elif key == "quality_decision" and value:
                    try:
                        state.quality_decision = QualityDecision(value)
                    except ValueError:
                        pass
                else:
                    setattr(state, key, value)
        return state
    
    def __repr__(self) -> str:
        """Краткое представление состояния"""
        return (
            f"ContentState("
            f"topic='{self.topic[:30]}...', "
            f"stage={self.stage.value}, "
            f"is_complete={self.is_complete}, "
            f"error={self.error})"
        )


def create_initial_state(
    topic: str,
    content_type: str = "article",
    target_audience: str = "general",
    tone: str = "professional",
    style: str = "informative",
    length: str = "medium",
    keywords: Optional[List[str]] = None
) -> ContentState:
    """
    Создает начальное состояние для workflow.
    
    Args:
        topic: Тема контента
        content_type: Тип контента (article, blog_post, etc.)
        target_audience: Целевая аудитория
        tone: Тон общения
        style: Стиль написания
        length: Длина контента
        keywords: Ключевые слова
    
    Returns:
        ContentState: Начальное состояние
    """
    state = ContentState()
    state.topic = topic
    state.target_audience = target_audience
    state.keywords = keywords or []
    state.stage = Stage.RESEARCH
    state.current_step = 0
    state.total_steps = 6
    state.attempt_number = 0
    state.max_retries = 3
    state.is_complete = False
    state.published = False
    
    # Устанавливаем параметры
    try:
        state.content_type = ContentType(content_type)
    except ValueError:
        state.content_type = ContentType.ARTICLE
    
    try:
        state.tone = Tone(tone)
    except ValueError:
        state.tone = Tone.PROFESSIONAL
    
    try:
        state.style = Style(style)
    except ValueError:
        state.style = Style.INFORMATIVE
    
    try:
        state.length = ContentLength(length)
    except ValueError:
        state.length = ContentLength.MEDIUM
    
    return state


def create_retry_state(state: ContentState, feedback: str) -> ContentState:
    """
    Создает состояние для повторной попытки с учетом фидбека.
    
    Args:
        state: Текущее состояние
        feedback: Комментарии редактора
    
    Returns:
        ContentState: Обновленное состояние для retry
    """
    state.editor_feedback = feedback
    state.attempt_number += 1
    state.stage = Stage.CONTENT
    state.quality_decision = QualityDecision.RETRY
    state.quality_score = None
    state.quality_breakdown = None
    
    # Очищаем результаты предыдущей попытки
    # (оставляем draft для контекста, но будем перезаписывать)
    
    return state


def create_success_state(state: ContentState) -> ContentState:
    """
    Отмечает состояние как успешно завершенное.
    
    Args:
        state: Текущее состояние
    
    Returns:
        ContentState: Обновленное состояние
    """
    state.stage = Stage.COMPLETED
    state.is_complete = True
    state.quality_decision = QualityDecision.APPROVE
    return state


def create_failed_state(state: ContentState, error: str) -> ContentState:
    """
    Отмечает состояние как завершенное с ошибкой.
    
    Args:
        state: Текущее состояние
        error: Сообщение об ошибке
    
    Returns:
        ContentState: Обновленное состояние
    """
    state.stage = Stage.FAILED
    state.is_complete = False
    state.error = error
    return state


# === ДЛЯ СОВМЕСТИМОСТИ С TYPEDDict (если нужно) ===

class ContentStateDict(TypedDict, total=False):
    """Типизированный словарь для совместимости с TypedDict"""
    topic: str
    content_type: str
    target_audience: str
    keywords: List[str]
    research_material: Optional[str]
    strategy: Optional[str]
    draft: Optional[str]
    edited_draft: Optional[str]
    publish_metadata: Optional[Dict[str, Any]]
    editor_feedback: Optional[str]
    quality_score: Optional[float]
    quality_breakdown: Optional[Dict[str, float]]
    quality_decision: Optional[str]
    stage: str
    current_step: int
    total_steps: int
    attempt_number: int
    max_retries: int
    error: Optional[str]
    is_complete: bool
    published: bool
    tone: str
    style: str
    length: str
    language: str
    metadata: Dict[str, Any]
    created_at: Optional[str]
    updated_at: Optional[str]


def state_to_dict(state: ContentState) -> ContentStateDict:
    """Преобразует ContentState в ContentStateDict"""
    return state.to_dict()


def dict_to_state(data: ContentStateDict) -> ContentState:
    """Преобразует ContentStateDict в ContentState"""
    return ContentState.from_dict(data)