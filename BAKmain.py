import configparser
import logging
import telegram
import random, os
import json

from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from random import randint

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

configProd = configparser.ConfigParser()
configProd.read('prod.ini')

# 把語錄檔案載入
if os.path.exists('sentences.txt'):
    with open('sentences.txt') as FILE:
        sentences = [sentence.strip() for sentence in FILE]
else:
    sentences = []

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
token=(config['TELEGRAM']['ACCESS_TOKEN'])
bot = telegram.Bot(token)
updater = Updater(token, use_context=True)

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    logger.info("webhook_handler")
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        logger.info("POST")

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

def reply_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """Reply message."""
    text = update.message.text
    update.message.reply_text(text)

def hello(update: telegram.Update, context: telegram.ext.CallbackContext):
    update.message.reply_text('hello, {}'.format(update.message.from_user.first_name))

def add(update: telegram.Update, context: telegram.ext.CallbackContext):
    print('from user:', update.message.from_user.id)
    # 限制只有特定人才能新增語錄
    # if update.message.from_user.id == YOUR_USER_ID_HERE:
    if True:
        sentence = update.message.text[5:].replace('\n', ' ')
        sentences.append(sentence)
        with open('sentences.txt', 'a') as FILE:
            print(sentence, file=FILE)
        update.message.reply_text('已加入：' + sentence)

def say(update: telegram.Update, context: telegram.ext.CallbackContext):
    if sentences:
        update.message.reply_text(random.choice(sentences))
    else:
        update.message.reply_text('I have no words.')

def calc(update: telegram.Update, context: telegram.ext.CallbackContext):
    a, b = randint(1, 100), randint(1, 100)
    update.message.reply_text('{} + {} = ?'.format(a, b),
        reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(str(s), callback_data = '{} {} {}'.format(a, b, s)) for s in range(a + b - randint(1, 3), a + b + randint(1, 3))
            ]]))

def answer(update: telegram.Update, context: telegram.ext.CallbackContext):
    a, b, s = [int(x) for x in update.callback_query.data.split()]
    if a + b == s:
        update.callback_query.edit_message_text('你答對了！')
    else:
        update.callback_query.edit_message_text('你答錯囉！')

hands = ['rock', 'paper', 'scissors']

emoji = {
    'rock': '👊',
    'paper': '✋',
    'scissors': '✌️'
} 

def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    update.message.reply_text('剪刀石頭布！',
        reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(emoji, callback_data = hand) for hand, emoji in emoji.items()
            ]]))

def judge(mine, yours):
    if mine == yours:
        return '平手'
    elif (hands.index(mine) - hands.index(yours)) % 3 == 1:
        return '我贏了'
    else:
        return '我輸了'

def play(update: telegram.Update, context: telegram.ext.CallbackContext):
    try:
        mine = random.choice(hands)
        yours = update.callback_query.data
        update.callback_query.edit_message_text('我出{}，你出{}，{}！'.format(emoji[mine], emoji[yours], judge(mine, yours)))
    except Exception as e:
        print(e)


# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
# updater.dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('add', add))
updater.dispatcher.add_handler(CommandHandler('say', say))
updater.dispatcher.add_handler(CommandHandler('calc', calc))
# updater.dispatcher.add_handler(CallbackQueryHandler(answer))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(play))

updater.start_polling()
updater.idle()

if __name__ == "__main__":
    # Running server
    app.run(debug=True)