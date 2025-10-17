import sqlite3
import json
import os
import re
from datetime import datetime

def create_hockey_database(json_file_path, db_file_path='hockey_matches.db'):
    """
    Создает SQLite базу данных с информацией о хоккейных матчах из JSON файла
    
    Args:
        json_file_path (str): Путь к JSON файлу с данными матчей
        db_file_path (str): Путь для сохранения SQLite базы данных
    """
    
    # Удаляем существующую базу данных, если есть
    if os.path.exists(db_file_path):
         os.remove(db_file_path)
         print(f"Удалена существующая база данных: {db_file_path}")
    
    try:
        # Загружаем данные из JSON
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        # Создаем таблицы
        
        # Основная таблица матчей
        cursor.execute('''
            CREATE TABLE matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_text TEXT,
                match_time TEXT,
                team1 TEXT NOT NULL,
                team2 TEXT NOT NULL,
                score TEXT,
                stadion TEXT,
                city TEXT,
                viewers INTEGER,
                attendance_percent INTEGER,
                max_capacity INTEGER
            )
        ''')
        
        # Таблица составов команд
        cursor.execute('''
            CREATE TABLE team_lineups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                team_name TEXT,
                player_name TEXT,
                FOREIGN KEY (match_id) REFERENCES matches (id)
            )
        ''')
        
        # Таблица забитых голов
        cursor.execute('''
            CREATE TABLE goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                team_name TEXT,
                player_name TEXT,
                FOREIGN KEY (match_id) REFERENCES matches (id)
            )
        ''')
        
        # Таблица удалений (kick_offs)
        cursor.execute('''
            CREATE TABLE kick_offs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                player_name TEXT,
                FOREIGN KEY (match_id) REFERENCES matches (id)
            )
        ''')
        
        def extract_time_from_match_text(match_text):
            """Извлекает время из текста матча"""
            if not match_text:
                return None
            
            # Ищем паттерн времени в начале строки (например, "13:30", "02:00")
            time_pattern = r'^(\d{1,2}:\d{2})'
            match = re.match(time_pattern, match_text.strip())
            
            if match:
                return match.group(1)
            return None
        
        # Вставляем данные матчей с безопасным доступом
        matches_processed = 0
        for match in data['matches']:
            try:
                # Безопасно получаем данные stats
                stats = match.get('stats', {})
                
                # Извлекаем время из match_text
                match_time = extract_time_from_match_text(match.get('text', ''))
                
                # Вставляем основной матч
                cursor.execute('''
                    INSERT INTO matches (
                        match_text, match_time, team1, team2, score,
                        stadion, city, viewers, attendance_percent, max_capacity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match.get('text', ''),
                    match_time,
                    match.get('team1', ''),
                    match.get('team2', ''),
                    match.get('score', ''),
                    stats.get('stadion', 'Неизвестно'),
                    stats.get('city', 'Неизвестно'),
                    stats.get('viewers', 0) or 0,
                    stats.get('attendance_percent', 0) or 0,
                    stats.get('max_capacity', 0) or 0
                ))
                
                match_id = cursor.lastrowid
                matches_processed += 1
                
                # Вставляем составы команды 1
                for player in stats.get('lineup_team1', []):
                    if player and player.strip():  # Проверяем, что игрок не пустой
                        cursor.execute('''
                            INSERT INTO team_lineups (match_id, team_name, player_name)
                            VALUES (?, ?, ?)
                        ''', (match_id, match.get('team1', ''), player))
                
                # Вставляем составы команды 2
                for player in stats.get('lineup_team2', []):
                    if player and player.strip():  # Проверяем, что игрок не пустой
                        cursor.execute('''
                            INSERT INTO team_lineups (match_id, team_name, player_name)
                            VALUES (?, ?, ?)
                        ''', (match_id, match.get('team2', ''), player))
                
                # Вставляем голы команды 1
                for player in stats.get('goals_team1', []):
                    if player and player.strip():  # Проверяем, что игрок не пустой
                        cursor.execute('''
                            INSERT INTO goals (match_id, team_name, player_name)
                            VALUES (?, ?, ?)
                        ''', (match_id, match.get('team1', ''), player))
                
                # Вставляем голы команды 2
                for player in stats.get('goals_team2', []):
                    if player and player.strip():  # Проверяем, что игрок не пустой
                        cursor.execute('''
                            INSERT INTO goals (match_id, team_name, player_name)
                            VALUES (?, ?, ?)
                        ''', (match_id, match.get('team2', ''), player))
                
                # Вставляем удаления (kick_offs)
                for player in stats.get('kick_offs', []):
                    if player and player.strip():  # Проверяем, что игрок не пустой
                        cursor.execute('''
                            INSERT INTO kick_offs (match_id, player_name)
                            VALUES (?, ?)
                        ''', (match_id, player))
                        
            except Exception as e:
                print(f"Ошибка при обработке матча {match.get('text', 'Unknown')}: {e}")
                continue
        
        # Создаем индексы для ускорения запросов
        cursor.execute('CREATE INDEX idx_matches_team1 ON matches(team1)')
        cursor.execute('CREATE INDEX idx_matches_team2 ON matches(team2)')
        cursor.execute('CREATE INDEX idx_matches_time ON matches(match_time)')
        cursor.execute('CREATE INDEX idx_lineups_match_id ON team_lineups(match_id)')
        cursor.execute('CREATE INDEX idx_goals_match_id ON goals(match_id)')
        cursor.execute('CREATE INDEX idx_kick_offs_match_id ON kick_offs(match_id)')
        
        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()
        
        print(f"База данных успешно создана: {db_file_path}")
        print(f"Обработано матчей: {matches_processed} из {len(data['matches'])}")
        
        # Проверяем структуру базы данных
        check_database_structure(db_file_path)
        
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        if 'conn' in locals():
            conn.close()

def check_database_structure(db_file_path):
    """Проверяет структуру созданной базы данных"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' OR type='view'")
        tables = cursor.fetchall()
        
        print("\nСтруктура базы данных:")
        for table in tables:
            table_name = table[0]
            print(f"\nТаблица: {table_name}")
            
            # Получаем информацию о колонках
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for column in columns:
                print(f"  Колонка: {column[1]} ({column[2]})")
        
        # Проверяем количество записей в каждой таблице
        print("\nКоличество записей:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} записей")
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка при проверке структуры базы данных: {e}")

def get_all_matches(db_file_path='hockey_matches.db'):
    """Получает все матчи из базы данных"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, match_text, match_time, team1, team2, score, stadion, city, viewers
            FROM matches
            ORDER BY match_time, id
        ''')
        
        matches = cursor.fetchall()
        conn.close()
        
        print(f"\nВсе матчи ({len(matches)}):")
        for match in matches:
            print(f"ID: {match[0]}, Время: {match[2]}, {match[3]} - {match[4]} {match[5]}, Стадион: {match[6]}, Зрители: {match[8]}")
        
        return matches
        
    except Exception as e:
        print(f"Ошибка при получении матчей: {e}")
        return []

