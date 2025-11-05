# 🏒 Hockey Matches Parser

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/v/release/KonuhovAND/Parser)](https://github.com/KonuhovAND/Parser/releases)
[![GitHub stars](https://img.shields.io/github/stars/KonuhovAND/Parser)](https://github.com/KonuhovAND/Parser/stargazers)

An automated tool to scrape detailed hockey match data from championat.com, covering multiple leagues (KHL, VHL, MHL, NHL). The project outputs data in JSON format and an SQLite database, and includes a Telegram bot for easy data access.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Structure](#data-structure)
- [Telegram Bot Commands](#telegram-bot-commands)
- [API Reference](#api-reference)
- [Development](#development)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 🎯 Overview

Hockey Matches Parser is a comprehensive data scraping solution that extracts detailed hockey match information from championat.com. It provides intelligent caching, robust error handling, and multiple output formats to ensure reliable data collection across various hockey leagues.

**Key Capabilities:**
- Multi-league support with comprehensive match data extraction
- Smart caching system to avoid redundant parsing
- Interactive Telegram bot interface for real-time queries
- Dual output formats (JSON and SQLite database)
- Headless browser automation with optimizations

## ✨ Features

### 🏟️ Multi-League Support
- **KHL** (Kontinental Hockey League)
- **VHL** (Supreme Hockey League) 
- **MHL** (Junior Hockey League)
- **NHL** (National Hockey League)

### 📊 Comprehensive Match Data
- **Match Information**: Results, scores, timings, match status
- **Venue Details**: Stadium names, cities, attendance figures
- **Team Statistics**: Full lineups (up to 40 players per match)
- **Performance Data**: Goal scorers, penalty information, kick-offs
- **Attendance Analytics**: Viewer counts, capacity percentages

### 🤖 Advanced Features
- **Interactive Telegram Bot**: Real-time data queries and parsing control
- **Smart Caching**: Prevents re-parsing of existing matches
- **Dual Output Formats**: JSON files and SQLite database
- **Error Handling**: Robust operation with detailed logging
- **Headless Browser**: Optimized Chrome automation

## 📋 Prerequisites

- **Python**: 3.12 or higher
- **Browser**: Chrome or Chromium (accessible via system PATH)
- **Git**: For repository cloning
- **Telegram Account**: For bot functionality (optional)

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/KonuhovAND/Parser.git
cd Parser
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Telegram Bot Setup

1. **Create Bot**: Message [@BotFather](https://t.me/BotFather) on Telegram
2. **Get Token**: Copy your bot token from BotFather
3. **Configure Token**: Update `tg_tools/_token.py`:
   ```python
   _token = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
   ```

### Browser Configuration

Ensure Chrome/Chromium is installed and accessible via system PATH. The parser automatically runs in headless mode for optimal performance.

## 💻 Usage

### Interactive Telegram Bot
Start the Telegram bot for interactive parsing and data access:
```bash
python running_bot.py
```

### Direct Parser Execution
Run the parser without Telegram interface:
```bash
python tools/read_data_from_page.py
```

**Output Files:**
- `matches_data.json` - JSON formatted match data
- `hockey_matches.db` - SQLite database

### Python API Integration

```python
# Import required modules
from tools.database_tools.generate_db import get_all_matches, get_player_stats
from tools.json_tools.json_adapter import load_matches_data

# Load and process match data
matches = get_all_matches()
top_scorers = get_player_stats()

# Access JSON data
json_data = load_matches_data()
print(f"Total matches parsed: {len(json_data['matches'])}")
```

## 📁 Project Structure

```
Parser/
├── 📄 README.md                     # Project documentation
├── 📄 requirements.txt              # Python dependencies
├── 📄 main.py                       # Main application entry
├── 📄 running_bot.py                # Telegram bot launcher
├── 📄 .gitignore                    # Git ignore rules
├── 📄 hockey_matches.db             # Generated SQLite database
├── 📄 matches_data.json             # Generated JSON output
│
├── 📂 tg_tools/                     # Telegram bot utilities
│   ├── 📄 _token.py                 # Bot token configuration
│   └── 📄 sm.py                     # State management
│
└── 📂 tools/                        # Core parsing modules
    ├── 📂 cache_tools/              # Caching mechanisms
    ├── 📂 database_tools/           # Database operations
    ├── 📂 json_tools/               # JSON handling
    ├── 📄 extract_teams_from_match_text.py  # Team name extraction
    ├── 📄 generate_urls_to_parse.py # URL generation logic
    ├── 📄 is_valid_name.py          # Name validation utilities
    └── 📄 read_data_from_page.py    # Core parsing engine
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
      "url": "https://www.championat.com/hockey/_matchReport/...",
      "source_url": "https://www.championat.com/hockey/khl/",
      "stats": {
        "stadion": "Сибирь-Арена",
        "city": "Новосибирск",
        "viewers": 11496,
        "attendance_percent": 95,
        "max_capacity": 12000,
        "lineup_team1": ["Player1", "Player2", "..."],
        "lineup_team2": ["PlayerA", "PlayerB", "..."],
        "goals_team1": [],
        "goals_team2": ["GoalScorer1", "GoalScorer2"],
        "kick_offs": ["PlayerX", "PlayerY"]
      }
    }
  ]
}
```

### Database Schema

| Table | Description | Key Fields |
|-------|-------------|------------|
| **matches** | Core match information | teams, scores, venue, attendance |
| **team_lineups** | Player rosters per match | match_id, team, players |
| **goals** | Goal scoring data | scorer, team, match_id |
| **kick_offs** | Penalty information | player, team, match_id |

## 🤖 Telegram Bot Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/start` | Display main menu and bot info | Initial bot interaction |
| `/parse` | Start parsing process and receive data | Trigger data collection |
| `/info` | Show detailed command information | Get help and documentation |
| `/projects` | Explore developer's other projects | View portfolio |
| `/showskills` | Display technical skills and stack | View capabilities |
| `/contact` | Get contact and support details | Reach out for help |

## 📚 API Reference

### Core Functions

```python
# Data extraction
from tools.read_data_from_page import extract_match_data
match_data = extract_match_data(url)

# Database operations  
from tools.database_tools.generate_db import create_database, insert_match
create_database()
insert_match(match_data)

# JSON handling
from tools.json_tools.json_adapter import save_to_json, load_from_json
save_to_json(data, "output.json")
loaded_data = load_from_json("output.json")

# Caching
from tools.cache_tools.cache import is_cached, cache_match
if not is_cached(match_url):
    cache_match(match_url, match_data)
```

## 🛠️ Development

### Adding New Features

**New League Support:**
```python
# Add league URLs in tools/generate_urls_to_parse.py
LEAGUE_URLS = {
    'khl': 'https://www.championat.com/hockey/khl/',
    'new_league': 'https://www.championat.com/hockey/new_league/'
}
```

**CSS Selector Updates:**
```python
# Update selectors in tools/read_data_from_page.py
SELECTORS = {
    'match_info': '.match-info-class',
    'new_element': '.new-element-class'
}
```

**Database Schema Extensions:**
```python
# Extend schema in tools/database_tools/generate_db.py
def create_new_table():
    cursor.execute('''
        CREATE TABLE new_data (
            id INTEGER PRIMARY KEY,
            match_id INTEGER,
            data_field TEXT,
            FOREIGN KEY (match_id) REFERENCES matches (id)
        )
    ''')
```

### Testing

```bash
# Run basic functionality test
python -c "from tools.read_data_from_page import test_parser; test_parser()"

# Test database connectivity
python -c "from tools.database_tools.generate_db import test_db; test_db()"
```

## ⚡ Performance

- **Processing Speed**: ~25 matches in 2-5 minutes
- **Memory Usage**: Optimized for large datasets with streaming
- **Caching Efficiency**: 90%+ cache hit rate on repeated runs
- **Browser Optimization**: Headless mode with reduced resource usage

### Performance Tips

- Enable caching for repeated parsing sessions
- Use headless browser mode (enabled by default)
- Clear cache periodically for updated match data
- Monitor memory usage during large parsing operations

## 🔧 Troubleshooting

### Common Issues

**Browser Not Found:**
```bash
# Verify Chrome installation
google-chrome --version
# or
chromium --version

# Add to PATH if needed (Linux/macOS)
export PATH=$PATH:/usr/bin/google-chrome
```

**Telegram Bot Token Issues:**
- Verify token format: `1234567890:ABCdefGHIjklMNOpqrSTUvwxyz`
- Check bot permissions with @BotFather
- Ensure token file is correctly configured

**Parsing Errors:**
- Clear cache: `rm -rf tools/cache_tools/cache/*`
- Update CSS selectors if website structure changed
- Check internet connectivity and site accessibility

**Database Errors:**
```bash
# Reset database
rm hockey_matches.db
python -c "from tools.database_tools.generate_db import create_database; create_database()"
```

### Debugging Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with appropriate tests
4. Update documentation as needed
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to new functions
- Include type hints where appropriate
- Write descriptive commit messages

### Areas for Contribution
- Additional league support
- Performance optimizations
- UI/UX improvements for Telegram bot
- Data visualization features
- API integrations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

**Andrey Konukhov**
- **GitHub**: [@KonuhovAND](https://github.com/KonuhovAND)
- **Telegram**: Contact through bot
- **Email**: Available via GitHub profile

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for the hockey community

</div>