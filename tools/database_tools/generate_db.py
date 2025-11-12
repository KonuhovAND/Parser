import sqlite3
import json
import os
import re
from datetime import datetime
from tools.database_tools.extract_time_from_match_text import (
    extract_time_from_match_text,
)

JSON_PATH = "matches_data.json"
DB_PATH = "hockey_matches.db"


def get_player_name(player):
    """
    Возвращает имя игрока из строки или словаря,
    безопасно обрабатывая оба варианта.
    """
    if isinstance(player, dict) and "name" in player:
        return player["name"].strip()
    elif isinstance(player, str):
        return player.strip()
    return None


def create_hockey_database(jsonfilepath=JSON_PATH, dbfilepath=DB_PATH):
    if os.path.exists(dbfilepath):
        os.remove(dbfilepath)
        print(f"Removed existing database: {dbfilepath}")

    with open(jsonfilepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    conn = sqlite3.connect(dbfilepath)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("""
    CREATE TABLE teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_text TEXT,
        match_time TEXT,
        team1_id INTEGER NOT NULL,
        team2_id INTEGER NOT NULL,
        score TEXT,
        stadium_id INTEGER,
        viewers INTEGER,
        attendance_percent INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE match_lineups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        player_id INTEGER NOT NULL,
        position TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE stadiums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        max_capacity INTEGER
    )
    """)

    for match in data.get("matches", []):
        team1 = match.get("team1", "").strip()
        team2 = match.get("team2", "").strip()

        cursor.execute("INSERT OR IGNORE INTO teams(name) VALUES (?)", (team1,))
        cursor.execute("INSERT OR IGNORE INTO teams(name) VALUES (?)", (team2,))

        cursor.execute("SELECT id FROM teams WHERE name=?", (team1,))
        team1_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM teams WHERE name=?", (team2,))
        team2_id = cursor.fetchone()[0]

        match_text = match.get("text", "").strip()
        match_time = extract_time_from_match_text(match_text)

        score = match.get("score", "").strip()

        stadion = match.get("stats", {}).get("stadion", "").strip()
        city = match.get("stats", {}).get("city", "").strip()
        max_capacity = match.get("stats", {}).get("max_capacity", None)

        if stadion:
            cursor.execute(
                "INSERT OR IGNORE INTO stadiums(name, city, max_capacity) VALUES (?, ?, ?)",
                (stadion, city, max_capacity),
            )
            cursor.execute("SELECT id FROM stadiums WHERE name=?", (stadion,))
            stadium_id = cursor.fetchone()[0]
        else:
            stadium_id = None

        cursor.execute(
            """INSERT INTO matches(match_text, match_time, team1_id, team2_id, score, stadium_id)
                          VALUES (?, ?, ?, ?, ?, ?)""",
            (match_text, match_time, team1_id, team2_id, score, stadium_id),
        )
        match_id = cursor.lastrowid

        for team_key, team_id in [
            ("lineup_team1", team1_id),
            ("lineup_team2", team2_id),
        ]:
            players = match.get("stats", {}).get(team_key, [])
            for player in players:
                name = get_player_name(player)
                if not name:
                    continue

                cursor.execute(
                    "INSERT OR IGNORE INTO players(name) VALUES (?)", (name,)
                )
                cursor.execute("SELECT id FROM players WHERE name=?", (name,))
                player_id = cursor.fetchone()[0]

                position = (
                    player["position"]
                    if (isinstance(player, dict) and "position" in player)
                    else None
                )

                cursor.execute(
                    """INSERT INTO match_lineups(match_id, team_id, player_id, position)
                                  VALUES (?, ?, ?, ?)""",
                    (match_id, team_id, player_id, position),
                )

    conn.commit()
    conn.close()
    print("База данных успешно создана и заполнена.")

