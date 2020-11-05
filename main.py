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

def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    update.message.reply_text('請選擇環境',
        reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton("PROD", callback_data='PROD'),
                InlineKeyboardButton("BETA", callback_data='BETA'),
                InlineKeyboardButton("ALPHA", callback_data='ALPHA')
            ]]))

MARKUP_1 = InlineKeyboardMarkup([[
    InlineKeyboardButton("Q", callback_data='Q'),
    InlineKeyboardButton("QQ", callback_data='QQ'),
    InlineKeyboardButton("QQQ", callback_data='QQQ')
]])

MARKUP_2 = InlineKeyboardMarkup([
    [InlineKeyboardButton('k', callback_data='two')]
])

def env(update: telegram.Update, context: telegram.ext.CallbackContext):
    try:
        #data = update.callback_query.data

        logger.info('message_id:{}'.format(update.callback_query.message.message_id))

        update.message.reply_text('請選擇環境', MARKUP_1)

        #update.callback_query.edit_message_text(text='QQ1234', chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, MARKUP_1)

        #if 'PROD' == data:
        #    update.callback_query.edit_message_reply_markup('Q', MARKUP_1)
        #elif 'BETA' == data:
        #    update.callback_query.edit_message_reply_markup('chatid, messageid', MARKUP_2)
        #else:
        #    update.callback_query.edit_message_reply_markup('chatid, messageid', MARKUP_2)
    except Exception as e:
        print(e)

FIRST, SECOND = range(2)

def start2(update: telegram.Update, context: telegram.ext.CallbackContext):
    keyboard = [
        [InlineKeyboardButton(u"Next", callback_data=str(FIRST))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        u"Start handler, Press next",
        reply_markup=reply_markup
    )
    return FIRST

def first(update: telegram.Update, context: telegram.ext.CallbackContext):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton(u"Next", callback_data=str(SECOND))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"First CallbackQueryHandler, Press next"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.effective_message.bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    return SECOND

def second(update: telegram.Update, context: telegram.ext.CallbackContext):
    query = update.callback_query
    update.effective_message.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"Second CallbackQueryHandler"
    )
    return


# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
# updater.dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
#updater.dispatcher.add_handler(CommandHandler('start', start))
#updater.dispatcher.add_handler(CallbackQueryHandler(env))

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start2', start2)],
    states={
        FIRST: [CallbackQueryHandler(first)],
        SECOND: [CallbackQueryHandler(second)]
    },
    fallbacks=[CommandHandler('start', start2)]
)
updater.dispatcher.add_handler(conv_handler)

updater.start_polling()
updater.idle()

if __name__ == "__main__":
    # Running server
    app.run(debug=True)