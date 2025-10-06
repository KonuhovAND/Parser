dev_profile = r"""
PYTHON DEVELOPER v2.3 (JUNIOR EDITION)
------------------------------------
[SYSTEM STATUS]
• Coding Skills: >>>-- 70%
• Problem Solving: >>--- 60%
• Coffee Consumption: >>>>- 90%
------------------------------------
[ACTIVE PROJECTS]
- Telegram API (Running)
- Data Analysis Tool (Debugging)
- Personal Portfolio (Updating)
------------------------------------
[RECENT ACTIVITY]
✔ Fixed index out of range bug
✔ Learned about decorators
✔ Pushed code to GitHub
------------------------------------
[QUICK LINKS]
/projects-- View Projects
/showskils -- Show Skills
/contact -- Contact Info
/exit -- Exit
------------------------------------
"""
github = "https://github.com/KonuhovAND"
showskils = [
    "https://leetcode.com/u/KonuhovAND/",
    "https://monkeytype.com/profile/Andrew_Konuhov",
]
contact = "https://t.me/Andrew_Konuhov"

scenario = {
    "projects": {
        "log": "User selected Projects",
        "links": {
            "links": "https://github.com/KonuhovAND",
        },
        "statment": "Here are my projects",
    },
    "showskils": {
        "log": "User selected Skills",
        "statment": "My current skills:",
        "links": {
            "leetcode": "https://leetcode.com/u/KonuhovAND/",
            "monkeytype": "https://monkeytype.com/profile/Andrew_Konuhov",
        },
    },
    "contact": {
        "log": "User selected Contact",
        "statment": "Contact information:",
        "links": {
            "tg": "https://t.me/Andrew_Konuhov",
        },
    },
    "exit": {
        "log": "User selected Exit",
        "statment": "Goodbye! ",
    },
    "help": {
        "statment": """
🚀 Quick Commands:
/projects - Show my projects
/skills - Display my skills
/contact - Get contact info
/start - Show main menu
            """,
        "log": "User askes for help",
    },
}

