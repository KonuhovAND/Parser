from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import json
import os
from is_valid_name import TEAMS, is_valid_player

def load_existing_data(filename="matches_data.json"):
    """Загружает существующие данные из JSON файла"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"matches": [], "source_urls": [], "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

def save_to_json(data, filename="matches_data.json"):
    """Сохраняет данные в JSON, добавляя к существующим"""
    # Загружаем существующие данные
    existing_data = load_existing_data(filename)
    
    # Обновляем данные
    existing_urls = {match['url'] for match in existing_data.get('matches', [])}
    
    new_matches = []
    for match in data:
        if match['url'] not in existing_urls:
            new_matches.append(match)
            existing_urls.add(match['url'])
    
    # Добавляем новые матчи
    existing_data['matches'].extend(new_matches)
    existing_data['matches_found'] = len(existing_data['matches'])
    
    # Добавляем URL источника если его еще нет
    if 'source_url' in data[0] if data else False:
        source_url = data[0]['source_url']
        if source_url not in existing_data.get('source_urls', []):
            existing_data.setdefault('source_urls', []).append(source_url)
    
    existing_data['last_update'] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Сохраняем обратно
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"Добавлено новых матчей: {len(new_matches)}")
    return len(new_matches)

def parse_match_lineups(driver, match_url):
    """Парсит составы команд на странице матча и разделяет на две команды"""
    try:
        main_window = driver.current_window_handle
        
        # Открываем матч в новой вкладке
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(match_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(1)

        # Ищем все элементы с именами игроков
        player_elements = driver.find_elements(By.CLASS_NAME, "table-item__name")
        player_names = set()
        
        for element in player_elements:
            try:
                text = element.text.strip()
                if text and text not in TEAMS and len(text.split()) == 2:
                    if is_valid_player(text): 
                        player_names.add(text)
            except:
                continue
        
        player_names = list(player_names)

        # Разделяем игроков на две команды
        team_1_players = []
        team_2_players = []
        
        if player_names:
            half_index = len(player_names) // 2
            team_1_players = player_names[:half_index] 
            team_2_players = player_names[half_index:] 

        lineup_data = {
            "team_1": {"lineup": team_1_players, "player_count": len(team_1_players)},
            "team_2": {"lineup": team_2_players, "player_count": len(team_2_players)},
            "total_players": len(player_names)
        }

        # Закрываем вкладку и возвращаемся
        driver.close()
        driver.switch_to.window(main_window)
        driver.refresh()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(1)

        return lineup_data

    except Exception as e:
        print(f"Ошибка при парсинге составов: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return {
            "team_1": {"lineup": [], "player_count": 0},
            "team_2": {"lineup": [], "player_count": 0},
            "total_players": 0
        }

def get_js_data_with_selenium(url):
    """Основная функция парсинга"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=options)
    matches_data = []

    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(1)

        match_selectors = [".results-item", ".tournament-item", ".js-match-item"]
        processed_urls = set()

        # Загружаем существующие URL чтобы не парсить повторно
        existing_data = load_existing_data()
        existing_urls = {match['url'] for match in existing_data.get('matches', [])}

        for selector in match_selectors:
            try:
                match_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for i, element in enumerate(match_elements):
                    try:
                        element = driver.find_elements(By.CSS_SELECTOR, selector)[i]
                        text = element.text.replace("\n", " ").strip()
                        if not text or len(text) < 10:
                            continue

                        # Ищем ссылку
                        match_url = None
                        try:
                            link = element.find_element(By.TAG_NAME, "a")
                            match_url = link.get_attribute("href")
                        except:
                            match_url = element.get_attribute("href")

                        if not match_url or match_url in processed_urls or match_url in existing_urls:
                            continue

                        processed_urls.add(match_url)

                        match_info = {
                            "text": text[:100] + "..." if len(text) > 100 else text,
                            "url": match_url,
                            "selector": selector,
                            "source_url": url  # Добавляем URL источника
                        }

                        print(f"Найден матч: {match_info['text']}")
                        
                        # Парсим составы
                        lineup_data = parse_match_lineups(driver, match_url)
                        match_info["lineups"] = lineup_data
                        match_info["processed_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

                        matches_data.append(match_info)

                    except StaleElementReferenceException:
                        continue
                    except Exception as e:
                        print(f"Ошибка обработки элемента {i}: {e}")
                        continue

            except Exception as e:
                print(f"Ошибка с селектором {selector}: {e}")
                continue

        return matches_data

    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    finally:
        driver.quit()
