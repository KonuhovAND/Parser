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


def parse_match_lineups(driver, match_url,score_team1,score_team2,team1,team2):
    
    """Парсит составы команд на странице матча и разделяет на две команды"""
    try:
        main_window = driver.current_window_handle
        
        # Открываем матч в новой вкладке
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(match_url)

        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(1)

        # Ищем все элементы с именами игроков
        player_elements = driver.find_elements(By.CLASS_NAME, "table-item__name")
        player_names = []
        
        # Ищем элементы с голами
        goals_elements_team1 = driver.find_elements(By.CSS_SELECTOR, ".match-stat__player")
        # Списки для хранения игроков и голов
        team_1_players_goals = []
        team_2_players_goals = []
        kick_offs = []
        
        stadion = ''
        viewers:int  = None

        # try:
        #     extra_information = driver.find_elements(By.CSS_SELECTOR, ".match-info__extra-row")
        #     for element in extra_information:
        #         text = element.strip()
        #         if not stadion:
        #             stadion = text
        #         else:
        #             viewers = int(text)
        # except:
        #      raise Exception("Ошибка в парсинге доп статистики")
        
        
        
        team_1_players,team_2_players = [],[]
        print("Trying to parse players...")
        for i, element in enumerate(player_elements):
            try:
                text = element.text.strip()
                # Упрощенная проверка - берем все имена, которые не являются названиями команд
                if text and text not in TEAMS and len(text) >= 3:
                    # Более мягкая проверка - только базовые критерии
                    if (not any(char.isdigit() for char in text) and 
                        'команда' not in text.lower() and 
                        'клуб' not in text.lower() and
                        text not in player_names):
                        player_names.append(text) 
            except:
                  continue
        
        
        if player_names:
            
                half_index = len(player_names) // 2
                team_1_players = player_names[:half_index] 
                team_2_players = player_names[half_index:]
                
                for element in goals_elements_team1[:(score_team1 + score_team2)]:
                    text = element.text.strip()
                    if text in team_1_players  and len(team_1_players_goals) <= score_team1:
                        team_1_players_goals.append(text)
                    elif text in team_2_players and len(team_2_players_goals) <= score_team2:
                        team_2_players_goals.append(text)
                        
                while len(team_1_players_goals) < score_team1:
                    team_1_players_goals.append(team_1_players_goals[-1])
                    
                while len(team_2_players_goals) < score_team2:
                    team_2_players_goals.append(team_2_players_goals[-1])
                    
                    
                for element in goals_elements_team1[(score_team1 + score_team2):]:
                    text = element.text.strip()
                    kick_offs.append(text)

        lineup_data ={
            "lineup_team1": team_1_players, 
            "lineup_team2": team_2_players, 
            "goals_team1":team_1_players_goals,
            "goals_team2": team_2_players_goals,
            "kick_offs": kick_offs,
        }

        # Закрываем вкладку и возвращаемся
        driver.close()
        driver.switch_to.window(main_window)
        driver.refresh()
        WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(1)
        print("%DONE%")
        return lineup_data
    

    except Exception as e:
        print(f"Ошибка при парсинге составов: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return None
        # return {
        #     "team_1": {"lineup": [], "player_count": 0},
        #     "team_2": {"lineup": [], "player_count": 0},
        #     "total_players": 0
        # }










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
        WebDriverWait(driver, 7).until(
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
                
                for i, element in enumerate(match_elements[:3]):
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
                        
                        scores = [x for x in text.split() if x.isnumeric() ]
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
