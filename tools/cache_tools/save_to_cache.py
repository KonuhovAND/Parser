import hashlib
import os
import pickle
CACHE_DIR = "./cache"
from tools.cache_tools.get_cache_file import get_cache_file
def save_to_cache(url, data):
    """Сохраняет данные в кэш"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    cache_file = get_cache_file(url)
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)