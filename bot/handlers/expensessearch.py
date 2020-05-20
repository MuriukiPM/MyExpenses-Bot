from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from bot import reply_markups
from libs import utils
from bot.globals import TYPING_REPLY, CHOOSING

def cancelInlineButton(update: Update, context: CallbackContext):
    text = ("Select an option from below to proceed.")
    context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                            text = text,
                            reply_markup = reply_markups.expenseSearchMarkup) 
    
    return CHOOSING

# Flow for searching expenses begins here
def expensesSearch(update: Update, context: CallbackContext):
    """
        Initiate the flow for searching expenses
    """
    text = ("Select an option from below to proceed.")
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markups.expenseSearchMarkup) 
    
    return CHOOSING

def expenseByID(update: Update, context: CallbackContext):
    """
        Start the flow to search expenses by expense id in database
    """
    text = ("Please select an option or type in the expense ID for the expense you would like to view.")
    reply_markup = reply_markups.backnHomeInlineMarkup
    context.bot.send_message(chat_id=update.message.chat_id,
					        text = text,
					        reply_markup = reply_markup) 

    return TYPING_REPLY

def displayexpenseByID(update: Update, context: CallbackContext):
    """
        Display the expense matching the provided ID
    """
    chatID = update.message.chat_id
    expID = update.message.text
    try:
        r = requests.get(url=env.get("URL_VIEW_EXPENSE_ID"),
                        params={'chat_id':chatID,'id':expID})
        res_pg = r.json()
        if r.status_code==200:
            text = ("Result: "
					+"\n{}".format(utils.convertJson(res_pg['Data'])))
            reply_markup = ReplyKeyboardRemove() 
            context.bot.send_message(chat_id=update.message.chat_id,
                                    text = text,
					                reply_markup = reply_markup)
            text = ("Please select an option or type in the expense ID for the expense you would like to view.")
        else: text = repr(res_pg['Comment'])
    except Exception as error:
        text = ("Something went wrong.")
        utils.logger.error("Error fetching expense: "+repr(error))
    reply_markup = reply_markups.backnHomeInlineMarkup
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markup)
            
    return TYPING_REPLY

def expensesByKeyphrase(update: Update, context: CallbackContext):
    """
        Start the flow to search expenses by keyphrase in database records
    """
    text = ("Please select an option or type in the search phrase for the expense you would like to view.")
    reply_markup = reply_markups.backnHomeInlineMarkup
    context.bot.send_message(chat_id=update.message.chat_id,
					        text = text,
					        reply_markup = reply_markup) 

    return TYPING_REPLY

# TODO: url encode search phrase
# TODO: Replace link with list
def displayexpensesByKeyphrase(update: Update, context: CallbackContext):
    """
        Display the expense matching the provided search phrase
    """
    chatID = update.message.chat_id
    phrase = update.message.text
    try:
        r = requests.get(url=env.get("URL_VIEW_EXPENSES_TERM"),
                        params={'chat_id':chatID,'q':phrase})
        utils.logger.debug("request: "+r.url)
        if r.status_code==200:
            res = [[InlineKeyboardButton(text="View results in browser", url=r.url)]]
            reply_markup = InlineKeyboardMarkup(res) 
            context.bot.send_message(chat_id=update.message.chat_id,
                                    text = "Success",
					                reply_markup = reply_markup)
            text = ("Please select an option or type in the search phrase for the expense you would like to view.")
        else:
            if r.status_code==404: text = ("Expense matching search phrase = "+phrase+" not found")
            else: text = ("Something went wrong on the server.")
    except Exception as error:
        text = ("Something went wrong.")
        utils.logger.error("Error fetching expenses: "+repr(error))
    reply_markup = reply_markups.backnHomeInlineMarkup
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markup)
            
    return TYPING_REPLY