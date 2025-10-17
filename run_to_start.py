import shutil
from tg_tools.bot import *


if not os.path.exists("./tg_tools/token.py"):
    with open('./tg_tools/token.py','w') as file:
        _token= input("Enter your telegram bot token: ")
        file.write(f"{_token}")
else: 
    with open('./tg_tools/token.py') as file:
        _token = file.read()

# directory = "./cache"
# for filename in os.listdir(directory):
#     file_path = os.path.join(directory, filename)
#     if os.path.isfile(file_path):
#         os.remove(file_path)
        
if __name__ == "__main__":
    first_et = tg_bot(token_bot=_token)
    first_et.run()