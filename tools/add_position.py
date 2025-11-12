import json
import random
import sqlite3
import os

# Путь к JSON и БД (указать нужные пути из проекта)
JSON_PATH = "matches_data.json"
DB_PATH = "hockey_matches.db"

# Возможные амплуа игроков в хоккее


def update_db_schema_and_insert_positions():
    if not os.path.exists(DB_PATH):
        print(f"База данных не найдена по пути {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Добавляем колонку position в таблицу match_lineups
        cursor.execute("ALTER TABLE match_lineups ADD COLUMN position TEXT")
        print("Столбец 'position' добавлен в таблицу match_lineups")
    except sqlite3.OperationalError:
        print("Столбец 'position' уже существует или возникла ошибка")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for match in data.get("matches", []):
        for team_key, team_name_key in [
            ("lineup_team1", "team1"),
            ("lineup_team2", "team2"),
        ]:
            players = match.get("stats", {}).get(team_key, [])
            team_name = match.get(team_name_key, "")

            # Для каждого игрока обновляем поле position в match_lineups
            for player_info in players:
                player_name = player_info["name"]
                position = player_info["position"]

                # Обновляем position для игрока по match, команде и игроку
                # Для поиска player_id и team_id сделаем вложенный запрос
                cursor.execute(
                    """
                    UPDATE match_lineups
                    SET position = ?
                    WHERE match_id = (
                        SELECT id FROM matches WHERE match_text = ?
                    ) AND team_id = (
                        SELECT id FROM teams WHERE name = ?
                    ) AND player_id = (
                        SELECT id FROM players WHERE name = ?
                    )
                """,
                    (position, match.get("text", ""), team_name, player_name),
                )

    conn.commit()
    conn.close()
    print("База данных обновлена: позиции игроков добавлены.")
