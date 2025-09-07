import sqlite3
import os


def create_database():
    conn = sqlite3.connect('hockey_stats.db')
    cursor = conn.cursor()

    # Таблица команд
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        league TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица игроков
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        team_id INTEGER,
        position TEXT,
        number INTEGER,
        birth_date TEXT,
        nationality TEXT,
        FOREIGN KEY (team_id) REFERENCES teams (id)
    )
    ''')

    # Таблица матчей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        home_team_id INTEGER,
        away_team_id INTEGER,
        score_home INTEGER,
        score_away INTEGER,
        arena TEXT,
        tournament TEXT,
        season TEXT,
        FOREIGN KEY (home_team_id) REFERENCES teams (id),
        FOREIGN KEY (away_team_id) REFERENCES teams (id)
    )
    ''')

    # Таблица голов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        team_id INTEGER,
        player_id INTEGER,
        period INTEGER,
        time TEXT,
        assist1_player_id INTEGER,
        assist2_player_id INTEGER,
        FOREIGN KEY (match_id) REFERENCES matches (id),
        FOREIGN KEY (team_id) REFERENCES teams (id),
        FOREIGN KEY (player_id) REFERENCES players (id),
        FOREIGN KEY (assist1_player_id) REFERENCES players (id),
        FOREIGN KEY (assist2_player_id) REFERENCES players (id)
    )
    ''')

    # Таблица удалений
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS penalties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        team_id INTEGER,
        player_id INTEGER,
        period INTEGER,
        time TEXT,
        duration INTEGER,
        reason TEXT,
        FOREIGN KEY (match_id) REFERENCES matches (id),
        FOREIGN KEY (team_id) REFERENCES teams (id),
        FOREIGN KEY (player_id) REFERENCES players (id)
    )
    ''')

    # Таблица статистики игроков в матче
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        team_id INTEGER,
        time_on_ice TEXT,
        shots INTEGER,
        hits INTEGER,
        blocks INTEGER,
        takeaways INTEGER,
        giveaways INTEGER,
        faceoff_wins INTEGER,
        faceoff_total INTEGER,
        FOREIGN KEY (match_id) REFERENCES matches (id),
        FOREIGN KEY (player_id) REFERENCES players (id),
        FOREIGN KEY (team_id) REFERENCES teams (id)
    )
    ''')

    conn.commit()
    conn.close()

create_database()
