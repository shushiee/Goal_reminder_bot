import os
import logging
import sys
import time
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import owner_id, bot_token, goals_list

# Bot configuration
BOT_TOKEN = os.getenv(bot_token, "")
OWNER_ID = os.getenv(owner_id, "")  
goals = goals_list 

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask server
app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "Bot is running!"}, 200

def run_web_server():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

def restart_bot():
    """Restarts the bot process."""
    try:
        logger.info("Restarting bot...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        logger.exception("Failed to restart bot.")

async def is_owner(update: Update):
    return update.effective_user and update.effective_user.id == OWNER_ID

async def send_goal_reminder(application):
    while True:
        await asyncio.sleep(3600)  # Wait for 1 hour
        goal_text = "\n".join([f"- {goal}" for goal in goals])
        await application.bot.send_message(OWNER_ID, f"Hourly Goal Reminder:\n{goal_text}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    await update.message.reply_text("Welcome! Use /setgoals to update your goals.")

async def set_goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    global goals
    goals = update.message.text.split("\n")[1:]  # Extract goals from message
    await update.message.reply_text("Goals updated successfully!")

if __name__ == "__main__":
    try:
        Thread(target=run_web_server, daemon=True).start()
        
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        loop = asyncio.get_event_loop()
        loop.create_task(send_goal_reminder(app))
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("setgoals", set_goals))
        
        logger.info("Starting Goal Reminder Bot...")
        app.run_polling()
    except Exception as e:
        logger.exception("Critical error occurred. Restarting bot...")
        restart_bot()