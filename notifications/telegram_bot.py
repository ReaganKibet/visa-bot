# notifications/telegram_bot.py
import telebot
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def send_alert_with_buttons(slot_data: dict):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_open = telebot.types.InlineKeyboardButton("✅ Open Booking", url="http://localhost:8000/bookings/new")
    btn_pause = telebot.types.InlineKeyboardButton("⏸️ Pause Monitor", callback_data="pause_monitor")
    btn_done = telebot.types.InlineKeyboardButton("✅ Mark Done", callback_data="mark_done")
    markup.add(btn_open, btn_pause, btn_done)

    message = (
        f"🆕 Slot available for Portugal visa!\n"
        f"📍 Flow: Mozambique → Portugal\n"
        f"🕒 Detected: {slot_data['timestamp']}\n"
        f"🔗 [View Page]({slot_data['url']})"
    )
    bot.send_message(TELEGRAM_CHAT_ID, message, reply_markup=markup, parse_mode='Markdown')