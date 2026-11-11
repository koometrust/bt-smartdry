import json
from pathlib import Path
from typing import Dict, Any

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"

_TEMPLATES: Dict[str, Dict[str, str]] = {}


def _load_templates():
    global _TEMPLATES
    if not _TEMPLATES:
        for lang in ["en", "sw"]:
            file_path = LOCALES_DIR / f"{lang}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    _TEMPLATES[lang] = data.get("advisories", {})


def generate_advisory(
    template_key: str,
    lang: str = "en",
    **kwargs: Any
) -> str:
    _load_templates()
    lang = lang if lang in _TEMPLATES else "en"
    template = _TEMPLATES.get(lang, {}).get(template_key)
    
    if not template:
        # Fallback to English
        template = _TEMPLATES.get("en", {}).get(template_key, "Batch is progressing.")

    for k, v in kwargs.items():
        template = template.replace(f"{{{{{k}}}}}", str(v))
    return template

