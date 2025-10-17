```markdown
🏒 Hockey Matches Parser

    A comprehensive web scraper for collecting hockey match data from championat.com with SQLite database integration and Telegram bot interface

[![Python Version](https://img.shields.iohttps://img.shields.io/badge/license-MIT-green.ntents

    Overview

    Features

    Prerequisites

    Installation

    Configuration

    Usage

    Project Structure

    Data Structure

    Telegram Bot Commands

    Development

    Performance

    Troubleshooting

    Contributing

    License

    Contact

🎯 Overview

Hockey Matches Parser is an automated data collection tool that extracts detailed hockey match information from championat.com. The project supports multiple leagues (KHL, VHL, MHL, NHL) and provides structured data access through JSON files, SQLite database, and a user-friendly Telegram bot interface.

​
✨ Features

    Multi-League Support: KHL, VHL, MHL, and NHL match data

    Comprehensive Data Collection:

        Match results (teams, scores, time)

        Stadium statistics (attendance, capacity)

        Team lineups (up to 40 players per match)

        Goal scorers

        Penalty information

    Multiple Output Formats: JSON and SQLite database

    Telegram Bot Interface: Easy access to parsed data

    Smart Caching: Avoids re-parsing already processed matches

    Error Handling: Robust exception handling for reliable operation

🔧 Prerequisites

Before installation, ensure you have:

    Python 3.12 or higher

    Chrome/Chromium browser installed

    Git (for cloning the repository)

    Telegram account (for bot functionality)

📦 Installation
1. Clone the Repository

bash
git clone https://github.com/KonuhovAND/Parser.git
cd Parser

2. Create Virtual Environment (Recommended)

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies

bash
pip install -r requirements.txt

⚙️ Configuration
Telegram Bot Setup

    Create a bot via @BotFather on Telegram

    Copy your bot token

    Update the token in tg_tools/not_a_token.py:

python
_token = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

Browser Configuration

The parser automatically uses Chrome in headless mode. Ensure Chrome/Chromium is installed and accessible in your system PATH.

​
🚀 Usage
Running the Telegram Bot

bash
python bot.py

The bot will start and provide an interactive interface for parsing and accessing match data.

​
Direct Parser Execution

bash
python tools/run_parser.py

This runs the parser without the Telegram interface and saves results to matches_data.json and hockey_matches.db.

​
Python API Usage

python
from tools.run_parser import runner
from tools.generate_db import get_all_matches, get_player_stats

# Run the parser
runner()

# Access database
matches = get_all_matches()
top_scorers = get_player_stats()

📁 Project Structure

text
Parser/
├── bot.py                          # Telegram bot main file
├── cache/                          # Cached parsing results
├── hockey_matches.db               # SQLite database output
├── matches_data.json               # JSON data output
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── tg_tools/                       # Telegram bot utilities
│   ├── not_a_token.py             # Bot token configuration
│   └── sm.py                      # Bot state management
└── tools/                          # Core parsing modules
    ├── cache.py                   # Caching functionality
    ├── extract_teams_from_match_text.py  # Team name extraction
    ├── generate_db.py             # Database generation
    ├── is_valid_name.py           # Name validation
    ├── json_adapter.py            # JSON handling
    ├── read_data_from_page.py     # Main parsing logic
    └── run_parser.py              # Parser execution

📊 Data Structure
JSON Output Format

json
{
  "matches": [
    {
      "text": "13:30 Сибирь – Амур 0 : 2 окончен",
      "team1": "Сибирь",
      "team2": "Амур",
      "score": "0:2",
      "url": "https://www.championat.com/...",
      "source_url": "https://www.championat.com/stat/hockey/#2025-09-07",
      "stats": {
        "stadion": "Сибирь-Арена",
        "city": "Новосибирск",
        "viewers": 11496,
        "attendance_percent": 95,
        "max_capacity": 12000,
        "lineup_team1": ["Луи Доминге", "Антон Красоткин"],
        "lineup_team2": ["Владислав Кара", "Никита Сошников"],
        "goals_team1": [],
        "goals_team2": ["Сергей Дубакин", "Олег Ли"],
        "kick_offs": ["Архип Неколенко", "Иван Мищенко"]
      }
    }
  ],
  "source_urls": ["..."],
  "matches_found": 25
}

Database Schema

matches - Core match information

    id, text, team1, team2, score, url, source_url, stadium, city, viewers, attendance_percent, max_capacity

team_lineups - Player lineups

    id, match_id, team_number, player_name

goals - Goal information

    id, match_id, team_number, player_name

kick_offs - Penalty information

    id, match_id, player_name

🤖 Telegram Bot Commands
Command	Description
/start	Display main menu and welcome message
/parse	Initiate parsing process and receive data files
/info	View detailed command information
/projects	Explore developer's other projects
/showskills	View developer's technical skills
/contact	Get contact information
🛠️ Development
Adding New Data Sources

    Add URLs to the urls list in tools/run_parser.py

​

Verify CSS selectors in tools/read_data_from_page.py match the new source

    ​

    Test parsing with the new source

Extending Functionality

New Statistics: Modify parse_match_lineups() in tools/read_data_from_page.py

​

Additional Tables: Update create_hockey_database() in tools/generate_db.py

​

Bot Commands: Add handlers in bot.py

​
Key Functions
get_js_data_with_selenium(url)

Main parser function that:

    Initializes headless browser with optimized settings

    Locates match elements via CSS selectors

    Extracts basic match information

    Handles StaleElementReferenceException errors

    Implements caching to avoid duplicate processing

    ​

parse_match_lineups(driver, match_url, score_team1, score_team2, team1, team2)

Detailed match statistics parser:

    Opens match page in new tab

    Extracts stadium information

    Parses team lineups

    Identifies goal scorers

    Collects penalty data

    ​

create_hockey_database(json_file_path, db_file_path)

Database generator:

    Creates normalized SQLite schema

    Validates data before insertion

    Creates indexes for query optimization

    Handles relationships between tables

    ​

📈 Performance

    Processing Speed: 2-5 minutes for 25 matches

​

Optimization Features:

    Result caching for processed matches

    Headless browser mode

    Disabled images and CSS loading

    Parallel match processing capability

        ​

🔍 Troubleshooting
Common Issues

Browser not found

    Ensure Chrome/Chromium is installed

    Check system PATH configuration

Telegram bot not responding

    Verify token in tg_tools/not_a_token.py

    ​

    Check bot permissions with BotFather

Parsing errors

    Website structure may have changed

    Update CSS selectors in read_data_from_page.py

    ​

    Clear cache directory and retry

🤝 Contributing

Contributions are welcome! Please follow these steps:

    Fork the repository

    Create a feature branch (git checkout -b feature/AmazingFeature)

    Commit your changes (git commit -m 'Add some AmazingFeature')

    Push to the branch (git push origin feature/AmazingFeature)

    Open a Pull Request

📄 License

This project is open source and available under the MIT License.
👤 Contact

Andrey Konukhov

    GitHub: @KonuhovAND

    Telegram: Contact via bot

    Project Link: https://github.com/KonuhovAND/Parser

⭐ Star this repository if you find it helpful!
```
