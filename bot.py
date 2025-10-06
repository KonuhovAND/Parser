import asyncio
import os
from tg_tools.not_a_token import _token
from tg_tools.sm import dev_profile, scenario
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
from tools.run_parser import runner


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

    async def parse(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        await update.message.reply_text("Parsing is started! I'll send you the results when finished.")
        
        # Run parser in background
        asyncio.create_task(self.run_parser_and_send_file(chat_id))

    async def run_parser_and_send_file(self, chat_id):
        """Run parser and send file when finished"""
        try:
            # Run the parser
            try:
                runner()
                await self.send_parser_results(chat_id)
            except Exception as e:
                print(f"Parser error details: {e}")
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ Parser failed with error: {str(e)}\n\nCheck the console for details."
                )
                
        except Exception as e:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Unexpected error: {str(e)}"
            ) 

    async def send_parser_results(self, chat_id):
        """Send parser results as files"""
        try:
            # Send completion message
            await self.application.bot.send_message(
                chat_id=chat_id,
                text="✅ Parsing completed successfully! Sending results..."
            )
            
            # List of files to send
            files_to_send = [
                ('matches_data.json', 'Parsed matches data (JSON)'),
                ('hockey_matches.db', 'Database with statistics'),
            ]
            
            # Send each file that exists
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
                        text=f"⚠️ File {filename} not found after parsing"
                    )
            
            # Send additional info
            await self.application.bot.send_message(
                chat_id=chat_id,
                text="📊 All data has been processed and sent!\n"
                     "Use /info to see available commands."
            )
                    
        except TelegramError as e:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text="❌ Failed to send result files."
            )

    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available commands"""
        info_text = """
🤖 Available Commands:

/start - Show main menu
/parse - Start parsing website and get results as files
/info - Show this help message
/projects - View my projects
/showskils - See my skills
/contact - Contact information
/help - Show help menu
/exit - Exit

After using /parse:
- You'll receive matches_data.json with parsed data
- You'll receive hockey_stats.db database file
- Processing may take a few minutes
        """
        await update.message.reply_text(info_text)

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(update.message.text)

    async def post_init(self, application: Application):
        await application.bot.set_my_commands(
            [
                ("start", "Show main menu"),
                ("parse", "Start parsing web site and get files"),
                ("info", "Show available commands"),
                ("projects", "View my projects"),
                ("showskils", "See my skills"),
                ("contact", "Contact information"),
                ("help", "Show help menu"),
                ("exit", "exit"),
            ]
        )

    def main(self):
        self.application = Application.builder().token(self.token_bot).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("parse", self.parse))
        self.application.add_handler(CommandHandler("info", self.info))
        self.application.add_handler(
            CommandHandler(
                ["help", "projects", "showskils", "contact", "exit"], self.options
            )
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


if __name__ == "__main__":
    first_et = tg_bot(token_bot=_token)
    first_et.run()