import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# ============================================
# LM Studio Configuration
# ============================================
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "not-needed")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen/qwen3-vl-4b")

# ============================================
# Langfuse Configuration
# ============================================
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_DEBUG = os.getenv("LANGFUSE_DEBUG", "False").lower() == "true"

# ============================================
# Model Parameters
# ============================================
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2048))
MAX_TOKENS_EDIT = int(os.getenv("MAX_TOKENS_EDIT", 600))
TEMPERATURE_DEFAULT = float(os.getenv("TEMPERATURE_DEFAULT", 0.3))
TEMPERATURE_CREATIVE = float(os.getenv("TEMPERATURE_CREATIVE", 0.7))
TEMPERATURE_PRECISE = float(os.getenv("TEMPERATURE_PRECISE", 0.2))
TOP_P = float(os.getenv("TOP_P", 0.85))

# ============================================
# Agent System Prompts
# ============================================
STRATEGIST_SYSTEM_PROMPT = os.getenv("STRATEGIST_SYSTEM_PROMPT", "")
COPYWRITER_SYSTEM_PROMPT = os.getenv("COPYWRITER_SYSTEM_PROMPT", "")
EDITOR_SYSTEM_PROMPT = os.getenv("EDITOR_SYSTEM_PROMPT", "")
PUBLISHER_SYSTEM_PROMPT = os.getenv("PUBLISHER_SYSTEM_PROMPT", "")
RESEARCHER_SYSTEM_PROMPT = os.getenv("RESEARCHER_SYSTEM_PROMPT", "")

# ============================================
# Prompt Templates
# ============================================
STRATEGIST_PROMPT_TEMPLATE = os.getenv("STRATEGIST_PROMPT_TEMPLATE", "")
COPYWRITER_PROMPT_TEMPLATE = os.getenv("COPYWRITER_PROMPT_TEMPLATE", "")
EDITOR_EDIT_PROMPT_TEMPLATE = os.getenv("EDITOR_EDIT_PROMPT_TEMPLATE", "")
EDITOR_QUALITY_PROMPT_TEMPLATE = os.getenv("EDITOR_QUALITY_PROMPT_TEMPLATE", "")
PUBLISHER_PROMPT_TEMPLATE = os.getenv("PUBLISHER_PROMPT_TEMPLATE", "")
RESEARCHER_PROMPT_TEMPLATE = os.getenv("RESEARCHER_PROMPT_TEMPLATE", "")

# ============================================
# Project Settings
# ============================================
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# ============================================
# Проверка загрузки переменных (для отладки)
# ============================================
def validate_config():
    """Проверяет, что все необходимые переменные загружены"""
    print("\n" + "=" * 60)
    print("🔍 ПРОВЕРКА КОНФИГУРАЦИИ")
    print("=" * 60)
    
    # Проверяем системные промпты
    system_prompts = {
        "STRATEGIST_SYSTEM_PROMPT": STRATEGIST_SYSTEM_PROMPT,
        "COPYWRITER_SYSTEM_PROMPT": COPYWRITER_SYSTEM_PROMPT,
        "EDITOR_SYSTEM_PROMPT": EDITOR_SYSTEM_PROMPT,
        "PUBLISHER_SYSTEM_PROMPT": PUBLISHER_SYSTEM_PROMPT,
        "RESEARCHER_SYSTEM_PROMPT": RESEARCHER_SYSTEM_PROMPT,
    }
    
    missing = []
    for name, value in system_prompts.items():
        if not value or value.strip() == "":
            missing.append(name)
        else:
            print(f"✅ {name}: {value[:50]}...")
    
    if missing:
        print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЕ: Отсутствуют переменные в .env:")
        for name in missing:
            print(f"   - {name}")
        print("\n   Используются значения по умолчанию (пустые строки)")
        print("   Агенты могут работать некорректно!")
    else:
        print("\n✅ Все системные промпты загружены!")
    
    # Проверяем шаблоны промптов
    templates = {
        "STRATEGIST_PROMPT_TEMPLATE": STRATEGIST_PROMPT_TEMPLATE,
        "COPYWRITER_PROMPT_TEMPLATE": COPYWRITER_PROMPT_TEMPLATE,
        "EDITOR_EDIT_PROMPT_TEMPLATE": EDITOR_EDIT_PROMPT_TEMPLATE,
        "EDITOR_QUALITY_PROMPT_TEMPLATE": EDITOR_QUALITY_PROMPT_TEMPLATE,
        "PUBLISHER_PROMPT_TEMPLATE": PUBLISHER_PROMPT_TEMPLATE,
        "RESEARCHER_PROMPT_TEMPLATE": RESEARCHER_PROMPT_TEMPLATE,
    }
    
    missing_templates = []
    for name, value in templates.items():
        if not value or value.strip() == "":
            missing_templates.append(name)
    
    if missing_templates:
        print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЕ: Отсутствуют шаблоны промптов:")
        for name in missing_templates:
            print(f"   - {name}")
    
    print("=" * 60 + "\n")
    
    return len(missing) == 0

# Вызываем проверку при импорте (если DEBUG)
if DEBUG:
    validate_config()