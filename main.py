from read_page_js import get_js_data_with_selenium, save_to_json
import json
import time
import hashlib
import os
import pickle
from generate_db import create_hockey_database
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

if __name__ == "__main__":
    urls = [
        # "https://www.championat.com/stat/hockey/#2025-09-07",
        "https://www.championat.com/stat/hockey/#2025-10-05"
    ]
    
    print("Запуск улучшенного парсера...")
    with open('./matches_data.json','w'): 
        all_new_matches = []
        start = time.time()
        
        for url in urls:
            print(f"Парсим страницу: {url}")
            
            # Пробуем загрузить из кэша
            cached_data = load_from_cache(url)
            if cached_data is not None:
                matches = cached_data
            else:
                matches = get_js_data_with_selenium(url)
                if matches:
                    save_to_cache(url, matches)
            
            if matches:
                # Сохраняем полученные матчи
                added_count = save_to_json(matches)
                all_new_matches.extend(matches)
                print(f"С страницы {url} добавлено {added_count} матчей")
            else:
                print(f"На странице {url} не найдено новых матчей")
        
        print(f"Общее время: {round(time.time()-start, 3)} секунд")

        start = time.time()
        
        # create_hockey_database('./matches_data.json') 
        # Вместо файла используем память
        create_hockey_database('matches_data.json')
        
        print(f"Время на создание db - {round(time.time() - start,3)} секунд")
        