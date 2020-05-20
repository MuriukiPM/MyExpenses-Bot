#!/usr/bin/python3
##!/usr/bin/env python3
"""
@ author: PMuriuki
"""
import sys
from os import environ as env
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, CallbackQueryHandler, Filters

from libs.utils import logger
from bot.handlers import auth, newexpense, expensestats, budgetlimits, expenseslist, expensessearch
from bot.globals import CHOOSING, TYPING_REPLY

# TODO: Add output message showing % of budgetary limit used per category
# TODO: add a "sorry, that's not a valid choice" fallback for each handler
def main():
    secrets = ['TELEGRAM_BOT_TOKEN', 'URL_POST_EXPENSE', 'URL_SORTDESC', 'URL_CATEGORIES',
               'URL_VIEW_EXPENSE', 'URL_USER_BY_CHATID', 'URL_POST_USER', 
               'MONGO_HOST', 'MONGO_DATABASE_NAME', 'MONGO_COLLECTION_NAME', 
               'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']
    if not all([secret in env for secret in secrets]): 
        logger.error('Be sure to set all environment vars')
        sys.exit(1)
    # Set up the Updater
    updater = Updater(env.get("TELEGRAM_BOT_TOKEN"),use_context=True)
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
    # TODO: Handle unexpected inputs: eg typing year instead of selecting month
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Expenses Report'), expensestats.expensesReport)],
        states = {
            CHOOSING : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                        MessageHandler(Filters.regex('View Expenses By Month'), expensestats.totalByMonth),
                        MessageHandler(Filters.regex('View Expenses By Category'), expensestats.totalByCategory),
                        MessageHandler(Filters.regex('^\d{4}$'), expensestats.selectYearWMonth),
                        MessageHandler(Filters.regex('(?:Jan$|Feb$|Mar$|Apr$|May$|June$|July$|Aug$|Sept$|Oct$|Nov$|Dec$)'), expensestats.selectMonth),
                        CallbackQueryHandler(pattern='/cancel', callback= expensestats.expensesReport),
                        CallbackQueryHandler(pattern='/done', callback= expensestats.viewByMonth),
                        CallbackQueryHandler(pattern='/home', callback= auth.homeInlineButton),
                        CommandHandler('home', auth.home),
                        CommandHandler('cancel', expensestats.expensesReport)],
            TYPING_REPLY : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                            MessageHandler(Filters.regex('^\d{4}$'), expensestats.selectYearWCategory),
                            MessageHandler(Filters.regex('(?:Jan$|Feb$|Mar$|Apr$|May$|June$|July$|Aug$|Sept$|Oct$|Nov$|Dec$)'), expensestats.selectMonth),
                            MessageHandler(Filters.regex('(^Total expenses for )'), expensestats.selectCategory),
                            CommandHandler('edit', budgetlimits.setBudgetLimits),
                            CommandHandler('cancel', expensestats.expensesReport),
                            CommandHandler('home', auth.home)],
        },
        fallbacks=[]
    ))

    # List expenses
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('List Expenses'), expenseslist.expensesList)],
        states={
            CHOOSING : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                        MessageHandler(Filters.regex('List Expenses By Count'), expenseslist.expensesByTail),
                        MessageHandler(Filters.regex('List Expenses By Date'), expenseslist.expensesByDate),
                        MessageHandler(Filters.regex('^\d{4}$'), expenseslist.selectYear),
                        MessageHandler(Filters.regex('^\d{1,2}$'), expenseslist.selectDay),
                        MessageHandler(Filters.regex('(?:Jan$|Feb$|Mar$|Apr$|May$|June$|July$|Aug$|Sept$|Oct$|Nov$|Dec$)'), expenseslist.selectMonth),
                        CallbackQueryHandler(pattern='/cancel', callback= expenseslist.cancelInlineButton),
                        CallbackQueryHandler(pattern='/home', callback= auth.homeInlineButton),
                        CommandHandler('done', expenseslist.displayexpensesByDate),
                        CommandHandler('cancel', expenseslist.expensesList),
                        CommandHandler('home', auth.home)
                        ],
            TYPING_REPLY : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                            MessageHandler(Filters.regex('^[0-9]'), expenseslist.displayexpensesByTail),
                            CallbackQueryHandler(pattern='/cancel', callback= expenseslist.cancelInlineButton),
                            CallbackQueryHandler(pattern='/home', callback= auth.homeInlineButton),
                            ]
        },
        fallbacks=[]
    ))

    # Seach expenses
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Search Expenses'), expensessearch.expensesSearch)],
        states={
            CHOOSING : [MessageHandler(Filters.regex('Main Menu'), auth.home),
                        MessageHandler(Filters.regex('Search Expenses By Expense ID'), expensessearch.expenseByID),
                        MessageHandler(Filters.regex('Search Expenses By Keyphrase'), expensessearch.expensesByKeyphrase),
                        CallbackQueryHandler(pattern='/cancel', callback= expensessearch.cancelInlineButton),
                        CallbackQueryHandler(pattern='/home', callback= auth.homeInlineButton),
                        ],
            TYPING_REPLY : [MessageHandler(Filters.regex('^[a-zA-Z]'), expensessearch.displayexpensesByKeyphrase),
                            MessageHandler(Filters.regex('^[0-9]'), expensessearch.displayexpenseByID),
                            CallbackQueryHandler(pattern='/cancel', callback= expensessearch.cancelInlineButton),
                            CallbackQueryHandler(pattern='/home', callback= auth.homeInlineButton),]
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
