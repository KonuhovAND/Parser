from tools.read_data_from_page import get_js_data_with_selenium, save_to_json
import json
import time
from tools.generate_db import * 
from tools.cache import *

def runner():
    urls = [
        "https://www.championat.com/stat/hockey/#2025-09-07",
        "https://www.championat.com/stat/hockey/#2025-10-05"
    ]
    
    print("Запуск улучшенного парсера...")
    
    # Clear the file at start
    with open('./matches_data.json', 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    
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
    
    print(f"Общее время парсинга: {round(time.time()-start, 3)} секунд")

    start_db = time.time()
    
    # Вместо файла используем память
    create_hockey_database('matches_data.json')
    
    # Получаем все матчи
    matches_count = len(get_all_matches())
    
    # Получаем статистику игроков
    player_stats = get_player_stats()
    penalized_players = get_most_penalized_players()
    
    # Получаем детали первого матча
    if get_all_matches():
        match_details = get_match_details(1)

    print(f"Время на создание db - {round(time.time() - start_db, 3)} секунд")
    print(f"Всего обработано матчей: {matches_count}")
    
    return {
        "total_matches": matches_count,
        "parsing_time": round(time.time()-start, 3),
        "db_creation_time": round(time.time() - start_db, 3)
    }