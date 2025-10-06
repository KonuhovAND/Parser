from tools.read_data_from_page import get_js_data_with_selenium, save_to_json
import json
import time
from tools.generate_db import * 
from tools.cache import *
from datetime import datetime,timedelta
def runner():
    urls = []
    today = datetime.now().date()
    last_3_days = []

    for i in range(1, 4):
        day = today - timedelta(days=i)
        urls.append(f"https://www.championat.com/stat/hockey/#{day.strftime('%Y-%m-%d')}")
    
    
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
        
        # Вместо файла используем память
        create_hockey_database('matches_data.json')
        
        # Получаем все матчи
        get_all_matches()
        
        # Получаем статистику игроков
        get_player_stats()
        get_most_penalized_players()
        
        # Получаем детали первого матча
        if get_all_matches():
            get_match_details(1)

        print(f"Время на создание db - {round(time.time() - start,3)} секунд")
        