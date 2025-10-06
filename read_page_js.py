from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
from is_valid_name import TEAMS, is_valid_player
from random import randint
from json_adapter import *
from extract_teams_from_match_text import extract_teams_from_match_text


       

def parse_match_lineups(driver, match_url, score_team1, score_team2, team1, team2):
    """Оптимизированная версия парсинга составов"""
    try:
        main_window = driver.current_window_handle
        
        # Открываем в новой вкладке
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        
        # Устанавливаем таймаут загрузки
        driver.set_page_load_timeout(5)
        driver.get(match_url)

        # Ждем меньше
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(0.3)  # Уменьшили sleep

        # Используем более быстрые селекторы
        player_elements = driver.find_elements(By.CSS_SELECTOR, ".table-item__name")
        
        # БЫСТРЫЙ ПАРСИНГ ИГРОКОВ
        player_names = []
        for element in player_elements:
            try:
                text = element.text.strip()
                if text and len(text) >= 3 and not any(char.isdigit() for char in text):
                    player_names.append(text)
            except:
                continue
        
        # БЫСТРОЕ РАЗДЕЛЕНИЕ НА КОМАНДЫ
        if player_names:
            half_index = len(player_names) // 2
            team_1_players = player_names[:half_index] 
            team_2_players = player_names[half_index:]
        else:
            team_1_players, team_2_players = [], []

        # БЫСТРЫЙ ПАРСИНГ ДОПОЛНИТЕЛЬНОЙ ИНФОРМАЦИИ
        stadion, city, viewers, max_capacity = parse_extra_info_fast(driver)
        
        extra_data = {
            "city": city,
            "stadion": stadion,
            "viewers": viewers,
            "max_capacity": max_capacity,
            "lineup_team1": team_1_players, 
            "lineup_team2": team_2_players, 
            "goals_team1": [],
            "goals_team2": [],
            "kick_offs": []
        }

        # Быстро закрываем
        driver.close()
        driver.switch_to.window(main_window)
        return extra_data

    except Exception as e:
        print(f"Быстрый парсинг: ошибка {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return None

def parse_extra_info_fast(driver):
    """Быстрый парсинг дополнительной информации"""
    stadion = city = ''
    viewers = max_capacity = None
    
    try:
        extra_elements = driver.find_elements(By.CSS_SELECTOR, ".match-info__extra-row")
        for element in extra_elements:
            text = element.text.strip()
            if not text or any(word in text.lower() for word in ['судья', 'линейный']):
                continue
                
            # Быстрый парсинг через regex
            import re
            # Стадион из ссылки
            try:
                link = element.find_element(By.TAG_NAME, 'a')
                stadion = link.text.strip()
            except:
                pass
                
            # Город из скобок
            city_match = re.search(r'\((.*?)(?:,|\))', text)
            if city_match:
                city = city_match.group(1).strip()
                
            # Числа
            numbers = re.findall(r'\d[\d\s]*\d', text)
            if numbers:
                viewers = int(numbers[0].replace(' ', ''))
                if len(numbers) > 1:
                    max_capacity = int(numbers[-1].replace(' ', ''))
                    
    except Exception as e:
        print(f"Быстрый парсинг доп инфо: {e}")
        
    return stadion, city, viewers, max_capacity




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
    
    # ОТКЛЮЧАЕМ ВСЕ ЛИШНЕЕ ДЛЯ УСКОРЕНИЯ
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")  # осторожно, может сломать сайт
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,  # Отключаем изображения
        "profile.managed_default_content_settings.stylesheets": 2,  # Отключаем CSS
    })
    
    # Более агрессивные настройки для скорости
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    
    # Устанавливаем таймауты поменьше
    driver.set_page_load_timeout(5)
    driver.implicitly_wait(2)
    
    matches_data = []

    try:
        driver.get(url)
        # Уменьшаем время ожидания
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Убираем sleep или уменьшаем
        time.sleep(0.5)

        match_selectors = [".results-item", ".tournament-item", ".js-match-item"]
        processed_urls = set()

        # Загружаем существующие URL чтобы не парсить повторно
        existing_data = load_existing_data()
        existing_urls = {match['url'] for match in existing_data.get('matches', [])}

        for selector in match_selectors:
            try:
                match_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for i, element in enumerate(match_elements[:]):
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
                        teams = extract_teams_from_match_text(text)
                        scores = [x for x in text.split(" ") if x.isnumeric() ]
                        team1 = teams[0]
                        team2 = teams[1]
                        match_info = {
                            "text": text[:100] + "..." if len(text) > 100 else text,
                            "team1":team1,
                            "team2":team2,
                            "score": scores[0] + ":"+ scores[1],
                            "url": match_url,
                            # "selector": selector,
                            "source_url": url  # Добавляем URL источника
                        }

                        print(f"Найден матч: {match_info['text']}")
                        
                        # Парсим составы
                        team_scores = [int(x) for x in match_info['score'].split(":")]
                        lineup_data = parse_match_lineups(driver, match_url,team_scores[0],team_scores[1],team1,team2)
                        match_info["stats"] = lineup_data
                        
                        # match_info["processed_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        if lineup_data:
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
