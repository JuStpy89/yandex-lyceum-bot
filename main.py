import requests
import logging
import sqlite3
from random import choice
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

url = "https://restcountries.com/v3.1/independent?status=true"
countries = requests.get(url).json()

conn = sqlite3.connect("db/users.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               name VARCHAR,
               telegram_id INTEGER,
               points INTEGER,
               answering BOOL,
               aliases VARCHAR
)""")
conn.commit()


async def handler(update, context):
    user = update.message.from_user
    text = update.message.text
    answering, aliases = cursor.execute(f"""SELECT answering, aliases FROM users WHERE telegram_id = '{user.id}'""").fetchone()
    if answering:
        points = cursor.execute(f"""SELECT points FROM users WHERE telegram_id = '{user.id}'""").fetchone()[0]
        keyboard = [
            [InlineKeyboardButton("Play again", callback_data="play")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        aliases = aliases.replace("-", "\-").split(",")
        if text.lower() in aliases:
            points += 1
            rep_text = f"*Congrats, this is the right answer and you get one point*"
        else:
            points -= 1
            rep_text = f"*Unfortunately this is an incorrect answer and you lose one point, the correct answer is '{aliases[1].title()}'*"
        await update.message.reply_text(rep_text, parse_mode="MarkdownV2", reply_markup=reply_markup)
        cursor.execute(f"""UPDATE users SET points = {points} WHERE telegram_id = '{user.id}'""")
        conn.commit()
        cursor.execute(f"""UPDATE users SET answering = False WHERE telegram_id = '{user.id}'""")
        conn.commit()


async def get_points(update, context):
    user = update.message.from_user
    points = cursor.execute(f"""SELECT points FROM users WHERE telegram_id = '{user.id}'""").fetchone()[0]
    await update.message.reply_text(f"*Your number of points is \{points}\!*", parse_mode="MarkdownV2")


async def callback_handler(update, context):
    query = update.callback_query
    user = query.from_user
    answering, aliases, points = cursor.execute(f"""SELECT answering, aliases, points FROM users WHERE telegram_id = '{user.id}'""").fetchone()
    if query.data == "play" and not answering:
        c = choice(countries)
        rus_name = c["translations"]["rus"]["common"]
        name = c["name"]["common"]
        names = f"{rus_name},{name}"
        picture = c["flags"]["png"]
        cursor.execute(f"""UPDATE users SET answering = True WHERE telegram_id = '{user.id}'""")
        conn.commit()
        cursor.execute(f"""UPDATE users SET aliases = '{names.lower()}' WHERE telegram_id = '{user.id}'""")
        conn.commit()
        keyboard = [
            [InlineKeyboardButton("Skip", callback_data="skip")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_photo(picture, parse_mode="MarkdownV2", caption=f"*Guess which country this flag belongs to*", reply_markup=reply_markup)
    elif query.data == "skip" and answering:
        cursor.execute(f"""UPDATE users SET answering = False WHERE telegram_id = '{user.id}'""")
        conn.commit()
        cursor.execute(f"""UPDATE users SET points = {points - 1} WHERE telegram_id = '{user.id}'""")
        conn.commit()
        keyboard = [
            [InlineKeyboardButton("Play again", callback_data="play")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        rep_aliases = aliases.replace('-', '\-').split(',')[1].title()
        await query.message.reply_text(f"*The correct answer is {rep_aliases}, you skipped the question so you lose one point*", parse_mode="MarkdownV2", reply_markup=reply_markup)


async def play(update, context):
    user = update.message.from_user
    answering = cursor.execute(f"""SELECT answering FROM users WHERE telegram_id = '{user.id}'""").fetchone()[0]
    if not answering:
        c = choice(countries)
        rus_name = c["translations"]["rus"]["common"]
        name = c["name"]["common"]
        names = f"{rus_name},{name}"
        picture = c["flags"]["png"]
        cursor.execute(f"""UPDATE users SET answering = True WHERE telegram_id = '{user.id}'""")
        conn.commit()
        cursor.execute(f"""UPDATE users SET aliases = '{names.lower()}' WHERE telegram_id = '{user.id}'""")
        conn.commit()
        keyboard = [
            [InlineKeyboardButton("Skip", callback_data="skip")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_photo(picture, parse_mode="MarkdownV2", caption="*Guess which country this flag belongs to*", reply_markup=reply_markup)


async def start(update, context):
    user = update.message.from_user
    if not cursor.execute(f"""SELECT * FROM users WHERE telegram_id = {user.id}""").fetchone():
        cursor.execute(f"""INSERT INTO users(name, telegram_id, points, answering, aliases) VALUES ('{user.name}', '{user.id}', 0, False, '')""")
        conn.commit()
    keyboard = [
        [KeyboardButton("/play")],
        [KeyboardButton("/points")],
        [KeyboardButton("/help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"*👋 Hi\! Welcome to the FlagGuesserBot\!*\n\n📍/play \- _to start a game_\n📍/points \- _to get your points number_", parse_mode="MarkdownV2", reply_markup=reply_markup)


async def help(update, context):
    keyboard = [
        [KeyboardButton("/play")],
        [KeyboardButton("/points")],
        [KeyboardButton("/help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"*Will be added soon\!*", parse_mode="MarkdownV2", reply_markup=reply_markup)


def run():
    app = Application.builder().token(os.getenv("TOKEN")).build()

    app.add_handler(CommandHandler("points", get_points))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))

    msg_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handler)
    app.add_handler(msg_handler)

    app.add_handler(CallbackQueryHandler(callback_handler))

    app.run_polling()


if __name__ == "__main__":
    run()
