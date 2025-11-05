from tools.cache_tools.get_cache_file import get_cache_file
import hashlib
import os
import pickle
CACHE_DIR = "./cache"

def load_from_cache(url):
    """Загружает данные из кэша"""
    cache_file = get_cache_file(url)
    if os.path.exists(cache_file):
        print("Используем кэшированные данные")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None