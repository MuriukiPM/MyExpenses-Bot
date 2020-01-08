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

# TODO: Add output message showing % of budgetary limit used per category
# TODO: add a "sorry, that's not a valid choice" fallback for each handler
def main():
    # Set up the Updater
    updater = Updater(env.get("TOKEN"),use_context=True)
    dispatcher = updater.dispatcher
    
    # Add dispatchers
    # Start and verify
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', auth.start)],
        states={
            TYPING_REPLY: [MessageHandler(Filters.regex('^[a-zA-Z0-9]'), auth.verify)],                       
                },
        fallbacks=[]
        ))

    # Enter new expense
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('New Expense'), newexpense.newExpense)],
        states = {
            CHOOSING : [MessageHandler(Filters.regex('Timestamp'), newexpense.timestamp),
                        MessageHandler(Filters.regex('Description'), newexpense.description),
                        MessageHandler(Filters.regex('Category'), newexpense.category),
                        MessageHandler(Filters.regex('Proof'), newexpense.proof),
                        MessageHandler(Filters.regex('Amount'), newexpense.amount),
                        MessageHandler(Filters.regex('Submit'), newexpense.postExpense),
                        MessageHandler(Filters.regex('Main Menu'), auth.home)],
            TYPING_REPLY: [ MessageHandler(Filters.text, newexpense.verifyValue),
                            CommandHandler('home', auth.home),
                            CommandHandler('cancel', newexpense.newExpense),
                            CommandHandler('done', newexpense.nextExpenseField),
                            CommandHandler('submit', newexpense.postExpense)],
            },
        fallbacks=[]
        ))
    
    # Set budget limits for categories of expenses
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Budget'), budgetlimits.budget)],
        states = {
            CHOOSING : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                        MessageHandler(Filters.regex('Set Budget Limits'), budgetlimits.setBudgetLimits),
                        MessageHandler(Filters.regex('Update Budget Limits'), budgetlimits.updateLimitsWRVW),
                        MessageHandler(Filters.regex('View Budget Limits'), budgetlimits.viewBudgetLimits),
                        CommandHandler('update', budgetlimits.updateLimitsnoRVW),
                        CommandHandler('home', auth.home),
                        CommandHandler('cancel', budgetlimits.budget)],
            TYPING_REPLY : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                            MessageHandler(Filters.regex('(^Set budget limit for )'), budgetlimits.limitKey),
                            MessageHandler(Filters.regex('^[0-9]'), budgetlimits.limitValue),
                            MessageHandler(Filters.regex('Review Budget Limits & Submit'), budgetlimits.reviewBudgetLimits),
                            CommandHandler('submit', budgetlimits.postBudgetLimits),
                            CommandHandler('edit', budgetlimits.setBudgetLimits),
                            CommandHandler('cancel', budgetlimits.budget),
                            CommandHandler('home', auth.home)],
        },
        fallbacks=[]
    ))

    # View various reports from expenses
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Expenses Report'), expensestats.expensesReport)],
        states = {
            CHOOSING : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                        MessageHandler(Filters.regex('View Expenses By Month'), expensestats.totalByMonth),
                        MessageHandler(Filters.regex('View Expenses By Category'), expensestats.totalByCategory),
                        MessageHandler(Filters.regex('^[0-9]'), expensestats.selectYearWMonth),
                        MessageHandler(Filters.regex('(?:Jan$|Feb$|Mar$|Apr$|May$|June$|July$|Aug$|Sept$|Oct$|Nov$|Dec$)'), expensestats.selectMonth),
                        CommandHandler('done', expensestats.viewByMonth),
                        CommandHandler('home', auth.home),
                        CommandHandler('cancel', expensestats.expensesReport)],
            TYPING_REPLY : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                            MessageHandler(Filters.regex('^[0-9]'), expensestats.selectYearWCategory),
                            MessageHandler(Filters.regex('(?:Jan$|Feb$|Mar$|Apr$|May$|June$|July$|Aug$|Sept$|Oct$|Nov$|Dec$)'), expensestats.selectMonth),
                            MessageHandler(Filters.regex('(^Total expenses for )'), expensestats.selectCategory),
                            CommandHandler('edit', budgetlimits.setBudgetLimits),
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
