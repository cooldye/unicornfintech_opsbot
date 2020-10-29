import configparser
import logging
import telegram

from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters, Updater, CommandHandler

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

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

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
# updater.dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
updater.dispatcher.add_handler(CommandHandler('hello', hello))

updater.start_polling()
updater.idle()

if __name__ == "__main__":
    # Running server
    app.run(debug=True)