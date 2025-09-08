from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json


def parse_match_lineups(driver, match_url):
    """Парсит составы команд на странице матча"""
    try:
        print(f"Переходим на страницу матча: {match_url}")
        driver.get(match_url)

        # Ждем загрузки страницы матча
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # time.sleep(2)  # Даем время на загрузку

        # Ищем блоки с составами команд
        lineup_selectors = [
            ".table-item__name",
            #     ".lineup",
            #     ".composition",
            #     '[class*="line-up"]',
            #     '[class*="sostav"]',
            #     ".team-players",
            #     ".player-list",
        ]

        lineups_found = []

        for selector in lineup_selectors:
            try:
                lineup_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if lineup_elements:
                    for lineup in lineup_elements:
                        text = lineup.text.strip()
                        if text and len(text) > 30:  # Минимальная длина для состава
                            lineups_found.append(
                                {
                                    "selector": selector,
                                    "text": (
                                        text[:200] + "..." if len(text) > 200 else text
                                    ),
                                }
                            )
            except:
                continue

        # Если не нашли стандартные селекторы, ищем по тексту
        if not lineups_found:
            all_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'состав') or contains(text(), 'линей') or contains(text(), 'вратар') or contains(text(), 'защитник') or contains(text(), 'нападающ')]",
            )
            for element in all_elements:
                text = element.text.strip()
                if text and len(text) > 30:
                    lineups_found.append(
                        {
                            "selector": "text_search",
                            "text": text[:200] + "..." if len(text) > 200 else text,
                        }
                    )

        return lineups_found

    except Exception as e:
        print(f"Ошибка при парсинге составов: {e}")
        return []


def get_js_data_with_selenium(url):
    # Настройка браузера
    options = Options()
    options.add_argument("--headless")  # Фоновый режим
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # Правильное создание драйвера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Открываем страницу
        driver.get(url)

        # Ждем загрузки JavaScript
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # time.sleep(3)  # Даем время на полную загрузку

        # Сохраняем основную страницу для отладки
        main_page_source = driver.page_source
        with open("main_page.html", "w", encoding="utf-8") as f:
            f.write(main_page_source)
        print("Основная страница сохранена в main_page.html")

        # Ищем элементы матчей с ссылками
        match_selectors = [
            ".results-item.js-match-item.fav-item.js-fav-item._is-end._not-started",
            # ".results-item",
            # ".js-match-item",
            # '[class*="match"]',
            # '[class*="game"]',
            # ".event-item",
            # ".tournament-item",
        ]

        matches_data = []

        for selector in match_selectors:
            try:
                match_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Селектор '{selector}': найдено {len(match_elements)} элементов")

                for i, element in enumerate(match_elements):
                    try:
                        text = element.text.replace("\n", " ").strip()
                        if text and len(text) > 10:
                            # Ищем ссылку внутри элемента матча - ПРАВИЛЬНЫЙ СПОСОБ
                            link_elements = element.find_elements(By.TAG_NAME, "a")
                            match_url = None

                            for link in link_elements:
                                href = link.get_attribute("href")
                                if href and (
                                    "hockey" in href
                                    or "match" in href
                                    or "game" in href
                                ):
                                    match_url = href
                                    break

                            # Если не нашли ссылку в теге a, ищем в данных элемента
                            if not match_url:
                                href = element.get_attribute("href")
                                if href and (
                                    "hockey" in href
                                    or "match" in href
                                    or "game" in href
                                ):
                                    match_url = href

                            match_info = {
                                "text": text[:100] + "..." if len(text) > 100 else text,
                                "url": match_url,
                                "selector": selector,
                            }

                            matches_data.append(match_info)
                            print(f"  Матч {len(matches_data)}: {match_info['text']}")

                            # Если есть ссылка, парсим составы
                            if match_url:
                                lineups = parse_match_lineups(driver, match_url)
                                match_info["lineups"] = lineups

                                if lineups:
                                    print(f"    Найдено составов: {len(lineups)}")
                                    for j, lineup in enumerate(lineups):
                                        print(f"      Состав {j+1}: {lineup['text']}")
                                else:
                                    print("    Составы не найдены")

                            print("-" * 50)

                    except Exception as e:
                        print(f"Ошибка обработки элемента {i}: {e}")
                        continue

            except Exception as e:
                print(f"Ошибка с селектором {selector}: {e}")
                continue

        # Сохраняем все данные в JSON
        output_data = {
            "source_url": url,
            "matches_found": len(matches_data),
            "matches": matches_data,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open("matches_data.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\nВсего найдено матчей: {len(matches_data)}")
        print("Данные сохранены в matches_data.json")
        return matches_data

    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    finally:
        driver.quit()


# Альтернативная функция для поиска ссылок на матчи
def find_match_links(driver):
    """Ищет все ссылки на матчи на странице"""
    try:
        # Ищем все ссылки, которые могут вести на матчи
        all_links = driver.find_elements(By.TAG_NAME, "a")
        match_links = []

        for link in all_links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()

                if (
                    href
                    and ("hockey" in href or "match" in href or "game" in href)
                    and len(text) > 5
                    and any(
                        word in text.lower()
                        for word in ["матч", "игра", "vs", ":", "-"]
                    )
                ):

                    match_links.append(
                        {
                            "text": text[:100] + "..." if len(text) > 100 else text,
                            "url": href,
                        }
                    )

            except:
                continue

        return match_links

    except Exception as e:
        print(f"Ошибка поиска ссылок: {e}")
        return []


# Упрощенная версия для тестирования
def simple_parser(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(3)

        # Просто выводим все ссылки для анализа
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Всего ссылок на странице: {len(links)}")

        hockey_links = []
        for link in links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                if href and "hockey" in href and text:
                    hockey_links.append(f"{text} -> {href}")
            except:
                continue

        print("\nХоккейные ссылки:")
        for i, link_info in enumerate(hockey_links[:20]):  # Первые 20
            print(f"{i+1}. {link_info}")

        # Сохраняем HTML для анализа
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\nHTML сохранен в debug_page.html")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        driver.quit()


# Запуск
if __name__ == "__main__":
    doc = "https://www.championat.com/stat/hockey/#2025-09-07"

    # Вариант 1: Полный парсер
    print("Запуск полного парсера...")
    matches = get_js_data_with_selenium(doc)

    # Вариант 2: Простой анализ ссылок
    # print("Запуск простого анализа ссылок...")
    # simple_parser(doc)
