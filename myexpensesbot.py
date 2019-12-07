#!/usr/bin/env python3
##!/usr/bin/python3
"""
@ author: PMuriuki
"""
from os import environ as env
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, Filters

from libs.utils import logger
from bot.handlers import auth, newexpense, expensestats, budgetlimits
# from bot.handlers.newexpense import *
# from bot.handlers.expensestats import *
# from bot.handlers.budgetlimits import *
from bot.globals import CHOOSING, TYPING_REPLY

# TODO: Create dev env on mongo, separate from prod
# TODO: REname "limits" to "budget limits"
# TODO: Add pipeline to accept proof as images and post to API
# TODO: Improve expenses report conversation flow
# TODO: Add step to end session/after period of inactivity
# to require verification on next session
# TODO: Add SMS verification
# TODO: Ask for monthly budgetary limits per category
# TODO: Add output message showing % of budgetary limit used per category
def main():
    # Set up the Updater
    updater = Updater(env.get("TOKEN"),use_context=True)
    dispatcher = updater.dispatcher
    
    # Add dispatchers
    # Start and verify
    # TODO: add a "sorry, that's not a valid choice" fallback
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', auth.start)],
        states={
            TYPING_REPLY: [MessageHandler(Filters.text, auth.verify)],                       
                },
        fallbacks=[]
        ))

    # Enter new expense
    # TODO: add a "sorry, that's not a valid choice" fallback
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('New Expense'), newexpense.newExpense)],
        states = {
            CHOOSING : [MessageHandler(Filters.regex('Timestamp'), newexpense.timestamp),
                        MessageHandler(Filters.regex('Description'), newexpense.description),
                        MessageHandler(Filters.regex('Category'), newexpense.category),
                        MessageHandler(Filters.regex('Proof'), newexpense.proof),
                        MessageHandler(Filters.regex('Amount'), newexpense.amount),
                        MessageHandler(Filters.regex('Submit'), newexpense.postExpense),
                        MessageHandler(Filters.regex('Abort'), auth.home)],
            TYPING_REPLY: [ MessageHandler(Filters.text, newexpense.verifyValue),
                            CommandHandler('home', auth.home),
                            CommandHandler('cancel', newexpense.newExpense),
                            CommandHandler('done', newexpense.nextExpenseField),
                            CommandHandler('submit', newexpense.postExpense)],
            },
        fallbacks=[]
        ))
    
    # Set limits for categories of expenses
    # TODO: add a "sorry, that's not a valid choice" fallback
    # TODO: separate Limits, expenses. limits->view,update,set | expenses->by month, by category
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Expenses Report'), expensestats.expensesReport)],
        states = {
            CHOOSING : [MessageHandler(Filters.regex('Abort'), auth.home),
                        MessageHandler(Filters.regex('Set Limits'), budgetlimits.setLimits),
                        MessageHandler(Filters.regex('Update Limits'), budgetlimits.updateLimitsWRVW),
                        MessageHandler(Filters.regex('View Limits'), budgetlimits.viewLimits),
                        MessageHandler(Filters.regex('View Expenses By Month'), expensestats.totalByMonth),
                        MessageHandler(Filters.regex('View Expenses By Category'), expensestats.totalByCategory),
                        CommandHandler('update', budgetlimits.updateLimitsnoRVW),
                        CommandHandler('home', auth.home),
                        CommandHandler('cancel', expensestats.expensesReport)],
            TYPING_REPLY : [MessageHandler(Filters.regex('(^Set limit for )'), budgetlimits.limitKey),
                            MessageHandler(Filters.regex('^[0-9]'), budgetlimits.limitValue),
                            CommandHandler('done', budgetlimits.reviewLimits),
                            # MessageHandler(Filters.regex('^[a-zA-Z]'), selectMonth),
                            MessageHandler(Filters.regex('(?:Jan$|Feb$|Mar$|Apr$|May$|June$|July$|Aug$|Sept$|Oct$|Nov$|Dec$)'), expensestats.selectMonth),
                            MessageHandler(Filters.regex('(^Total expenses for )'), expensestats.selectCategory),
                            CommandHandler('submit', budgetlimits.postLimits),
                            CommandHandler('edit', budgetlimits.setLimits),
                            CommandHandler('cancel', expensestats.expensesReport),
                            CommandHandler('home', auth.home)],
        },
        fallbacks=[]
    ))
    
    # log errors
    dispatcher.add_error_handler(auth.error)

    # Start the bot
    updater.start_polling()
    
    logger.info("Starting the Chatbot....")
    updater.idle()

if __name__ == "__main__":
    main()
