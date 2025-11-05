import sqlite3
import json
import os
import re
from datetime import datetime

def extract_time_from_match_text(match_text):
            """Extracts time from match text"""
            if not match_text:
                return None
            time_pattern = r'^(\d{1,2}:\d{2})'
            match = re.match(time_pattern, match_text.strip())
            return match.group(1) if match else None
        