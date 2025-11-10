from tools.read_data_from_page import get_js_data_with_selenium
import time
from tools.database_tools.generate_db import *
from tools.cache_tools.load_from_cache import load_from_cache
from tools.cache_tools.save_to_cache import save_to_cache
from tools.json_tools.save_to_json import save_to_json
from datetime import datetime, timedelta


def runner(days, league):
    urls = []
    today = datetime.now().date()

    for i in range(1, days + 1):
        day = today - timedelta(days=i)
        urls.append(
            f"https://www.championat.com/stat/hockey/#{day.strftime('%Y-%m-%d')}"
        )

    print("Запуск улучшенного парсера...")
    with open("./matches_data.json", "w") as f:
        all_new_matches = []
        start = time.time()
        for url in urls:
            print(f"Парсим страницу: {url}")

            # Пробуем загрузить из кэша
            cached_data = load_from_cache(url)
            if cached_data is not None:
                matches = cached_data
            else:
                matches = get_js_data_with_selenium(url, league)
                if matches:
                    save_to_cache(url, matches)

            if matches:
                # Сохраняем полученные матчи
                added_count = save_to_json(matches)
                all_new_matches.extend(matches)
                print(f"С страницы {url} добавлено {added_count} матчей")
            else:
                print(f"На странице {url} не найдено новых матчей")

        print(f"Общее время: {round(time.time() - start, 3)} секунд")

        start = time.time()

        # Вместо файла используем память
        create_hockey_database("matches_data.json")

        # Получаем все матчи
        get_all_matches()

        # Получаем статистику игроков
        get_player_stats()
        get_most_penalized_players()

        # Получаем детали первого матча
        if get_all_matches():
            get_match_details(1)

        print(f"Время на создание db - {round(time.time() - start, 3)} секунд")

