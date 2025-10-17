
***

# 🏒 Hockey Matches Parser

> A comprehensive web scraper for collecting hockey match data from championat.com with SQLite database integration and Telegram bot interface

https://img.shields.iohttps://img.shields.io/badge/license-MIT-green.ntents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Structure](#data-structure)
- [Telegram Bot Commands](#telegram-bot-commands)
- [Development](#development)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 🎯 Overview

Hockey Matches Parser is an automated data collection tool that extracts detailed hockey match information from championat.com. The project supports multiple leagues (KHL, VHL, MHL, NHL) and provides structured data access through JSON files, SQLite database, and a user-friendly Telegram bot interface.[4]

## ✨ Features

- **Multi-League Support**: KHL, VHL, MHL, and NHL match data
- **Comprehensive Data Collection**:
  - Match results (teams, scores, time)
  - Stadium statistics (attendance, capacity)
  - Team lineups (up to 40 players per match)
  - Goal scorers
  - Penalty information
- **Multiple Output Formats**: JSON and SQLite database
- **Telegram Bot Interface**: Easy access to parsed data
- **Smart Caching**: Avoids re-parsing already processed matches
- **Error Handling**: Robust exception handling for reliable operation

## 🔧 Prerequisites

Before installation, ensure you have:

- **Python 3.12 or higher**
- **Chrome/Chromium browser** installed
- **Git** (for cloning the repository)
- **Telegram account** (for bot functionality)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/KonuhovAND/Parser.git
cd Parser
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Telegram Bot Setup

1. **Create a bot** via [@BotFather](https://t.me/botfather) on Telegram
2. **Copy your bot token**
3. **Update the token** in `tg_tools/not_a_token.py`:

```python
_token = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
```

### Browser Configuration

The parser automatically uses Chrome in headless mode. Ensure Chrome/Chromium is installed and accessible in your system PATH.[4]

## 🚀 Usage

### Running the Telegram Bot

```bash
python bot.py
```

The bot will start and provide an interactive interface for parsing and accessing match data.[4]

### Direct Parser Execution

```bash
python tools/run_parser.py
```

This runs the parser without the Telegram interface and saves results to `matches_data.json` and `hockey_matches.db`.[4]

### Python API Usage

```python
from tools.run_parser import runner
from tools.generate_db import get_all_matches, get_player_stats

# Run the parser
runner()

# Access database
matches = get_all_matches()
top_scorers = get_player_stats()
```

## 📁 Project Structure

```
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
```

## 📊 Data Structure

### JSON Output Format

```json
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
```

### Database Schema

**matches** - Core match information
- `id`, `text`, `team1`, `team2`, `score`, `url`, `source_url`, `stadium`, `city`, `viewers`, `attendance_percent`, `max_capacity`

**team_lineups** - Player lineups
- `id`, `match_id`, `team_number`, `player_name`

**goals** - Goal information
- `id`, `match_id`, `team_number`, `player_name`

**kick_offs** - Penalty information
- `id`, `match_id`, `player_name`

## 🤖 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Display main menu and welcome message |
| `/parse` | Initiate parsing process and receive data files |
| `/info` | View detailed command information |
| `/projects` | Explore developer's other projects |
| `/showskills` | View developer's technical skills |
| `/contact` | Get contact information |

## 🛠️ Development

### Adding New Data Sources

1. Add URLs to the `urls` list in `tools/run_parser.py`[4]
2. Verify CSS selectors in `tools/read_data_from_page.py` match the new source[4]
3. Test parsing with the new source

### Extending Functionality

**New Statistics**: Modify `parse_match_lineups()` in `tools/read_data_from_page.py`[4]

**Additional Tables**: Update `create_hockey_database()` in `tools/generate_db.py`[4]

**Bot Commands**: Add handlers in `bot.py`[4]

### Key Functions

#### `get_js_data_with_selenium(url)`
Main parser function that:
- Initializes headless browser with optimized settings
- Locates match elements via CSS selectors
- Extracts basic match information
- Handles StaleElementReferenceException errors
- Implements caching to avoid duplicate processing[4]

#### `parse_match_lineups(driver, match_url, score_team1, score_team2, team1, team2)`
Detailed match statistics parser:
- Opens match page in new tab
- Extracts stadium information
- Parses team lineups
- Identifies goal scorers
- Collects penalty data[4]

#### `create_hockey_database(json_file_path, db_file_path)`
Database generator:
- Creates normalized SQLite schema
- Validates data before insertion
- Creates indexes for query optimization
- Handles relationships between tables[4]

## 📈 Performance

- **Processing Speed**: 2-5 minutes for 25 matches[4]
- **Optimization Features**:
  - Result caching for processed matches
  - Headless browser mode
  - Disabled images and CSS loading
  - Parallel match processing capability[4]

## 🔍 Troubleshooting

### Common Issues

**Browser not found**
- Ensure Chrome/Chromium is installed
- Check system PATH configuration

**Telegram bot not responding**
- Verify token in `tg_tools/not_a_token.py`[4]
- Check bot permissions with BotFather

**Parsing errors**
- Website structure may have changed
- Update CSS selectors in `read_data_from_page.py`[4]
- Clear cache directory and retry

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👤 Contact

**Andrey Konukhov**

- GitHub: [@KonuhovAND](https://github.com/KonuhovAND)
- Telegram: [Contact via bot](https://t.me/your_bot_username)
- Project Link: [https://github.com/KonuhovAND/Parser](https://github.com/KonuhovAND/Parser)

---

**⭐ Star this repository if you find it helpful!**

[19](https://www.daytona.io/dotfiles/how-to-write-4000-stars-github-readme-for-your-project)
[20](https://zencoder.ai/blog/docstring-generation-tools-2024)
[21](https://stackoverflow.com/questions/23989232/is-there-a-way-to-represent-a-directory-tree-in-a-github-readme-md)
