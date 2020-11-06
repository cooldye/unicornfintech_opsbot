import configparser
import logging
import telegram
import random, os
import json

from flask import Flask, request
from telegram import message
from telegram.ext import Dispatcher, MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('C:\\Users\\0265\\Documents\\Elton\\WorkSpace\\python\\unicornfintech_opsbot\\config.ini')

x =  '{ "Server Name":"User Service", "IP":"10.10.7.186", "PORT":"Taiwan"}'

configProd = configparser.ConfigParser()
configProd.read('prod.ini')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
token=(config['TELEGRAM']['ACCESS_TOKEN'])
bot = telegram.Bot(token)
updater = Updater(token) # , use_context=False

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    logger.info("webhook_handler")
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

def reply_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """Reply message."""
    text = update.message.text
    update.message.reply_text(text)

############################### Bot ############################################
def start(update: telegram.Update, context: telegram.ext.CallbackContext):
  update.message.reply_text(main_menu_message(),
                            reply_markup=main_menu_keyboard())

def main_menu(update: telegram.Update, context: telegram.ext.CallbackContext):
  query = update.callback_query
  bot = update.effective_message.bot
  bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=main_menu_message(),
                        reply_markup=main_menu_keyboard())

def first_menu(update: telegram.Update, context: telegram.ext.CallbackContext):
  query = update.callback_query
  bot = update.effective_message.bot
  bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=first_menu_message(),
                        reply_markup=first_menu_keyboard())

def second_menu(update: telegram.Update, context: telegram.ext.CallbackContext):
  query = update.callback_query
  bot = update.effective_message.bot
  bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=second_menu_message(),
                        reply_markup=second_menu_keyboard())

# and so on for every callback_data option
def first_submenu(update: telegram.Update, context: telegram.ext.CallbackContext):
  pass

def second_submenu(update: telegram.Update, context: telegram.ext.CallbackContext):
  pass

############################ Keyboards #########################################
def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Option 1', callback_data='m1')],
              [InlineKeyboardButton('Option 2', callback_data='m2')],
              [InlineKeyboardButton('Option 3', callback_data='m3')]]
  return InlineKeyboardMarkup(keyboard)

def first_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Submenu 1-1', callback_data='m1_1')],
              [InlineKeyboardButton('Submenu 1-2', callback_data='m1_2')],
              [InlineKeyboardButton('Main menu', callback_data='main')]]
  return InlineKeyboardMarkup(keyboard)

def second_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Submenu 2-1', callback_data='m2_1')],
              [InlineKeyboardButton('Submenu 2-2', callback_data='m2_2')],
              [InlineKeyboardButton('Main menu', callback_data='main')]]
  return InlineKeyboardMarkup(keyboard)

############################# Messages #########################################
def main_menu_message():
  return 'Choose the option in main menu:'

def first_menu_message():
  return 'Choose the submenu in first menu:'

def second_menu_message():
  return 'Choose the submenu in second menu:'


# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
# updater.dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
#updater.dispatcher.add_handler(CommandHandler('start', start))
#updater.dispatcher.add_handler(CallbackQueryHandler(env))

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
updater.dispatcher.add_handler(CallbackQueryHandler(first_menu, pattern='m1'))
updater.dispatcher.add_handler(CallbackQueryHandler(second_menu, pattern='m2'))
updater.dispatcher.add_handler(CallbackQueryHandler(first_submenu, pattern='m1_1'))
updater.dispatcher.add_handler(CallbackQueryHandler(second_submenu, pattern='m2_1'))

updater.start_polling()
updater.idle()

if __name__ == "__main__":
    # Running server
    app.run(debug=True)