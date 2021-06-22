
import telebot
import sqlalchemy

import database
import config

from weather import get_current_weather

bot = telebot.TeleBot(config.TOKEN)

user_data = {}


class NewUser:
    def __init__(self, name):
        self.name = name
        self.location = None
        self.user_id = None

    def __repr__(self):
        return f"{self.name} from {self.location}"


@bot.message_handler(commands=["start"])
def registration(message):
    msg = bot.send_message(message.chat.id, "Hello, Human! Please enter some information.\n"
                           "How can I call you?")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = NewUser(message.text)
        msg = bot.send_message(message.chat.id, f"Nice to meet you, {message.text}!\n"
                               "And where you from? It's need to send weathercast.")
        bot.register_next_step_handler(msg, process_location_step)
    except Exception:
        bot.reply_to(message, "ooooops, something wrong :p")


def process_location_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.location = message.text
        user.user_id = message.from_user.id
        user_data[user_id] = user

        database.add_to_users(user_data[user_id])

        bot.send_message(message.chat.id, f"I was one time in {message.text}! Cool place!")
        bot.send_message(message.chat.id, f"You registered as {user_data[message.chat.id]}.")
        del user_data[user_id]

    except sqlalchemy.exc.IntegrityError:
        bot.reply_to(message, "I know you! You registered already.")

    except Exception as e:
        print(e.__class__.__name__)
        bot.reply_to(message, "ooooops, something wrong :p")


@bot.message_handler(commands=["menu"])
def menu_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            "Current Weather", callback_data="get-weather-now")
    )

    bot.send_message(
        message.chat.id, "You want to see the weather?",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def weather_callback(call):
    if call.data.startswith('get-weather-now'):
        bot.answer_callback_query(call.id)
        sent_weather_now(call.message, call.from_user.id)
    else:
        bot.answer_callback_query(call.id, "Something broke up(")


def sent_weather_now(message, user_id):
    bot.send_message(message.chat.id,
                     get_current_weather(database.get_location(user_id)))


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(message.chat.id, "It's help message. I'm bot with MySQL"
                     "If you ")


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will happen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=1)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == "__main__":

    bot.polling(none_stop=True)
