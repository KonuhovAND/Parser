import asyncio
import os
import signal
import warnings
from telegram.warnings import PTBUserWarning
from tg_tools.sm import dev_profile, scenario
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from telegram.error import TelegramError
from tools.run_parser import runner

# Suppress the specific per_message warning
warnings.filterwarnings('ignore', message='.*per_message.*', category=PTBUserWarning)

DATA, MODE, LEAGUE = range(3)
class tg_bot:
    def __init__(self, token_bot):
        self.token_bot = token_bot
        self.application = None
    # Tools commands
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
        
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        button_data = query.data  
        
        if button_data in ['json', 'db', 'both']:
            context.user_data['mode'] = button_data
            await query.edit_message_text(f"✓ Selected format: {button_data}")
            
            keyboard = [
                [InlineKeyboardButton("NHL", callback_data='nhl')],
                [InlineKeyboardButton("KHL", callback_data='_superleague')],
                [InlineKeyboardButton("VHL", callback_data='_highleague')],
                [InlineKeyboardButton("MHL", callback_data='mhl')],
                [InlineKeyboardButton("All", callback_data='all')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text='Choose league:',
                reply_markup=reply_markup
            )
            return LEAGUE
            
        elif button_data in ['nhl', '_superleague', '_highleague', 'mhl', 'all']:
            context.user_data['league'] = button_data
            await query.edit_message_text(f"✓ Selected league: {button_data.upper()}")
            
            chat_id = query.message.chat_id
            days = context.user_data.get('days')
            mode = context.user_data.get('mode')
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🚀 Starting parser...\n\n📅 Days: {days}\n📦 Format: {mode}\n🏒 League: {button_data.upper()}"
            )
            
            asyncio.create_task(self.run_parser_and_send_file(chat_id, mode, days, button_data))
            
            return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Operation cancelled")
        return ConversationHandler.END
    
    async def post_init(self, application: Application):
            await application.bot.set_my_commands([
                ("start", "Show main menu"),
                ("parse", "Parse to JSON/DB/both"),
                ("info", "Show commands"),
                ("cancel", "Cancel operation"),
            ])
        
    # Parsing commands
    async def parse(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Enter amount of days to parse:")
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

      
        
        
    async def receive_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        days = update.message.text.strip()
        
        
        # Validate input
        if not days.isdigit() or int(days) <= 0:
            await update.message.reply_text("❌ Please enter a valid positive number of days:")
            return DATA
        
        # Store days
        context.user_data['days'] = int(days)
        
    
        keyboard = [
            [InlineKeyboardButton("JSON", callback_data='json')],
            [InlineKeyboardButton("DB file", callback_data='db')],
            [InlineKeyboardButton("Both", callback_data='both')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Choose output format:', reply_markup=reply_markup)
        
        # Return the next state
        return MODE


   

    def main(self):
        self.application = Application.builder().token(self.token_bot).build()
        
        # Conversation handler with proper callback handling
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("parse", self.parse)],
            states={
                DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_data)],
                MODE: [CallbackQueryHandler(self.button_handler)],
                LEAGUE: [CallbackQueryHandler(self.button_handler)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            per_chat=True,
            per_message=False,
        )
        
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("info", self.info))
        self.application.add_handler(conv_handler)
        
        
        self.application.post_init = self.post_init
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def run(self):
        try:
            self.main()
        except Exception as exc:
            print(f"Bot error: {exc}")


