import asyncio
import os
import signal
from tg_tools.sm import dev_profile, scenario
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.error import TelegramError
from tools.run_parser import runner
from time import time
from tg_tools.bot_functions.conversation_handlers_league import *
DATA = []
class tg_bot:
    def __init__(self, token_bot):
        self.token_bot = token_bot
        self.application = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(dev_profile)

    async def options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        option = update.message.text.strip()[1:]
        await update.message.reply_text(scenario[option]["statment"])
        if "links" in scenario[option]:
            for name, link in scenario[option]["links"].items():
                await update.message.reply_text(link)
        if option == "exit":
            os.kill(os.getpid(), signal.SIGINT)

    # Entry point for JSON parsing
    async def parse_to_json(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Enter amount of days to parse:")
        context.user_data['mode'] = 'json'
        return DATA

    # Entry point for DB parsing
    async def parse_to_db(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Enter amount of days to parse:")
        context.user_data['mode'] = 'db'
        return DATA

    # Entry point for both JSON and DB
    async def parse_to_json_and_db(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Enter amount of days to parse:")
        context.user_data['mode'] = 'both'
        return DATA

    

    async def run_parser_and_send_file(self, chat_id, mode, days,league):
        try:
            runner(days=days,league=league)
            await self.send_parser_results(chat_id, mode)
        except Exception as e:
            print(f"Parser error details: {e}")
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Parser failed with error: {str(e)}"
            )

    async def send_parser_results(self, chat_id, mode):
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text="✅ Parsing completed successfully! Sending results..."
            )
            
            if mode == 'json':
                files_to_send = [('matches_data.json', 'Parsed matches data (JSON)')]
            elif mode == 'db':
                files_to_send = [('hockey_matches.db', 'Database with statistics')]
            else:   
                files_to_send = [
                    ('matches_data.json', 'Parsed matches data (JSON)'),
                    ('hockey_matches.db', 'Database with statistics'),
                ]
            
            for filename, description in files_to_send:
                if os.path.exists(filename):
                    with open(filename, 'rb') as file:
                        await self.application.bot.send_document(
                            chat_id=chat_id,
                            document=file,
                            filename=filename,
                            caption=description
                        )
                else:
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=f"⚠️ File {filename} not found"
                    )
            
            await self.application.bot.send_message(
                chat_id=chat_id,
                text="📊 All data sent! Use /info for commands."
            )
                    
        except TelegramError as e:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text="❌ Failed to send files."
            )

    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        info_text = """
🤖 Available Commands:

/start - Show main menu
/parse_json - Parse and get JSON file
/parse_db - Parse and get DB file
/parse_json_and_db - Parse and get both files
/info - Show this help
/cancel - Cancel current operation
        """
        await update.message.reply_text(info_text)

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(update.message.text)

    async def post_init(self, application: Application):
        await application.bot.set_my_commands([
            ("start", "Show main menu"),
            ("parse_json", "Parse to JSON"),
            ("parse_db", "Parse to DB"),
            ("parse_json_and_db", "Parse to both"),
            ("info", "Show commands"),
            ("cancel", "Cancel operation"),
        ])

    def main(self):
        self.application = Application.builder().token(self.token_bot).build()
        
        # Single ConversationHandler with 3 entry points
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("parse_json", self.parse_to_json),
                CommandHandler("parse_db", self.parse_to_db),
                CommandHandler("parse_json_and_db", self.parse_to_json_and_db)
            ],
            states={
                DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_days)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            per_chat=True
        )
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler("info", self.info))
        self.application.add_handler(
            CommandHandler(["help", "projects", "showskils", "contact", "exit"], self.options)
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo)
        )
        
        self.application.post_init = self.post_init
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def run(self):
        try:
            self.main()
        except Exception as exc:
            print(f"Bot error: {exc}")


