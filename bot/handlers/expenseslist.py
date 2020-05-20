from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from bot import reply_markups
from libs import utils
from bot.globals import *

def cancelInlineButton(update: Update, context: CallbackContext):
    context.user_data['inputYear'] = ''
    context.user_data['inputMonth'] = ''
    context.user_data['inputDay'] = ''
    text = ("Select an option from below to proceed.")
    context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                            text = text,
                            reply_markup = reply_markups.expenseListMarkup) 
    
    return CHOOSING

# Flow for listing expenses begins here
def expensesList(update: Update, context: CallbackContext):
    """
        Initiate the flow for listing expenses
    """
    context.user_data['inputYear'] = ''
    context.user_data['inputMonth'] = ''
    context.user_data['inputDay'] = ''
    text = ("Select an option from below to proceed.")
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markups.expenseListMarkup) 
    
    return CHOOSING

# List previous expenses by count
def expensesByTail(update: Update, context: CallbackContext):
    """
        Start the flow for listing the previous N expenses
    """
    text = ("Please select an option or type in the number of most recently recorded expenses to show.")
    reply_markup = reply_markups.backnHomeInlineMarkup
    context.bot.send_message(chat_id=update.message.chat_id,
					        text = text,
					        reply_markup = reply_markup) 

    return TYPING_REPLY

# TODO: Replace link with list
def displayexpensesByTail(update: Update, context: CallbackContext):
    """
        Display the previous expenses given the number
    """
    chatID = update.message.chat_id
    num = update.message.text
    try:
        r = requests.get(url=env.get("URL_LIST_EXPENSES_TAIL"),
                        params={'chat_id':chatID,'num':num})
        # res_pg = r.json()
        # utils.logger.debug("request: "+r.url) 
        if r.status_code==200:
            # text = r.url
            res = [[InlineKeyboardButton(text="View results in browser", url=r.url)]]
            reply_markup = InlineKeyboardMarkup(res) 
            context.bot.send_message(chat_id=update.message.chat_id,
					                # text = """<a href=\"%s\">%s</a>""" %(text,text),
                                    text = "Success",
                                    # parse_mode = "HTML",
                                    # disable_web_page_preview=False,
					                reply_markup = reply_markup)
            text = ("Please select an option or type in the number of most recently recorded expenses to show.")
        else:
            if r.status_code==404:
                text = ("You have not entered any expenses")
            else:
                text = ("Something went wrong on the server.")
    except Exception as error:
        text = ("Something went wrong.")
        utils.logger.error("Error fetching expenses: "+repr(error))
    reply_markup = reply_markups.backnHomeInlineMarkup
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markup)
            
    return TYPING_REPLY
    
# List all expenses for a given date
def expensesByDate(update: Update, context: CallbackContext):
    """
        Start the flow for listing expenses for the given date
    """
    utc_datetime = datetime.datetime.utcnow()
    local_datetime = (utc_datetime + datetime.timedelta(hours=UTC_OFFSET))
    year = str(local_datetime.year)
    context.user_data['inputYear'] = year
    text = ("Using '"+year+"' as the selected year"
			+"\n"
            +"\nSelect from below the month for which you'd like to list expenses for"
            +"\nOr:"
            +"\n1. type in the year in full for which to list expenses"
            +"\n2. choose any of these commands:"
			+"\n/done   : view results"
            +"\n"
			+"\n/cancel : choose other options "
            +"\n"
			+"\n/home   : return to Main Menu")
    commands = [[KeyboardButton("/done"), KeyboardButton("/cancel"), KeyboardButton("/home")]]
    reply_markup = ReplyKeyboardMarkup(commands + reply_markups.months, resize_keyboard=True,
                                        one_time_keyboard=True)
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markup)

    return CHOOSING

def selectYear(update: Update, context: CallbackContext):
    """
        Select the yaer for which to list expenses
    """
    year = update.message.text
    context.user_data['inputYear'] = year
    text = ("Received '"+year+"' as the selected year"
			+"\nSelect from below the month for which you'd like to list expenses for"
			+"\nOr:"
            +"\n1. retype the year in full for which to list expenses"
            +"\n2. choose any of these commands:"
            +"\n/done   : view results"
            +"\n"
			+"\n/cancel : abort and choose other options "
            +"\n"
			+"\n/home   : return to Main Menu")
    commands = [[KeyboardButton("/done"), KeyboardButton("/cancel"), KeyboardButton("/home")]]
    reply_markup = ReplyKeyboardMarkup(commands + reply_markups.months, resize_keyboard=True,
                                        one_time_keyboard=True)
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markup)

    return CHOOSING

