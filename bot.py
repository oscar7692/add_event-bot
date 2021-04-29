#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

import logging
import os
import telegram

from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import (Updater, CommandHandler, CallbackContext,
                         MessageHandler, Filters)
from telegram.forcereply import ForceReply


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO
    )
logger = logging.getLogger(__name__)

# get token from env variable
# TOKEN = os.getenv("TOKEN")
TOKEN = "1552672771:AAHGbdwsbz7Ahxa1HqF7sSNbeMtZSUevQwA"

# bot commands
def start(update, context):
    logger.info(f"user:{update.effective_user['username']} started a new session")

    user_id = update.effective_user['username']

    response = f"""*Welcome {user_id}* to add\_event\-bot\n
    I'll help you to create events and schedule them,
    type /help to get some hints about my features"""

    context.bot.sendMessage(chat_id=update.effective_user['id'], 
                            parse_mode=ParseMode.MARKDOWN_V2, text=response)

# function to handle the /help command
def help(update, context):
    menu = """Commands available\n
    /start: start bot
    /help: list all commands availables
    /setevent: create an event format eventname YYYY/MM/DD HH:MM
    /delevent: delete an event format eventname
    /checkevents: list all available events"""

    user_id = update.effective_user['id']
    context.bot.sendMessage(chat_id=user_id, parse_mode=ParseMode.MARKDOWN_V2,
                            text=menu)

# function to handle errors occured in the dispatcher 
def error(update, context):
    update.message.reply_text('an error occured')

# function to handle normal text 
def text(update, context):
    text_received = update.message.text
    update.message.reply_text(f'did you said "{text_received}" ?')

def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def setevent(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        event = [int(i) for i in context.args[0].split(',')]
        eventtime = datetime(event[0],event[1],event[2],event[3],event[4])
        print(datetime.now())
        if eventtime < datetime.now():
            err_sms = f"""
            Sorry we can't go back to future! choose a valid date\n
            your typed {eventtime}"""
            update.message.reply_text(err_sms)
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, eventtime, context=chat_id, 
                                    name=str(chat_id))

        text = 'Event successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except Exception as err:
        update.message.reply_text(f'Usage: /setevent YYYY,M,D,H,M {err}')
    # msg1 = """Set a date for the envent, use the following format:
    # eventname YYYY/MM/DD HH:MM"""
    # update.message.reply_text(msg1)
    # update.message.reply_text(reply_markup=ForceReply(selective=True), 
    #                             text="Reply to this message")
    pass

def main():
    # create the updater, that will automatically create also a dispatcher 
    # and a queue tomake them dialoge
    updater = Updater(my_bot.token, use_context=True)
    dispatcher = updater.dispatcher

    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("setevent", setevent))

    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))

    # add an handler for errors
    dispatcher.add_error_handler(error)

    # start your shiny new bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':

    main()