def get_match_details(match_id, db_file_path='hockey_matches.db'):
    """Получает детальную информацию о конкретном матче"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        # Основная информация о матче
        cursor.execute('SELECT * FROM matches WHERE id = ?', (match_id,))
        match = cursor.fetchone()
        
        if not match:
            print("Матч не найден")
            return
        
        print(f"\nДетали матча ID {match_id}:")
        print(f"Матч: {match[1]}")
        print(f"Время: {match[2]}")
        print(f"Команды: {match[3]} - {match[4]}")
        print(f"Счет: {match[5]}")
        print(f"Стадион: {match[6]}, Город: {match[7]}")
        print(f"Зрители: {match[8]}, Заполняемость: {match[9]}%, Вместимость: {match[10]}")
        
        # Составы команд
        cursor.execute('''
            SELECT team_name, GROUP_CONCAT(player_name, ', ')
            FROM team_lineups 
            WHERE match_id = ?
            GROUP BY team_name
        ''', (match_id,))
        
        lineups = cursor.fetchall()
        print("\nСоставы команд:")
        for team, players in lineups:
            player_count = len(players.split(',')) if players else 0
            print(f"{team} ({player_count} игроков): {players}")
        
        # Голы
        cursor.execute('''
            SELECT team_name, player_name 
            FROM goals 
            WHERE match_id = ?
            ORDER BY team_name
        ''', (match_id,))
        
        goals = cursor.fetchall()
        print("\nЗабитые голы:")
        team1_goals = [g for g in goals if g[0] == match[3]]
        team2_goals = [g for g in goals if g[0] == match[4]]
        
        print(f"{match[3]}: {len(team1_goals)} голов")
        for team, player in team1_goals:
            print(f"  - {player}")
            
        print(f"{match[4]}: {len(team2_goals)} голов")
        for team, player in team2_goals:
            print(f"  - {player}")
        
        # Удаления
        cursor.execute('SELECT player_name FROM kick_offs WHERE match_id = ?', (match_id,))
        kick_offs = cursor.fetchall()
        
        print(f"\nУдаления ({len(kick_offs)}):")
        for kick_off in kick_offs:
            print(f"  - {kick_off[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка при получении деталей матча: {e}")

def get_player_stats(db_file_path='hockey_matches.db'):
    """Получает статистику игроков по голам"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT player_name, COUNT(*) as goals 
            FROM goals 
            WHERE player_name IS NOT NULL AND player_name != ''
            GROUP BY player_name 
            ORDER BY goals DESC 
            LIMIT 20
        ''')
        
        scorers = cursor.fetchall()
        
        print("\nТоп-20 бомбардиров:")
        for i, (player, goals) in enumerate(scorers, 1):
            print(f"  {i:2d}. {player}: {goals} голов")
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка при получении статистики игроков: {e}")

def get_most_penalized_players(db_file_path='hockey_matches.db'):
    """Получает игроков с наибольшим количеством удалений"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT player_name, COUNT(*) as penalties 
            FROM kick_offs 
            WHERE player_name IS NOT NULL AND player_name != ''
            GROUP BY player_name 
            ORDER BY penalties DESC 
            LIMIT 15
        ''')
        
        penalized = cursor.fetchall()
        
        print("\nТоп-15 игроков по удалениям:")
        for i, (player, penalties) in enumerate(penalized, 1):
            print(f"  {i:2d}. {player}: {penalties} удалений")
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка при получении статистики удалений: {e}")

def get_matches_by_time(time_range, db_file_path='hockey_matches.db'):
    """Получает матчи по временному диапазону"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        if '-' in time_range:
            start_time, end_time = time_range.split('-')
            cursor.execute('''
                SELECT id, match_time, team1, team2, score, stadion, city
                FROM matches 
                WHERE match_time BETWEEN ? AND ?
                ORDER BY match_time
            ''', (start_time.strip(), end_time.strip()))
        else:
            cursor.execute('''
                SELECT id, match_time, team1, team2, score, stadion, city
                FROM matches 
                WHERE match_time = ?
                ORDER BY match_time
            ''', (time_range,))
        
        matches = cursor.fetchall()
        conn.close()
        
        print(f"\nМатчи в диапазоне {time_range} ({len(matches)}):")
        for match in matches:
            print(f"ID: {match[0]}, Время: {match[1]}, {match[2]} - {match[3]} {match[4]}, Стадион: {match[5]}")
        
        return matches
        
    except Exception as e:
        print(f"Ошибка при получении матчей по времени: {e}")
        return []