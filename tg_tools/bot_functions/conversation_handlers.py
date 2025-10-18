import asyncio
import os
import signal
from tg_tools.sm import dev_profile, scenario
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.error import TelegramError
from tools.run_parser import runner
from time import time
from tg_tools.bot import DATA

# Shared handler: receives and validates days
async def receive_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    days = update.message.text
    leaugue = update.message.text
    # Validate input
    if not days.isdigit():
        await update.message.reply_text("Please enter a valid number of days:")
        return DATA
    if not leaugue in ["nhl","khl","all"]:
        await update.message.reply_text("Please enter a valid league (nhl, khl, mhl, vhl ,all):")
        return DATA
    
    chat_id = update.message.chat_id
    mode = context.user_data.get('mode')
    
    await update.message.reply_text("Parsing is started! I'll send you the file when finished.")
    self.receive_league(self, update, context)
    # Run parser in background
    asyncio.create_task(self.run_parser_and_send_file(chat_id, mode=mode, days=int(days), league=context.user_data.get('league')))
    
    return ConversationHandler.END

async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled")
    return ConversationHandler.END


