#!/usr/bin/python3
"""
@ author: PMuriuki
"""
from os import environ as env
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, Filters

from libs.utils import logger
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
    # TODO: add a "sorry, that's not a valid choice" fallback
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
    # TODO: add a "sorry, that's not a valid choice" fallback
    dispatcher.add_handler(ConversationHandler(
        entry_points=[RegexHandler('New Expense', handlers.newExpense,
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
                        RegexHandler('Submit', handlers.postExpense,
                                    pass_user_data=True),
                        RegexHandler('Abort', handlers.home,
                                    pass_user_data=True)],
            TYPING_REPLY: [ MessageHandler(Filters.text, handlers.verifyValue,
                                          pass_user_data=True),
                            CommandHandler('home', handlers.home, 
                                            pass_user_data=True),
                            CommandHandler('cancel', handlers.newExpense, 
                                            pass_user_data=True),
                            CommandHandler('done', handlers.value,
                                            pass_user_data=True),
                            CommandHandler('submit', handlers.postExpense,
                                            pass_user_data=True)],
            },
        fallbacks=[]
        ))
    
    # Set limits for categories of expenses
    # TODO: add a "sorry, that's not a valid choice" fallback
    dispatcher.add_handler(ConversationHandler(
        entry_points=[RegexHandler('Expenses Report', handlers.expensesReport,
                                    pass_user_data=True)],
        states = {
            CHOOSING : [RegexHandler('Abort', handlers.home,
                                    pass_user_data=True),
                        RegexHandler('Set Limits', handlers.setLimits,
                                    pass_user_data=True),
                        RegexHandler('Update Limits', handlers.updateLimitsWRVW,
                                    pass_user_data=True),
                        RegexHandler('View Limits', handlers.viewLimits,
                                    pass_user_data=True),
                        RegexHandler('View Expenses', handlers.viewExpenses,
                                    pass_user_data=True),
                        CommandHandler('update', handlers.updateLimitsnoRVW, 
                                    pass_user_data=True),
                        CommandHandler('home', handlers.home, 
                                    pass_user_data=True),
                        CommandHandler('cancel', handlers.expensesReport, 
                                    pass_user_data=True),
                        MessageHandler(Filters.text, handlers.limitKey,
                                    pass_user_data=True),
                        CommandHandler('done', handlers.reviewLimits,
                                    pass_user_data=True)],
            TYPING_REPLY : [MessageHandler(Filters.regex('^[0-9]'), handlers.limitValue,
                                            pass_user_data=True),
                            MessageHandler(Filters.regex('^[a-zA-Z]'), handlers.selectMonth,
                                            pass_user_data=True),
                            CommandHandler('submit', handlers.postLimits,
                                            pass_user_data=True),
                            CommandHandler('edit', handlers.setLimits, 
                                            pass_user_data=True),
                            CommandHandler('cancel', handlers.expensesReport, 
                                            pass_user_data=True),
                            CommandHandler('home', handlers.home, 
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
