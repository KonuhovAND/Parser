from read_page_js import get_js_data_with_selenium,save_to_json
import json
import time
if __name__ == "__main__":
    urls = [
        "https://www.championat.com/stat/hockey/#2025-09-07",
        "https://www.championat.com/stat/hockey/#2025-09-08"
    ]
    
    print("Запуск улучшенного парсера...")
    
    all_new_matches = []
    start = time.time()
    with open("matches_data.json", "w", encoding="utf-8") as f:    
        for url in urls:
            print(f"Парсим страницу: {url}")
            matches = get_js_data_with_selenium(url)
            
            if matches:
                # Сохраняем полученные матчи
                added_count = save_to_json(matches)
                all_new_matches.extend(matches)
                print(f"С страницы {url} добавлено {added_count} матчей")
            else:
                print(f"На странице {url} не найдено новых матчей")
    print(time.time()-start)