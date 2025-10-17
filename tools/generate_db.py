import sqlite3
import json
import os
import re
from datetime import datetime


def create_hockey_database(json_file_path, db_file_path='hockey_matches.db'):
    """
    Creates SQLite database with hockey match information from JSON file
    
    Args:
        json_file_path (str): Path to JSON file with match data
        db_file_path (str): Path to save SQLite database
    """
    
    # Remove existing database if exists
    if os.path.exists(db_file_path):
        os.remove(db_file_path)
        print(f"Removed existing database: {db_file_path}")
    
    try:
        # Load data from JSON
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Connect to database
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Create Teams table (normalized structure)
        cursor.execute('''
            CREATE TABLE teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Create Stadiums table
        cursor.execute('''
            CREATE TABLE stadiums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                max_capacity INTEGER,
                UNIQUE(name, city)
            )
        ''')
        
        # Create Matches table
        cursor.execute('''
            CREATE TABLE matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_text TEXT,
                match_time TEXT,
                team1_id INTEGER NOT NULL,
                team2_id INTEGER NOT NULL,
                score TEXT,
                stadium_id INTEGER,
                viewers INTEGER DEFAULT 0,
                attendance_percent INTEGER DEFAULT 0,
                FOREIGN KEY (team1_id) REFERENCES teams (id),
                FOREIGN KEY (team2_id) REFERENCES teams (id),
                FOREIGN KEY (stadium_id) REFERENCES stadiums (id)
            )
        ''')
        
        # Create Players table
        cursor.execute('''
            CREATE TABLE players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Create Match Lineups table (junction table)
        cursor.execute('''
            CREATE TABLE match_lineups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                FOREIGN KEY (match_id) REFERENCES matches (id),
                FOREIGN KEY (team_id) REFERENCES teams (id),
                FOREIGN KEY (player_id) REFERENCES players (id),
                UNIQUE(match_id, player_id)
            )
        ''')
        
        # Create Goals table
        cursor.execute('''
            CREATE TABLE goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                FOREIGN KEY (match_id) REFERENCES matches (id),
                FOREIGN KEY (team_id) REFERENCES teams (id),
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # Create Penalties table (renamed from kick_offs for clarity)
        cursor.execute('''
            CREATE TABLE penalties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                FOREIGN KEY (match_id) REFERENCES matches (id),
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        def extract_time_from_match_text(match_text):
            """Extracts time from match text"""
            if not match_text:
                return None
            time_pattern = r'^(\d{1,2}:\d{2})'
            match = re.match(time_pattern, match_text.strip())
            return match.group(1) if match else None
        
        def get_or_create_team(team_name):
            """Gets team ID or creates new team"""
            if not team_name or not team_name.strip():
                return None
            
            cursor.execute('SELECT id FROM teams WHERE name = ?', (team_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                cursor.execute('INSERT INTO teams (name) VALUES (?)', (team_name,))
                return cursor.lastrowid
        
        def get_or_create_player(player_name):
            """Gets player ID or creates new player"""
            if not player_name or not player_name.strip():
                return None
            
            cursor.execute('SELECT id FROM players WHERE name = ?', (player_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                cursor.execute('INSERT INTO players (name) VALUES (?)', (player_name,))
                return cursor.lastrowid
        
        def get_or_create_stadium(stadium_name, city, max_capacity):
            """Gets stadium ID or creates new stadium"""
            if not stadium_name or stadium_name == 'Неизвестно':
                stadium_name = 'Unknown'
            if not city or city == 'Неизвестно':
                city = 'Unknown'
            
            cursor.execute('SELECT id FROM stadiums WHERE name = ? AND city = ?', 
                          (stadium_name, city))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                cursor.execute('''
                    INSERT INTO stadiums (name, city, max_capacity) 
                    VALUES (?, ?, ?)
                ''', (stadium_name, city, max_capacity or 0))
                return cursor.lastrowid
        
        # Process matches
        matches_processed = 0
        for match in data['matches']:
            try:
                stats = match.get('stats', {})
                match_time = extract_time_from_match_text(match.get('text', ''))
                
                # Get or create teams
                team1_id = get_or_create_team(match.get('team1', ''))
                team2_id = get_or_create_team(match.get('team2', ''))
                
                if not team1_id or not team2_id:
                    continue
                
                # Get or create stadium
                stadium_id = get_or_create_stadium(
                    stats.get('stadion', 'Unknown'),
                    stats.get('city', 'Unknown'),
                    stats.get('max_capacity', 0)
                )
                
                # Insert match
                cursor.execute('''
                    INSERT INTO matches (
                        match_text, match_time, team1_id, team2_id, score,
                        stadium_id, viewers, attendance_percent
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match.get('text', ''),
                    match_time,
                    team1_id,
                    team2_id,
                    match.get('score', ''),
                    stadium_id,
                    stats.get('viewers', 0) or 0,
                    stats.get('attendance_percent', 0) or 0
                ))
                
                match_id = cursor.lastrowid
                matches_processed += 1
                
                # Insert lineups for team 1
                for player_name in stats.get('lineup_team1', []):
                    if player_name and player_name.strip():
                        player_id = get_or_create_player(player_name)
                        if player_id:
                            cursor.execute('''
                                INSERT OR IGNORE INTO match_lineups (match_id, team_id, player_id)
                                VALUES (?, ?, ?)
                            ''', (match_id, team1_id, player_id))
                
                # Insert lineups for team 2
                for player_name in stats.get('lineup_team2', []):
                    if player_name and player_name.strip():
                        player_id = get_or_create_player(player_name)
                        if player_id:
                            cursor.execute('''
                                INSERT OR IGNORE INTO match_lineups (match_id, team_id, player_id)
                                VALUES (?, ?, ?)
                            ''', (match_id, team2_id, player_id))
                
                # Insert goals for team 1
                for player_name in stats.get('goals_team1', []):
                    if player_name and player_name.strip():
                        player_id = get_or_create_player(player_name)
                        if player_id:
                            cursor.execute('''
                                INSERT INTO goals (match_id, team_id, player_id)
                                VALUES (?, ?, ?)
                            ''', (match_id, team1_id, player_id))
                
                # Insert goals for team 2
                for player_name in stats.get('goals_team2', []):
                    if player_name and player_name.strip():
                        player_id = get_or_create_player(player_name)
                        if player_id:
                            cursor.execute('''
                                INSERT INTO goals (match_id, team_id, player_id)
                                VALUES (?, ?, ?)
                            ''', (match_id, team2_id, player_id))
                
                # Insert penalties
                for player_name in stats.get('kick_offs', []):
                    if player_name and player_name.strip():
                        player_id = get_or_create_player(player_name)
                        if player_id:
                            cursor.execute('''
                                INSERT INTO penalties (match_id, player_id)
                                VALUES (?, ?)
                            ''', (match_id, player_id))
                        
            except Exception as e:
                print(f"Error processing match {match.get('text', 'Unknown')}: {e}")
                continue
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX idx_matches_team1 ON matches(team1_id)')
        cursor.execute('CREATE INDEX idx_matches_team2 ON matches(team2_id)')
        cursor.execute('CREATE INDEX idx_matches_time ON matches(match_time)')
        cursor.execute('CREATE INDEX idx_lineups_match ON match_lineups(match_id)')
        cursor.execute('CREATE INDEX idx_lineups_team ON match_lineups(team_id)')
        cursor.execute('CREATE INDEX idx_lineups_player ON match_lineups(player_id)')
        cursor.execute('CREATE INDEX idx_goals_match ON goals(match_id)')
        cursor.execute('CREATE INDEX idx_goals_player ON goals(player_id)')
        cursor.execute('CREATE INDEX idx_penalties_match ON penalties(match_id)')
        cursor.execute('CREATE INDEX idx_penalties_player ON penalties(player_id)')
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"\n✓ Database successfully created: {db_file_path}")
        print(f"✓ Processed matches: {matches_processed} of {len(data['matches'])}")
        
        # Check database structure
        check_database_structure(db_file_path)
        
    except Exception as e:
        print(f"Error creating database: {e}")
        if 'conn' in locals():
            conn.close()


def check_database_structure(db_file_path):
    """Checks structure of created database"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("\n" + "="*60)
        print("DATABASE STRUCTURE")
        print("="*60)
        
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Table: {table_name}")
            print("-" * 60)
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for column in columns:
                col_name = column[1]
                col_type = column[2]
                is_pk = " [PRIMARY KEY]" if column[5] else ""
                is_not_null = " [NOT NULL]" if column[3] else ""
                print(f"  • {col_name:<20} {col_type:<15} {is_pk}{is_not_null}")
        
        print("\n" + "="*60)
        print("RECORD COUNTS")
        print("="*60)
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name:<20} {count:>10} records")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database structure: {e}")


def get_all_matches(db_file_path='hockey_matches.db'):
    """Gets all matches from database"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                m.id, 
                m.match_time, 
                t1.name as team1, 
                t2.name as team2, 
                m.score,
                s.name as stadium,
                s.city,
                m.viewers
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.id
            JOIN teams t2 ON m.team2_id = t2.id
            LEFT JOIN stadiums s ON m.stadium_id = s.id
            ORDER BY m.match_time, m.id
        ''')
        
        matches = cursor.fetchall()
        conn.close()
        
        print(f"\n{'='*100}")
        print(f"ALL MATCHES ({len(matches)})")
        print(f"{'='*100}\n")
        
        for match in matches:
            print(f"ID: {match[0]:3d} | Time: {match[1]:5s} | {match[2]:25s} vs {match[3]:25s} | "
                  f"Score: {match[4]:7s} | Stadium: {match[5]:20s} | Viewers: {match[7]:,}")
        
        return matches
        
    except Exception as e:
        print(f"Error getting matches: {e}")
        return []


def get_match_details(match_id, db_file_path='hockey_matches.db'):
    """Gets detailed information about specific match with improved lineup display"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        # Main match information
        cursor.execute('''
            SELECT 
                m.match_text,
                m.match_time,
                t1.name as team1,
                t2.name as team2,
                m.score,
                s.name as stadium,
                s.city,
                m.viewers,
                m.attendance_percent,
                s.max_capacity,
                m.team1_id,
                m.team2_id
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.id
            JOIN teams t2 ON m.team2_id = t2.id
            LEFT JOIN stadiums s ON m.stadium_id = s.id
            WHERE m.id = ?
        ''', (match_id,))
        
        match = cursor.fetchone()
        
        if not match:
            print("Match not found")
            return
        
        team1_name, team2_name = match[2], match[3]
        team1_id, team2_id = match[10], match[11]
        
        print(f"\n{'='*100}")
        print(f"MATCH DETAILS - ID: {match_id}")
        print(f"{'='*100}\n")
        print(f"Match:       {match[0]}")
        print(f"Time:        {match[1]}")
        print(f"Teams:       {team1_name} vs {team2_name}")
        print(f"Score:       {match[4]}")
        print(f"Stadium:     {match[5]}, {match[6]}")
        print(f"Attendance:  {match[7]:,} viewers ({match[8]}% capacity, max: {match[9]:,})")
        
        # Team lineups with improved formatting
        print(f"\n{'='*100}")
        print(f"TEAM LINEUPS")
        print(f"{'='*100}\n")
        
        # Team 1 lineup
        cursor.execute('''
            SELECT p.name
            FROM match_lineups ml
            JOIN players p ON ml.player_id = p.id
            WHERE ml.match_id = ? AND ml.team_id = ?
            ORDER BY p.name
        ''', (match_id, team1_id))
        
        team1_lineup = cursor.fetchall()
        
        print(f"┌─ {team1_name} ({len(team1_lineup)} players) " + "─" * (97 - len(team1_name) - len(str(len(team1_lineup)))))
        for i, (player,) in enumerate(team1_lineup, 1):
            print(f"│ {i:2d}. {player}")
        print("└" + "─" * 99)
        
        # Team 2 lineup
        cursor.execute('''
            SELECT p.name
            FROM match_lineups ml
            JOIN players p ON ml.player_id = p.id
            WHERE ml.match_id = ? AND ml.team_id = ?
            ORDER BY p.name
        ''', (match_id, team2_id))
        
        team2_lineup = cursor.fetchall()
        
        print(f"\n┌─ {team2_name} ({len(team2_lineup)} players) " + "─" * (97 - len(team2_name) - len(str(len(team2_lineup)))))
        for i, (player,) in enumerate(team2_lineup, 1):
            print(f"│ {i:2d}. {player}")
        print("└" + "─" * 99)
        
        # Goals with team separation
        print(f"\n{'='*100}")
        print(f"GOALS SCORED")
        print(f"{'='*100}\n")
        
        cursor.execute('''
            SELECT t.name, p.name, COUNT(*) as goal_count
            FROM goals g
            JOIN teams t ON g.team_id = t.id
            JOIN players p ON g.player_id = p.id
            WHERE g.match_id = ?
            GROUP BY t.name, p.name
            ORDER BY t.name, goal_count DESC
        ''', (match_id,))
        
        goals = cursor.fetchall()
        
        team1_goals = [(p, c) for t, p, c in goals if t == team1_name]
        team2_goals = [(p, c) for t, p, c in goals if t == team2_name]
        
        print(f"┌─ {team1_name}: {sum(c for _, c in team1_goals)} goals " + "─" * (97 - len(team1_name) - len(str(sum(c for _, c in team1_goals)))))
        if team1_goals:
            for player, count in team1_goals:
                goals_str = f"{'⚽ ' * count}"
                print(f"│ {player:<50} {goals_str}")
        else:
            print("│ (no goals)")
        print("└" + "─" * 99)
        
        print(f"\n┌─ {team2_name}: {sum(c for _, c in team2_goals)} goals " + "─" * (97 - len(team2_name) - len(str(sum(c for _, c in team2_goals)))))
        if team2_goals:
            for player, count in team2_goals:
                goals_str = f"{'⚽ ' * count}"
                print(f"│ {player:<50} {goals_str}")
        else:
            print("│ (no goals)")
        print("└" + "─" * 99)
        
        # Penalties
        print(f"\n{'='*100}")
        print(f"PENALTIES")
        print(f"{'='*100}\n")
        
        cursor.execute('''
            SELECT p.name, COUNT(*) as penalty_count
            FROM penalties pen
            JOIN players p ON pen.player_id = p.id
            WHERE pen.match_id = ?
            GROUP BY p.name
            ORDER BY penalty_count DESC, p.name
        ''', (match_id,))
        
        penalties = cursor.fetchall()
        
        if penalties:
            for i, (player, count) in enumerate(penalties, 1):
                print(f"{i:2d}. {player:<50} {'🟨 ' * count}({count})")
        else:
            print("No penalties in this match")
        
        conn.close()
        
    except Exception as e:
        print(f"Error getting match details: {e}")


def get_player_stats(db_file_path='hockey_matches.db'):
    """Gets player statistics by goals"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, COUNT(*) as goals 
            FROM goals g
            JOIN players p ON g.player_id = p.id
            GROUP BY p.name 
            ORDER BY goals DESC, p.name
            LIMIT 20
        ''')
        
        scorers = cursor.fetchall()
        
        print(f"\n{'='*100}")
        print(f"TOP 20 SCORERS")
        print(f"{'='*100}\n")
        
        for i, (player, goals) in enumerate(scorers, 1):
            bar = '█' * (goals * 2)
            print(f"{i:2d}. {player:<50} {goals:3d} goals {bar}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error getting player statistics: {e}")


def get_most_penalized_players(db_file_path='hockey_matches.db'):
    """Gets players with most penalties"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, COUNT(*) as penalty_count 
            FROM penalties pen
            JOIN players p ON pen.player_id = p.id
            GROUP BY p.name 
            ORDER BY penalty_count DESC, p.name
            LIMIT 15
        ''')
        
        penalized = cursor.fetchall()
        
        print(f"\n{'='*100}")
        print(f"TOP 15 PENALIZED PLAYERS")
        print(f"{'='*100}\n")
        
        for i, (player, penalties) in enumerate(penalized, 1):
            bar = '▓' * penalties
            print(f"{i:2d}. {player:<50} {penalties:3d} penalties {bar}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error getting penalty statistics: {e}")


def get_team_statistics(db_file_path='hockey_matches.db'):
    """Gets comprehensive team statistics"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        print(f"\n{'='*100}")
        print(f"TEAM STATISTICS")
        print(f"{'='*100}\n")
        
        cursor.execute('''
            SELECT 
                t.name,
                COUNT(DISTINCT m.id) as matches_played,
                COALESCE(SUM(g.goal_count), 0) as total_goals,
                COALESCE(SUM(p.penalty_count), 0) as total_penalties
            FROM teams t
            LEFT JOIN matches m ON (t.id = m.team1_id OR t.id = m.team2_id)
            LEFT JOIN (
                SELECT team_id, match_id, COUNT(*) as goal_count
                FROM goals
                GROUP BY team_id, match_id
            ) g ON t.id = g.team_id AND m.id = g.match_id
            LEFT JOIN (
                SELECT ml.team_id, pen.match_id, COUNT(*) as penalty_count
                FROM penalties pen
                JOIN match_lineups ml ON pen.match_id = ml.match_id AND pen.player_id = ml.player_id
                GROUP BY ml.team_id, pen.match_id
            ) p ON t.id = p.team_id AND m.id = p.match_id
            GROUP BY t.name
            ORDER BY matches_played DESC, total_goals DESC
        ''')
        
        teams = cursor.fetchall()
        
        print(f"{'Team':<30} {'Matches':>8} {'Goals':>8} {'Penalties':>10} {'Goals/Match':>12}")
        print("-" * 100)
        
        for team, matches, goals, penalties in teams:
            goals_per_match = goals / matches if matches > 0 else 0
            print(f"{team:<30} {matches:>8} {goals:>8} {penalties:>10} {goals_per_match:>12.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error getting team statistics: {e}")


def get_matches_by_time(time_range, db_file_path='hockey_matches.db'):
    """Gets matches by time range"""
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        if '-' in time_range:
            start_time, end_time = time_range.split('-')
            cursor.execute('''
                SELECT 
                    m.id, 
                    m.match_time, 
                    t1.name, 
                    t2.name, 
                    m.score,
                    s.name as stadium
                FROM matches m
                JOIN teams t1 ON m.team1_id = t1.id
                JOIN teams t2 ON m.team2_id = t2.id
                LEFT JOIN stadiums s ON m.stadium_id = s.id
                WHERE m.match_time BETWEEN ? AND ?
                ORDER BY m.match_time, m.id
            ''', (start_time.strip(), end_time.strip()))
        else:
            cursor.execute('''
                SELECT 
                    m.id, 
                    m.match_time, 
                    t1.name, 
                    t2.name, 
                    m.score,
                    s.name as stadium
                FROM matches m
                JOIN teams t1 ON m.team1_id = t1.id
                JOIN teams t2 ON m.team2_id = t2.id
                LEFT JOIN stadiums s ON m.stadium_id = s.id
                WHERE m.match_time = ?
                ORDER BY m.id
            ''', (time_range,))
        
        matches = cursor.fetchall()
        conn.close()
        
        print(f"\n{'='*100}")
        print(f"MATCHES IN TIME RANGE: {time_range} ({len(matches)} matches)")
        print(f"{'='*100}\n")
        
        for match in matches:
            print(f"ID: {match[0]:3d} | Time: {match[1]:5s} | {match[2]:25s} vs {match[3]:25s} | "
                  f"Score: {match[4]:7s} | Stadium: {match[5]}")
        
        return matches
        
    except Exception as e:
        print(f"Error getting matches by time: {e}")
        return []



