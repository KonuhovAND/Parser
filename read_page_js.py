from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import json


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
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Даем время на выполнение JavaScript
        time.sleep(5)

        # Способ 1: Получить отрендеренный HTML
        page_source = driver.page_source
        print("Страница загружена успешно")
        print(f"Длина HTML: {len(page_source)} символов")

        # Способ 2: Выполнить простой JavaScript код
        js_data = driver.execute_script(
            """
            // Простой и безопасный JavaScript код
            return {
                title: document.title,
                url: window.location.href,
                bodyTextLength: document.body.textContent.length,
                matchElements: document.querySelectorAll('[class*="results-item js-match-item fav-item js-fav-item _is-end _not-started"], [class*="game"]').length,
                hasBody: !!document.body,
                readyState: document.readyState
            };
        """
        )

        print(
            "Данные из JavaScript:", json.dumps(js_data, indent=2, ensure_ascii=False)
        )

        # Способ 3: Поиск элементов с правильными селекторами
        try:
            # Пробуем разные селекторы для матчей
            selectors = [
                ".results-item",
                # '.js-match-item',
                # '.fav-item',
                # '[class*="match"]',
                # '[class*="game"]',
                # '.event-item',
                # '.tournament-item'
            ]

            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(
                            f"Селектор '{selector}': найдено {len(elements)} элементов"
                        )
                        for i, element in enumerate(elements[:]):
                            try:
                                text = element.text.replace("\n", " ").strip()
                                if text and len(text) > 10:
                                    print(f"  Элемент {i + 1}: {text[:100]}...")
                            except:
                                continue
                        print("---")
                except:
                    continue

        except Exception as e:
            print(f"Ошибка при поиске элементов: {e}")

        # Способ 4: Поиск по тексту
        try:
            all_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'матч') or contains(text(), 'игра') or contains(text(), 'score')]",
            )
            print(f"Элементов с текстом матча: {len(all_elements)}")

            for i, element in enumerate(all_elements[:5]):
                try:
                    text = element.text.replace("\n", " ").strip()
                    if text and len(text) > 5:
                        print(f"Текстовый элемент {i + 1}: {text[:80]}...")
                except:
                    continue

        except Exception as e:
            print(f"Ошибка текстового поиска: {e}")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        driver.quit()


# Запуск
urls = [
    "https://www.championat.com/stat/hockey/#2025-09-07",
    # 'https://www.championat.com/stat/hockey/#2025-09-06',
    # 'https://www.championat.com/stat/hockey/#2025-09-05'
]
for url in urls:
    get_js_data_with_selenium(url)
