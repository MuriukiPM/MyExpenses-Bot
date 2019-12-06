##!/usr/bin/env python3
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
        entry_points=[CommandHandler('start', handlers.start)],
        states={
            TYPING_REPLY: [MessageHandler(Filters.text, handlers.verify)],                       
                },
        fallbacks=[]
        ))

    # Enter new expense
    # TODO: add a "sorry, that's not a valid choice" fallback
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('New Expense'), handlers.newExpense)],
        states = {
            CHOOSING : [MessageHandler(Filters.regex('Timestamp'), handlers.timestamp),
                        MessageHandler(Filters.regex('Description'), handlers.description),
                        MessageHandler(Filters.regex('Category'), handlers.category),
                        MessageHandler(Filters.regex('Proof'), handlers.proof),
                        MessageHandler(Filters.regex('Amount'), handlers.amount),
                        MessageHandler(Filters.regex('Submit'), handlers.postExpense),
                        MessageHandler(Filters.regex('Abort'), handlers.home)],
            TYPING_REPLY: [ MessageHandler(Filters.text, handlers.verifyValue),
                            CommandHandler('home', handlers.home),
                            CommandHandler('cancel', handlers.newExpense),
                            CommandHandler('done', handlers.nextExpenseField),
                            CommandHandler('submit', handlers.postExpense)],
            },
        fallbacks=[]
        ))
    
    # Set limits for categories of expenses
    # TODO: add a "sorry, that's not a valid choice" fallback
    # TODO: separate Limits, expenses. limits->view,update,set | expenses->by month, by category
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Expenses Report'), handlers.expensesReport)],
        states = {
            CHOOSING : [MessageHandler(Filters.regex('Abort'), handlers.home),
                        MessageHandler(Filters.regex('Set Limits'), handlers.setLimits),
                        MessageHandler(Filters.regex('Update Limits'), handlers.updateLimitsWRVW),
                        MessageHandler(Filters.regex('View Limits'), handlers.viewLimits),
                        MessageHandler(Filters.regex('View Expenses By Month'), handlers.totalByMonth),
                        MessageHandler(Filters.regex('View Expenses By Category'), handlers.totalByCategory),
                        CommandHandler('update', handlers.updateLimitsnoRVW),
                        CommandHandler('home', handlers.home),
                        CommandHandler('cancel', handlers.expensesReport),
                        # MessageHandler(Filters.text, handlers.limitKey),
                        CommandHandler('done', handlers.reviewLimits)],
            TYPING_REPLY : [MessageHandler(Filters.regex('(^Set limit for )'), handlers.limitKey),
                            MessageHandler(Filters.regex('^[0-9]'), handlers.limitValue),
                            # MessageHandler(Filters.regex('^[a-zA-Z]'), handlers.selectMonth),
                            MessageHandler(Filters.regex('(?:Jan$|Feb$|Mar$|Apr$|May$|June$|July$|Aug$|Sept$|Oct$|Nov$|Dec$)'), handlers.selectMonth),
                            MessageHandler(Filters.regex('(^Total expenses for )'), handlers.selectCategory),
                            CommandHandler('submit', handlers.postLimits),
                            CommandHandler('edit', handlers.setLimits),
                            CommandHandler('cancel', handlers.expensesReport),
                            CommandHandler('home', handlers.home)],
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
