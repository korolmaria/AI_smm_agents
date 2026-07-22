# main.py
from client import lm_client
from graph.workflow import Workflow
from graph.state import create_initial_state
from langfuse_client import flush_langfuse
import json
from datetime import datetime


def test_connection():
    """Тест подключения к LM Studio"""
    print("=" * 50)
    print("🔍 ПРОВЕРКА СВЯЗИ С LM STUDIO")
    print("=" * 50)
    
    try:
        response = lm_client.generate(
            prompt="Ответь одним предложением: работает ли подключение?",
            system_prompt="Ты - ассистент. Отвечай кратко.",
            max_tokens=30,
            temperature=0.3
        )
        
        if response:
            print("✅ СВЯЗЬ УСТАНОВЛЕНА!")
            print(f"📝 Ответ модели: {response}\n")
            return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def run_workflow(topic: str, save_results: bool = True):
    """
    Запуск workflow с указанной темой
    
    Args:
        topic: Тема для генерации контента
        save_results: Сохранять ли результаты в файл
    """
    print("\n" + "=" * 50)
    print("🚀 ЗАПУСК WORKFLOW С АГЕНТАМИ")
    print("=" * 50)
    print(f"📌 Тема: {topic}")
    print("=" * 50)
    
    workflow = Workflow()
    
    # Запускаем workflow
    result = workflow.run(topic)
    
    # Сбрасываем буфер Langfuse
    flush_langfuse()
    
    # Показываем результаты
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 60)
    print(f"📌 Тема: {result.topic}")
    print(f"📌 Статус: {result.stage.value}")
    print(f"📌 Завершен: {'✅ Да' if result.is_complete else '❌ Нет'}")
    print(f"📌 Ошибка: {result.error or 'Нет'}")
    print(f"📌 Количество попыток: {result.attempt_number}")
    print(f"📌 Оценка качества: {result.quality_score or 'Нет'}/10")
    
    if result.quality_decision:
        print(f"📌 Решение редактора: {result.quality_decision.value}")
    
    # Выводим финальный текст
    if result.edited_draft:
        print("\n" + "=" * 60)
        print("📝 ФИНАЛЬНЫЙ ТЕКСТ (отредактированный)")
        print("=" * 60)
        print(result.edited_draft)
    
    # Выводим метаданные для публикации
    if result.publish_metadata:
        print("\n" + "=" * 60)
        print("📋 МЕТАДАННЫЕ ДЛЯ ПУБЛИКАЦИИ")
        print("=" * 60)
        for key, value in result.publish_metadata.items():
            print(f"  {key.replace('_', ' ').upper()}: {value}")
    
    # Сохраняем результаты в файл
    if save_results and result.is_complete:
        save_results_to_file(result)
    
    return result


def save_results_to_file(result):
    """Сохраняет результаты в JSON файл"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/result_{timestamp}.json"
    
    # Создаем папку output если её нет
    import os
    os.makedirs("output", exist_ok=True)
    
    # Подготавливаем данные для сохранения
    data = {
        "timestamp": timestamp,
        "topic": result.topic,
        "stage": result.stage.value,
        "is_complete": result.is_complete,
        "attempt_number": result.attempt_number,
        "quality_score": result.quality_score,
        "quality_decision": result.quality_decision.value if result.quality_decision else None,
        "error": result.error,
        "research_material": result.research_material,
        "strategy": result.strategy,
        "draft": result.draft,
        "edited_draft": result.edited_draft,
        "publish_metadata": result.publish_metadata,
        "metadata": result.metadata
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {filename}")


def main():
    """Главная функция с выбором режима"""
    print("🚀 ЗАПУСК ПРОЕКТА С АГЕНТАМИ")
    print("=" * 50)
    
    # Проверяем подключение
    if not test_connection():
        print("\n❌ Нет подключения к LM Studio. Исправьте ошибку.")
        return
    
    # Выбор режима
    print("\n📋 ВЫБЕРИ РЕЖИМ РАБОТЫ:")
    print("  1. Тестовый запуск (спорт)")
    print("  2. Онлайн школа React/Next.js")
    print("  3. Своя тема")
    print("  4. Выйти")
    
    choice = input("\n👉 Введите номер (1-4): ").strip()
    
    if choice == "1":
        topic = "Как начать заниматься спортом дома"
    elif choice == "2":
        topic = "Онлайн школа программирования по React/Next.js: контент-план на неделю для начинающих разработчиков"
    elif choice == "3":
        topic = input("Введите тему для генерации контента: ").strip()
        if not topic:
            print("❌ Тема не может быть пустой!")
            return
    elif choice == "4":
        print("👋 До свидания!")
        return
    else:
        print("❌ Неверный выбор!")
        return
    
    # Запускаем workflow
    result = run_workflow(topic, save_results=True)
    
    # Дополнительная информация
    if result.is_complete:
        print("\n" + "=" * 60)
        print("🎉 КОНТЕНТ УСПЕШНО СОЗДАН И ГОТОВ К ПУБЛИКАЦИИ!")
        print("=" * 60)
        print("\n📌 Что дальше?")
        print("  1. Проверьте финальный текст в выводе выше")
        print("  2. Метаданные для публикации готовы")
        print("  3. Результаты сохранены в папке output/")
        print("  4. Данные отправлены в Langfuse — проверь в интерфейсе!")
    else:
        print("\n" + "=" * 60)
        print("❌ КОНТЕНТ НЕ БЫЛ СОЗДАН")
        print("=" * 60)
        print(f"\nОшибка: {result.error}")
        print("Попробуйте перезапустить с другой темой.")


if __name__ == "__main__":
    main()