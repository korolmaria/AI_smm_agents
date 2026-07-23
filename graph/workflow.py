from typing import Optional
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
    RESEARCHER_SYSTEM_PROMPT,
    TEMPERATURE_DEFAULT,
    MAX_TOKENS,
    MAX_RETRIES,
    DEBUG,
    LANGFUSE_PUBLIC_KEY
)
from langfuse_client import get_langfuse, flush_langfuse
import time
import uuid


class Workflow:
    """Workflow с условными переходами и агентами"""
    
    def __init__(self):
        self.max_retries = MAX_RETRIES
        
        # Инициализируем агентов
        self.strategist = Strategist()
        self.copywriter = Copywriter()
        self.editor = Editor()
        self.publisher = Publisher()
        
        # Langfuse
        self.langfuse = get_langfuse() if LANGFUSE_PUBLIC_KEY else None
        self.trace = None
        self.trace_id = None
    
    def run(self, topic: str) -> ContentState:
        """Запуск workflow с логированием в Langfuse"""
        
        # Создаем trace
        if self.langfuse:
            try:
                self.trace_id = str(uuid.uuid4())
                self.trace = self.langfuse.trace(
                    id=self.trace_id,
                    name="content_generation_workflow",
                    input={"topic": topic},
                    metadata={
                        "total_steps": 6,
                        "max_retries": self.max_retries,
                        "timestamp": time.time()
                    }
                )
                print(f"🔍 [LANGFUSE] Trace создан: {self.trace_id}")
            except Exception as e:
                print(f"⚠️ [LANGFUSE] Ошибка создания trace: {e}")
        
        print(f"\n🚀 Запуск workflow для темы: {topic}")
        print("=" * 60)
        
        # Создаем начальное состояние
        state = create_initial_state(topic)
        state.total_steps = 6
        state.metadata["trace_id"] = self.trace_id
        
        # Шаг 1: Исследование
        state = self._do_research(state)
        if state.error:
            self._finish_trace(state, "failed")
            return state
        
        # Шаг 2: Стратег
        state = self._run_agent("strategist", state, self.strategist.process)
        if state.error:
            self._finish_trace(state, "failed")
            return state
        
        # Основной цикл
        while state.attempt_number < self.max_retries:
            state.attempt_number += 1
            print(f"\n🔄 Попытка {state.attempt_number} из {self.max_retries}")
            
            # Шаг 3: Копирайтер
            state = self._run_agent("copywriter", state, self.copywriter.process)
            if state.error:
                self._finish_trace(state, "failed")
                return state
            
            # Шаг 4: Редактор
            state = self._run_agent("editor", state, self.editor.process)
            if state.error:
                self._finish_trace(state, "failed")
                return state
            
            # Шаг 5: Проверка решения
            if state.quality_decision == QualityDecision.APPROVE:
                print("✅ Контент одобрен! Отправляем на публикацию.")
                
                # Шаг 6: Паблишер
                state = self._run_agent("publisher", state, self.publisher.process)
                if state.error:
                    self._finish_trace(state, "failed")
                    return state
                
                state = create_success_state(state)
                self._finish_trace(state, "success")
                print("✅ Workflow завершен успешно!")
                break
                
            elif state.quality_decision == QualityDecision.RETRY:
                print("🔄 Контент требует доработки. Отправляем обратно копирайтеру.")
                state.stage = Stage.CONTENT
                continue
            else:
                state = create_failed_state(state, "Не удалось пройти проверку качества")
                self._finish_trace(state, "failed")
                break
        
        if not state.is_complete and not state.error:
            state = create_failed_state(
                state, 
                f"Превышено количество попыток ({self.max_retries})"
            )
            self._finish_trace(state, "failed")
            print(f"\n❌ Превышено количество попыток. Workflow завершен с ошибкой.")
        
        # Сбрасываем буфер Langfuse
        flush_langfuse()
        
        return state
    
    def _run_agent(self, agent_name: str, state: ContentState, agent_func) -> ContentState:
        """Запуск агента с логированием в Langfuse"""
        
        # Создаем span для агента
        span = None
        if self.trace:
            try:
                span = self.trace.span(
                    name=f"{agent_name}_agent",
                    input={
                        "agent": agent_name,
                        "attempt": state.attempt_number,
                        "stage": state.stage.value if state.stage else None,
                        "topic": state.topic
                    },
                    metadata={
                        "attempt": state.attempt_number,
                        "start_time": time.time()
                    }
                )
                print(f"🔍 [LANGFUSE] Span создан: {agent_name}_agent")
            except Exception as e:
                print(f"⚠️ [LANGFUSE] Ошибка создания span: {e}")
        
        start_time = time.time()
        
        try:
            # Выполняем агента
            result_state = agent_func(state)
            duration_ms = (time.time() - start_time) * 1000
            
            # Обновляем span с результатом
            if span:
                try:
                    quality_info = ""
                    if hasattr(result_state, 'quality_decision') and result_state.quality_decision:
                        quality_info = result_state.quality_decision.value
                    
                    span.update(
                        output={
                            "success": not bool(result_state.error),
                            "stage": result_state.stage.value if result_state.stage else None,
                            "quality_score": result_state.quality_score if hasattr(result_state, 'quality_score') else None,
                            "quality_decision": quality_info,
                            "error": result_state.error
                        },
                        metadata={
                            "duration_ms": duration_ms,
                            "attempt": state.attempt_number
                        }
                    )
                    span.end()
                    print(f"🔍 [LANGFUSE] Span завершен: {agent_name}_result")
                except Exception as e:
                    print(f"⚠️ [LANGFUSE] Ошибка обновления span: {e}")
            
            return result_state
            
        except Exception as e:
            error = str(e)
            print(f"❌ Ошибка в агенте {agent_name}: {error}")
            
            if span:
                try:
                    span.update(
                        output={"error": error, "success": False},
                        metadata={"duration_ms": (time.time() - start_time) * 1000}
                    )
                    span.end()
                except Exception as e:
                    print(f"⚠️ [LANGFUSE] Ошибка логирования ошибки: {e}")
            
            return create_failed_state(state, f"Ошибка в агенте {agent_name}: {error}")
    
    def _do_research(self, state: ContentState) -> ContentState:
        """Шаг 1: Исследование с логированием в Langfuse"""
        print(f"\n📌 Шаг 1: RESEARCH (исследование)")
        print("-" * 40)
        
        # Создаем span для исследования
        span = None
        if self.trace:
            try:
                span = self.trace.span(
                    name="research_agent",
                    input={"topic": state.topic},
                    metadata={"start_time": time.time()}
                )
                print("🔍 [LANGFUSE] Span создан: research_agent")
            except Exception as e:
                print(f"⚠️ [LANGFUSE] Ошибка создания span: {e}")
        
        start_time = time.time()
        
        try:
            prompt = f"Проведи исследование по теме: {state.topic}. Напиши 5-7 предложений с ключевыми фактами, статистикой и трендами."
            
            response = lm_client.generate(
                prompt=prompt,
                system_prompt=RESEARCHER_SYSTEM_PROMPT or "Ты - исследователь. Отвечай кратко и структурированно.",
                max_tokens=500,
                temperature=TEMPERATURE_DEFAULT
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if response and response.strip():
                state.research_material = response
                state.stage = Stage.RESEARCH
                print("✅ Исследование завершено")
                
                # Обновляем span с результатом
                if span:
                    try:
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
                        print("🔍 [LANGFUSE] Span завершен: research_result")
                    except Exception as e:
                        print(f"⚠️ [LANGFUSE] Ошибка обновления span: {e}")
            else:
                error_msg = "Не удалось получить ответ от модели"
                if span:
                    try:
                        span.update(
                            output={"error": error_msg, "success": False},
                            metadata={"duration_ms": duration_ms, "status": "error"}
                        )
                        span.end()
                    except Exception as e:
                        print(f"⚠️ [LANGFUSE] Ошибка обновления span: {e}")
                return create_failed_state(state, error_msg)
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка при исследовании: {e}")
            
            if span:
                try:
                    span.update(
                        output={"error": error_msg, "success": False},
                        metadata={"duration_ms": (time.time() - start_time) * 1000, "status": "error"}
                    )
                    span.end()
                except Exception as e:
                    print(f"⚠️ [LANGFUSE] Ошибка обновления span: {e}")
            
            return create_failed_state(state, f"Ошибка при исследовании: {e}")
        
        return state
    
    def _finish_trace(self, state: ContentState, status: str):
        """Завершает трейс в Langfuse"""
        if self.trace:
            try:
                self.trace.update(
                    output={
                        "status": status,
                        "stage": state.stage.value if state.stage else None,
                        "is_complete": state.is_complete,
                        "quality_score": state.quality_score if hasattr(state, 'quality_score') else None,
                        "attempts": state.attempt_number,
                        "published": state.published if hasattr(state, 'published') else False
                    },
                    metadata={
                        "error": state.error,
                        "quality_decision": state.quality_decision.value if hasattr(state, 'quality_decision') and state.quality_decision else None,
                        "topic": state.topic
                    }
                )
                print(f"🔍 [LANGFUSE] Trace завершен: {self.trace_id}")
            except Exception as e:
                print(f"⚠️ [LANGFUSE] Ошибка завершения trace: {e}")