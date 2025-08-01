import json
import os

TRANSLATIONS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations.json')

with open(TRANSLATIONS_PATH, 'r', encoding='utf-8') as f:
    translations = json.load(f)

def t(key, lang='fa'):
    # اول کلید رو می‌گیریم، بعد زبان رو توش می‌گردیم
    return translations.get(key, {}).get(lang, key)