def selectMonth(update: Update, context: CallbackContext):
    """
        Select the month for which to list expenses
    """
    month = update.message.text
    month_map = {
		'jan':'01',
		'feb':'02',
		'mar':'03',
		'apr':'04',
		'may':'05',
		'june':'06',
		'july':'07',
		'aug':'08',
		'sept':'09',
		'oct':'10',
		'nov':'11',
		'dec':'12'}
    context.user_data['inputMonth'] = '-'+month_map[month.lower()]
    text = ("Received '"+month+"' as the selected month"
            +"\nPlease type in the day in digits for which to view expenses"
			+"\nOr:"
            +"\n1. reselect from below the month for which you'd like to view expenses for"
			+"\n2. retype the year in full for which to view expenses"
			+"\n3. choose any of the following commands:"
            +"\n/done   : view results"
            +"\n"
			+"\n/cancel : abort and choose other options "
            +"\n"
			+"\n/home   : return to Main Menu")
    commands = [[KeyboardButton("/done"), KeyboardButton("/cancel"), KeyboardButton("/home")]]
    reply_markup = ReplyKeyboardMarkup(commands + reply_markups.months, resize_keyboard=True,
                                        one_time_keyboard=True)
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markup)

    
    return CHOOSING

def selectDay(update: Update, context: CallbackContext):
    """
        Select the day for which to list expenses
    """
    day = update.message.text
    context.user_data['inputDay'] = '-0'+day if len(day)==1 else '-'+day
    text = ("Received '"+day+"' as the selected day"
            +"\nPlease choose any of these commands:"
            +"\n/done   : view results"
            +"\n"
			+"\n/cancel : abort and choose other options "
            +"\n"
			+"\n/home   : return to Main Menu"
			+"\nOr:"
            +"\n1. reselect from below the month for which you'd like to view expenses for"
			+"\n2. retype the year in full for which to view expenses"
            +"\n3. retype the day in digits for which to view expenses")
    commands = [[KeyboardButton("/done"), KeyboardButton("/cancel"), KeyboardButton("/home")]]
    reply_markup = ReplyKeyboardMarkup(commands + reply_markups.months, resize_keyboard=True,
                                        one_time_keyboard=True)
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markup)
    
    return CHOOSING

#  TODO: validate 
# TODO: Replace link with list: use markdown formatting?
def displayexpensesByDate(update: Update, context: CallbackContext):
    """
        Display the previous expenses given the date
    """
    chatID = update.message.chat_id
    date = context.user_data['inputYear']+context.user_data['inputMonth']+context.user_data['inputDay']
    context.user_data['inputDay'] = ''
    # utils.logger.debug("DATE: "+date)
    try:
        r = requests.get(url=env.get("URL_LIST_EXPENSES_DATE"),
                        params={'chat_id':chatID,'date':date})
        # res_pg = r.json()
        # utils.logger.debug("request: "+str(r.status_code))
        if r.status_code==200:
            # text = r.url
            res = [[InlineKeyboardButton(text="View results in browser", url=r.url)]]
            reply_markup = InlineKeyboardMarkup(res) 
            context.bot.send_message(chat_id=update.message.chat_id,
                                    text = "Success",
					                reply_markup = reply_markup)
            text = ("Please: "
                    +"\n1. reselect from below the month for which you'd like to view expenses for"
			        +"\n2. retype the year in full for which to view expenses"
                    +"\n3. retype the day in digits for which to view expenses"
                    +"\nOr select:"
                    +"\n/cancel  : return to choose other options."
                    +"\n"
                    +"\n/home  : return to Main Menu")
        else:
            if r.status_code==404:
                text = ("You have not entered any expenses for "+date
                        +"\nPlease: "
                        +"\n1. reselect from below the month for which you'd like to view expenses for"
			            +"\n2. retype the year in full for which to view expenses"
                        +"\n3. retype the day in digits for which to view expenses"
                        +"\nOr select:"
                        +"\n/cancel  : choose other options."
                        +"\n"
                        +"\n/home  : return to Main Menu") 
            else:
                text = ("Something went wrong on server."
                        +"\n"
                        +"\n/cancel  : choose other options."
                        +"\n"
                        +"\n/home  : return to Main Menu")
        commands = [[KeyboardButton("/cancel"), KeyboardButton("/home")]]
        reply_markup = ReplyKeyboardMarkup(commands + reply_markups.months, resize_keyboard=True, 
                                            one_time_keyboard=True)
    except Exception as error:
        text = ("Something went wrong.")
        utils.logger.error("Error fetching expenses: "+repr(error))
        reply_markup = reply_markups.backnHomeInlineMarkup
    context.bot.send_message(chat_id=update.message.chat_id,
                            text = text,
                            reply_markup = reply_markup)
            
    return CHOOSING

