import re

def extract_teams_from_match_text(match_text):
    """
    Извлекает названия команд из текста матча
    Возвращает список: ['team1', 'team2']
    """
    
    # Список известных команд для более точного определения
    KNOWN_TEAMS = [
        # ... существующие команды ...
        # Добавьте иностранные команды
        "Айсберен Берлин", "Гренобль", "Фиштаун Пингвинз", "Лукко", 
        "Больцано", "Маунтфилд", "Лозанна", "Ингольштадт", "Берн", 
        "Комета Брно", "Цуг", "Белфаст Джайантс", "Оденсе Бульдогс",
        "Клагенфуртер", "ГКС Тыхы", "Лулео", "Брюнес", "Цюрих Лайонс",
        "Ильвес", "Сторхамар"
    ]
    
    # Очищаем текст от лишних символов и приводим к нижнему регистру для сравнения
    clean_text = re.sub(r'[^\w\s–\-]', ' ', match_text)  # Убираем знаки препинания, оставляем дефисы
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # Убираем лишние пробелы
    
    # Разбиваем текст на слова
    words = clean_text.split()
    
    teams = []
    current_team = []
    
    # Паттерны для пропуска
    skip_patterns = [
        r'^\d{1,2}:\d{1,2}$',  # время (13:30)
        r'^\d+[:]\d+$',         # счет (0:2, 4:3)
        r'^окончен$',           # статус матча
        r'^ОТ$',                # овертайм
        r'^Б$',                 # буллиты
    ]
    
    i = 0
    while i < len(words):
        word = words[i]
        
        # Пропускаем служебные слова
        if any(re.match(pattern, word) for pattern in skip_patterns):
            i += 1
            continue
        
        # Если это тире между командами
        if word in ['–', '-', '—']:
            if current_team:
                teams.append(' '.join(current_team))
                current_team = []
            i += 1
            continue
        
        # Проверяем, является ли слово частью известной команды
        is_team_part = False
        for known_team in KNOWN_TEAMS:
            known_parts = known_team.lower().split()
            # Проверяем, совпадает ли текущее слово с частью известной команды
            if word.lower() in [part.lower() for part in known_parts]:
                is_team_part = True
                break
        
        # Если это часть команды, добавляем к текущей команде
        if is_team_part or (not word.isdigit() and len(word) > 1):
            current_team.append(word)
        elif current_team:
            # Если нашли не-командное слово после командных слов, заканчиваем текущую команду
            teams.append(' '.join(current_team))
            current_team = []
        
        i += 1
    
    # Добавляем последнюю команду, если есть
    if current_team:
        teams.append(' '.join(current_team))
    
    # Фильтруем результат - оставляем только команды с 2+ символами
    teams = [team for team in teams if len(team) >= 2]
    
    # Если нашли ровно 2 команды - возвращаем их
    if len(teams) == 2:
        return teams
    
    # Альтернативный подход: ищем по формату "команда1 – команда2"
    pattern1 = r'([А-Яа-яA-Za-z\s]+)\s*[–\-]\s*([А-Яа-яA-Za-z\s]+)'
    matches1 = re.findall(pattern1, match_text)
    if matches1:
        team1, team2 = matches1[0]
        return [team1.strip(), team2.strip()]
    
    # Еще один паттерн: ищем две группы слов перед и после тире
    words = match_text.split()
    dash_index = -1
    for i, word in enumerate(words):
        if word in ['–', '-', '—']:
            dash_index = i
            break
    
    if dash_index > 0 and dash_index < len(words) - 1:
        # Берем слова до тире как первую команду
        team1_words = []
        for j in range(dash_index - 1, -1, -1):
            if re.match(r'^\d{1,2}:\d{1,2}$', words[j]) or words[j].isdigit():
                break
            team1_words.insert(0, words[j])
        
        # Берем слова после тире как вторую команду
        team2_words = []
        for j in range(dash_index + 1, len(words)):
            if re.match(r'^\d+[:]\d+$', words[j]) or words[j] in ['окончен', 'ОТ', 'Б']:
                break
            team2_words.append(words[j])
        
        if team1_words and team2_words:
            return [' '.join(team1_words), ' '.join(team2_words)]
    
    return teams[:2]  # Возвращаем максимум 2 команды
