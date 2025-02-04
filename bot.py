import json
import logging
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Insert your bot token here
TOKEN = '8067216971:AAG_bk0_xlDyNTWoYJn0q8WIzSngqmuskZQ' 

DATA_FILE = "data.json"

# Logging setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Load or initialize countdown date
def load_date():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return datetime.strptime(data["target_date"], "%Y-%m-%d")
    except (FileNotFoundError, KeyError, ValueError):
        return datetime.now() + timedelta(days=30)  # Default to 30 days later

def save_date(target_date):
    with open(DATA_FILE, "w") as f:
        json.dump({"target_date": target_date.strftime("%Y-%m-%d")}, f)

# Bot commands
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I will send countdown updates for the KNY Trip.")

async def set_date(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /setdate YYYY-MM-DD")
        return
    
    try:
        new_date = datetime.strptime(context.args[0], "%Y-%m-%d")
        save_date(new_date)
        await update.message.reply_text(f"New countdown date set: {context.args[0]}")
    except ValueError:
        await update.message.reply_text("Invalid date format! Use YYYY-MM-DD.")

async def send_countdown(context: CallbackContext) -> None:
    chat_id = context.job.chat_id
    target_date = load_date()
    today = datetime.now()
    days_left = (target_date - today).days

    if days_left >= 0:
        message = f"KNY Trip is {days_left} days left!"
    else:
        message = "KNY Trip has already happened!"
    
    await context.bot.send_message(chat_id=chat_id, text=message)

async def start_countdown(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    # Add job to scheduler (runs every day at 9 AM)
    context.job_queue.run_daily(send_countdown, time=datetime.now().replace(hour=9, minute=0, second=0), chat_id=chat_id)
    await update.message.reply_text("Daily countdown updates started!")

# Main bot function
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setdate", set_date))
    app.add_handler(CommandHandler("startcountdown", start_countdown))

    app.run_polling()

if __name__ == "__main__":
    main()
