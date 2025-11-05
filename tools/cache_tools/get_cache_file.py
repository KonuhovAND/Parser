import hashlib
import os
import pickle
CACHE_DIR = "./cache"

def get_cache_file(url):
    """Генерирует имя файла для кэша"""
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.pkl")


