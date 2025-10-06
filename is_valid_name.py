import re
from nameparser import HumanName

TEAMS = [
    "Авангард", "Омск",
    "Автомобилист", "Екатеринбург", 
    "Адмирал", "Владивосток",
    "Ак Барс", "Казань",
    "Амур", "Хабаровск",
    "Барыс", "Астана",
    "Динамо М", "Москва",
    "Динамо Мн", "Минск",
    "Лада", "Тольятти",
    "Локомотив", "Ярославль",
    "Металлург Мг", "Магнитогорск",
    "Нефтехимик", "Нижнекамск",
    "СКА", "Санкт-Петербург",
    "Салават Юлаев", "Уфа",
    "Северсталь", "Череповец",
    "Сибирь", "Новосибирская область",
    "Спартак", "Москва",
    "Торпедо", "Нижний Новгород",
    "Трактор", "Челябинск",
    "ХК Сочи", "Сочи",
    "ЦСКА", "Москва",
    "Шанхайские Драконы", "Шанхай",
    "Южный Урал","Омские Крылья"
]

def is_valid_player_name(name):
    """
    Проверяет, является ли имя валидным с помощью библиотеки nameparser
    """
    try:
        name = name.strip()
        
        # Базовые проверки
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # Проверка на цифры и специальные символы
        if re.search(r'\d', name) or re.search(r'[!@#$%^&*()_+=\[\]{};:"\\|,.<>/?]', name):
            return False
        
        # Пропускаем явно невалидные паттерны
        invalid_patterns = [
            r'.*команда.*', r'.*клуб.*', r'.*академия.*', r'.*армия.*',
            r'.*львы.*', r'.*пингвины.*', r'.*медведи.*', r'.*собаки.*',
            r'^[A-ZА-Я]{1,3}$',  # Одиночные инициалы
            r'.*\d+:\d+.*',  # Время
            r'.*\d+[-+]\d+.*',  # Счет
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return False
        
        # Используем nameparser для анализа имени
        parsed_name = HumanName(name)
        
        # Должна быть хотя бы фамилия
        if not parsed_name.last:
            return False
        
        # Должно быть хотя бы одно имя или отчество
        if not parsed_name.first and not parsed_name.middle:
            return False
        
        # Проверяем длину компонентов (более мягкие требования)
        if parsed_name.last and len(parsed_name.last) < 2:
            return False
            
        if parsed_name.first and len(parsed_name.first) < 1:  # Имя может быть одной буквой
            return False
            
        if parsed_name.middle and len(parsed_name.middle) < 1:  # Отчество может быть одной буквой
            return False
        
        # Если дошли сюда, имя вероятно валидно
        return True
        
    except Exception as e:
        print(f"Ошибка при проверке имени '{name}': {e}")
        return False

# Альтернативный подход с эвристическими правилами
def is_valid_player_name_simple(name):
    """
    Простая проверка имени с эвристическими правилами
    """
    try:
        name = name.strip()
        
        # Базовые проверки (более мягкие)
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # Не должно содержать цифр
        if any(char.isdigit() for char in name):
            return False
        
        # Не должно содержать специальных символов (кроме пробелов, дефисов, точек)
        if re.search(r'[!@#$%^&*()_+=\[\]{};:"\\|,<>/?]', name):
            return False
        
        # Должно содержать пробел (имя и фамилия) - но это не всегда обязательно
        if ' ' not in name:
            # Разрешаем имена без пробелов (например, иностранные имена)
            words = [name]
        else:
            words = name.split()
        
        if len(words) < 1 or len(words) > 4:
            return False
        
        # Проверяем каждое слово (более мягкие требования)
        for word in words:
            if len(word) < 1:  # Разрешаем очень короткие слова
                return False
            if len(word) > 20:  # Увеличил максимальную длину слова
                return False
        
        # Черный список общих не-имен
        blacklist = [
            'комета', 'цюрих', 'бельфаст', 'айсберен', 'оденсе', 'фиштаун',
            'академия', 'красная', 'армия', 'стальные', 'лисы', 'львы',
            'пингвины', 'медведи', 'собаки', 'тигры', 'волки', 'орлы',
            'окончен', 'завершен', 'матч', 'игра', 'тайм', 'период',
            'нк','спб','крылья', 'россия', 'канада', 'сша', 'германия', 'вр', 'зщ', 'нп'
        ]
        
        lower_name = name.lower()
        for banned in blacklist:
            if banned in lower_name:
                return False
        
        # Если все проверки пройдены
        return True
        
    except Exception as e:
        print(f"Ошибка при простой проверке имени '{name}': {e}")
        return False

# Универсальная функция для использования
def is_valid_player(name):
    """
    Универсальная проверка имени игрока
    """
    # Сначала пробуем простую проверку, потом сложную
    return is_valid_player_name_simple(name) or is_valid_player_name(name)