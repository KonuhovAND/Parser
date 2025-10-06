import hashlib
import os
import pickle
CACHE_DIR = "cache"

def get_cache_file(url):
    """Генерирует имя файла для кэша"""
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.pkl")

def load_from_cache(url):
    """Загружает данные из кэша"""
    cache_file = get_cache_file(url)
    if os.path.exists(cache_file):
        print("Используем кэшированные данные")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None

def save_to_cache(url, data):
    """Сохраняет данные в кэш"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    cache_file = get_cache_file(url)
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)