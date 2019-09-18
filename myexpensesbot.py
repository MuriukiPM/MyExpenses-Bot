#!/usr/bin/python3
"""
@ author: PMuriuki
"""
from os import environ as env
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, Filters

from bot.utils import logger
from bot import handlers
from bot.globals import CHOOSING, TYPING_REPLY

# TODO: Add expenses report conversation flow
# TODO: Add step to end session/after period of inactivity
# to require verification on next session
# TODO: Add SMS verification
# TODO: Ask for monthly budgetary limits per category
# TODO: Add output message showing % of budgetary limit used per category
def main():
    # Set up the Updater
    updater = Updater(env.get("TOKEN"))
    dispatcher = updater.dispatcher
    
    # Add dispatchers
    # Start and verify
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start,
                                    pass_user_data=True)],
        states={
            TYPING_REPLY: [MessageHandler(Filters.text, handlers.verify,
                                          pass_user_data=True)],                       
                },
        fallbacks=[]
        ))

    # Enter new expense
    dispatcher.add_handler(ConversationHandler(
        entry_points=[RegexHandler('New Expense', handlers.new,
                                    pass_user_data=True)],
        states = {
            CHOOSING : [RegexHandler('Timestamp', handlers.timestamp,
                                    pass_user_data=True),
                        RegexHandler('Description', handlers.description,
                                    pass_user_data=True),
                        RegexHandler('Category', handlers.category,
                                    pass_user_data=True),
                        RegexHandler('Proof', handlers.proof,
                                    pass_user_data=True),
                        RegexHandler('Amount', handlers.amount,
                                    pass_user_data=True),
                        RegexHandler('Submit', handlers.post,
                                    pass_user_data=True),
                        RegexHandler('Abort', handlers.home,
                                    pass_user_data=True)],
            TYPING_REPLY: [ MessageHandler(Filters.text, handlers.verifyValue,
                                          pass_user_data=True),
                            CommandHandler('home', handlers.home, 
                                            pass_user_data=True),
                            CommandHandler('cancel', handlers.new, 
                                            pass_user_data=True),
                            CommandHandler('done', handlers.value,
                                            pass_user_data=True),
                            CommandHandler('submit', handlers.post,
                                            pass_user_data=True)],
            },
        fallbacks=[]
        ))
    
    # log errors
    dispatcher.add_error_handler(handlers.error)

    # Start the bot
    updater.start_polling()
    
    logger.info("Starting the Chatbot....")
    updater.idle()

if __name__ == "__main__":
    main()
