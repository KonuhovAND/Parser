***

# 🏒 Hockey Matches Parser

An automated tool to scrape detailed hockey match data from championat.com, covering multiple leagues (KHL, VHL, MHL, NHL). The project outputs data in JSON format and an SQLite database, and includes a Telegram bot for easy data access.

## Overview

Hockey Matches Parser extracts comprehensive hockey match information including scores, stadium statistics, team lineups, goal scorers, and penalties. It supports smart caching to avoid re-parsing matches and includes robust error handling for reliable data collection.

## Features

- Multi-league support: KHL, VHL, MHL, NHL  
- Detailed match data:
  - Match results, scores, timings  
  - Stadium attendance and capacity  
  - Team lineups (up to 40 players per match)  
  - Goal scorers and penalty info  
- Outputs in JSON and SQLite database  
- Interactive Telegram bot interface for querying data  
- Caching for improved performance and efficiency  
- Error handling for stable operation  

## Prerequisites

- Python 3.12 or higher  
- Chrome or Chromium browser installed and in system PATH  
- Git (for cloning repository)  
- Telegram account (for bot usage)  

## Installation

1. Clone repository:  
   ```bash
   git clone https://github.com/KonuhovAND/Parser.git
   cd Parser
   ```
2. (Recommended) Create and activate a virtual environment:  
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Windows: venv\Scripts\activate
   ```
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Telegram Bot Setup

- Create a Telegram bot with @BotFather  
- Copy the bot token  
- Update the token in `tg_tools/_token.py`:
  ```python
  _token = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
  ```

### Browser Setup

Ensure Chrome/Chromium is installed and accessible via system PATH. The parser runs Chrome in headless mode.

## Usage

### Run Telegram Bot

Start the Telegram bot to interactively parse and access match data:
```bash
python running_bot.py
```

### Run Parser Directly

Run parser without Telegram interface; outputs JSON and SQLite:
```bash
python tools/run_parser.py
```
Created files: `matches_data.json` and `hockey_matches.db`

### Use as Python API

Example to run parser and access data:
```python
from tools.run_parser import runner
from tools.generate_db import get_all_matches, get_player_stats

# Run the parser
runner()

# Get data
matches = get_all_matches()
top_scorers = get_player_stats()
```

## Project Structure

```
Parser/
├── bot.py                    # Telegram bot main file
├── cache/                    # Cache for parsed matches
├── hockey_matches.db         # SQLite database output
├── matches_data.json         # JSON data output
├── requirements.txt          # Dependencies
├── tg_tools/                 # Telegram bot utilities
│   ├── _token.py        # Bot token config
│   └── sm.py                 # Bot state management
└── tools/                    # Parsing core modules
    ├── cache.py              # Caching logic
    ├── extract_teams_from_match_text.py  # Team name extraction
    ├── generate_db.py        # DB generation
    ├── is_valid_name.py      # Name validation
    ├── json_adapter.py       # JSON handling
    ├── read_data_from_page.py # Parsing logic
    └── run_parser.py         # Parser runner
```

## Data Structure

### JSON Output Example
```json
{
  "matches": [
    {
      "text": "13:30 Сибирь – Амур 0 : 2 окончен",
      "team1": "Сибирь",
      "team2": "Амур",
      "score": "0:2",
      "url": "...",
      "source_url": "...",
      "stats": {
        "stadion": "Сибирь-Арена",
        "city": "Новосибирск",
        "viewers": 11496,
        "attendance_percent": 95,
        "max_capacity": 12000,
        "lineup_team1": ["Player1", "Player2"],
        "lineup_team2": ["PlayerA", "PlayerB"],
        "goals_team1": [],
        "goals_team2": ["GoalScorer1", "GoalScorer2"],
        "kick_offs": ["PlayerX", "PlayerY"]
      }
    }
  ]
}
```

### Database Schema Summary

- **matches**: match info (teams, scores, venue, attendance)  
- **team_lineups**: players per team per match  
- **goals**: goal scorers data  
- **kick_offs**: penalty info  

## Telegram Bot Commands

| Command      | Description                        |
|--------------|----------------------------------|
| `/start`     | Display main menu                 |
| `/parse`     | Start parsing and receive data   |
| `/info`      | Show detailed command info       |
| `/projects`  | Explore developer's other projects|
| `/showskills`| View technical skills            |
| `/contact`   | Get contact details              |

## Development and Contribution

- Add new URL sources in `tools/run_parser.py`  
- Update CSS selectors in `tools/read_data_from_page.py` if site changes  
- Extend database schema in `tools/generate_db.py` for new data  
- Add new bot commands in `bot.py`  
- Contributions welcome via forks and pull requests

## Performance

- Processes around 25 matches in 2-5 minutes  
- Uses headless browser with optimizations and caching  

## Troubleshooting

- Verify Chrome/Chromium installation and system PATH  
- Check Telegram bot token and permissions  
- Clear cache in `cache/` folder if errors occur  
- Update CSS selectors if scraping errors arise  

## License

MIT License

## Contact

**Andrey Konukhov**  
GitHub: [@KonuhovAND](https://github.com/KonuhovAND)  
Telegram: Contact through bot

***
