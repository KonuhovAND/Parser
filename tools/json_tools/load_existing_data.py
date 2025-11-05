import json
import os

def load_existing_data(filename="matches_data.json"):
    """Загружает существующие данные из JSON файла"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"matches": [], "source_urls": []}



