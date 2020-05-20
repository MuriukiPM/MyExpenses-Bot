from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup
import pymongo

from bot import reply_markups
from libs import utils
from bot.globals import *

# Flow for expense input begins here
def newExpense (update: Update, context: CallbackContext):
	"""
		Initiate the expenses input flow
	"""
	text = ("Select a field to fill in from below, once ready, tap Submit.")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markups.newExpenseMarkup) 
	
	return CHOOSING

# Create new expense 
# timestamp column: YYYY-MM-DD HH:MM:SS
# TODO: Use /done to navigate back to new()
# FIXME: deal with incorrect input
def timestamp(update: Update, context: CallbackContext):
	context.user_data['currentExpCat'] = "Timestamp"
	# Find out the local time and date
	utc_datetime = datetime.datetime.utcnow()
	local_datetime = (utc_datetime + datetime.timedelta(hours=UTC_OFFSET)).strftime("%Y-%m-%d %H:%M:%S")
	context.user_data['input'][context.user_data['currentExpCat']] =  local_datetime
	text = ("Using '"+local_datetime+"' as your "+context.user_data['currentExpCat']+" value."
			+"\n"
			+"\nType  /done  to proceed "
			+"\nor type in how long ago the expense occured in the format"
			+"\n'x duration' for example, 1 hour, 6 days, 10 weeks." 
			+"\nOr  /cancel  to choose other options "
			+"\nOr  /home  to return to Main Menu")
	markup = ReplyKeyboardRemove()
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup)
	
	return TYPING_REPLY

# Create new expense 
# description column
# TODO: Add feature: set how many months back to look
# TODO: Add bot message just before the query to state how far back we are looking
# TODO: Add a check to see if there is sufficient data depending on number of descr to query
# TODO: For each of the top ten descriptions, attach the most common amount
def description(update: Update, context: CallbackContext):
	chat_ID = update.message.chat_id
	#get the local time
	dt0 = datetime.datetime.utcnow()+ datetime.timedelta(hours=UTC_OFFSET)
	# get the date from 3 months back from now
	for _ in range(3):  dt0 = utils.subtract_one_month(dt0)
	date = dt0.strftime("%Y-%m-%d %H:%M:%S")[:10] #only the date, not 
	# date = '2019-02-01'
	utils.logger.debug("START DATE: "+date)
	top_descr = []
	# send a get request to obtain top ten results in a json
	try:
		context.bot.sendChatAction(chat_id=chat_ID, action='Typing')
		r = requests.get(env.get("URL_SORTDESC"),
						params={'chat_id':chat_ID,'date':date})		
		response = r.json() 
		if response['Success'] is not True:     # some error 
			text = ("Failed!"
					+"\nComment: " +response['Comment']
					+"\nError: "+response['Error']+".")
		else:       # no errors
			# append the top ten descriptions to the reply markup list
			# for descr in response['Data']:
			# 	top_descr.append([KeyboardButton(descr['Description'])])
			top_descr = [[KeyboardButton(descr['Description'])] for descr in response['Data']]
			reply_markup = ReplyKeyboardMarkup(top_descr, resize_keyboard=True)
			text = ("Select a description from below or type in the description. Or  /cancel  to return to choose other options."
					+"\nOr  /home  to return to Main Menu")
	except Exception as e:
		text = ("Something went wrong."
				+"\n"
				+"\nNo connection to the db server."
				+"\n"
				+"Type in the description. Or  /cancel  to return to choose other options."
				+"\nOr  /home  to return to Main Menu")   
		utils.logger.error("failed to select description with error: "+repr(e))
		reply_markup = ReplyKeyboardRemove()
	context.user_data['currentExpCat'] = "Description"
	context.bot.send_message(chat_id=chat_ID,
					text = text,
					reply_markup = reply_markup)
	return TYPING_REPLY

# Create new expense 
# category column
# TODO: Consider using userdata saved categories
def category(update: Update, context: CallbackContext):
	categories = []
	chat_ID = update.message.chat_id
	# get the categories
	try:
		context.bot.sendChatAction(chat_id=chat_ID, action='Typing')
		r = requests.get(env.get("URL_CATEGORIES"),
						params={'chat_id':chat_ID})
		response = r.json() 
		if response['Success'] is not True:     # some error 
			text = ("Failed!"
					+"\nComment: " +response['Comment']
					+"\nError: "+response['Error']+".")
		else:       # no errors
			# append the categories to the reply markup list
			# for category in response['Data']:
			# 	categories.append([KeyboardButton(category['Category'])])
			categories = [[KeyboardButton(category['Category'])] for category in response['Data']]	
			reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
			text = ("Select a category from below or type in the category. Or  /cancel  to return to choose other options."
					+"\nOr  /home  to return to Main Menu")
	except Exception as e:
		text = ("Something went wrong."
				+"\n"
				+"\nNo connection to the db server."
				+"\n"
				+"Type in the category. Or  /cancel  to choose other options."
				+"\nOr  /home  to return to Main Menu")   
		utils.logger.error("failed to select category with error: "+repr(e))
		reply_markup = ReplyKeyboardRemove()
	context.user_data['currentExpCat'] = "Category" #update the check for most recently updated field
	context.bot.send_message(chat_id=chat_ID,
					text = text,
					reply_markup = reply_markup)
	
	return TYPING_REPLY

# Create new expense 
# proof column
# TODO: Accept image. Call API to upload in multiform
def proof(update: Update, context: CallbackContext):
	context.user_data['currentExpCat'] = "Proof"
	text = ("Type in the proof. Or  /cancel  to choose other options."
			+"\nOr  /home  to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = ReplyKeyboardRemove())
	
	return TYPING_REPLY

# Create new expense 
# Amount column
# TODO: Add keys of most common amounts
def amount(update: Update, context: CallbackContext):
	context.user_data['currentExpCat'] = "Amount"
	text = ("Type in the amount. Or /cancel to return to choose other options."
			+"\nOr /home to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = ReplyKeyboardRemove())
	
	return TYPING_REPLY

# Create new expense 
# confirmation of entered value
def verifyValue(update: Update, context: CallbackContext):
	"""
		Verify various inputs to proceed
	"""
	data = update.message.text #grab the reply text
	# if the timestamp was just set sort the input
	if (context.user_data['currentExpCat'] == 'Timestamp'):
		try: #if datetime object can be obtained from input. expected to raise exception
			datetime.datetime.strptime(data,"%Y-%m-%d %H:%M:%S")
		except ValueError: #time passed given
			s = update.message.text.split() #split on space
			X = int(s[0])
			s = s[1].lower() #the keyword. Lowercase for standardization
			#get current datetime
			dt0 = (datetime.datetime.utcnow()+ datetime.timedelta(hours=3))
			#go back in time. Filter 's' from keywords if present
			if (s.replace('s','') == 'hour'): dt1 = dt0 - datetime.timedelta(seconds=X*3600)
			if (s.replace('s','') == 'day'): dt1 = dt0 - datetime.timedelta(days=X)
			if (s.replace('s','') == 'week'): dt1 = dt0 - datetime.timedelta(days=X*7)
			data = dt1.strftime("%Y-%m-%d %H:%M:%S") #get string format
	#parse to relevant key
	context.user_data['input'][context.user_data['currentExpCat']] =  data
	text = ("Received '"+data+"' as your "+context.user_data['currentExpCat']+" value."
			+"\n"
			+"\nType  /done  to proceed or type in a different value to change the "
			+context.user_data['currentExpCat']+" value." 
			+"\nOr  /cancel  to choose other options ")
	markup = ReplyKeyboardRemove()
	#If amount was just entered, provide summary of values and update 'text' var
	if (context.user_data['currentExpCat'] == 'Amount'):
		text = ("Received '"+data+"' as your "+context.user_data['currentExpCat']+" value."
			+"\nCurrent entries: "
			+"\n{}".format(utils.convertJson(context.user_data['input']))
			+"\n"
			+"\nType  /submit  to post or type in a different value to change the "
			+context.user_data['currentExpCat']+" value." 
			+"\nOr  /cancel  to Choose other entries to change")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup) 
	
	return TYPING_REPLY

# Create new expense 
# display and allow other field selection
def nextExpenseField(update: Update, context: CallbackContext):
	"""
		Display keyboards to select other input categories
	"""
	# Choose relevant reply markup
	markup = context.user_data['markups'][context.user_data['currentExpCat']]		
	text = ("Great! Choose next option to populate." 
			+"\nOr if done, tap Submit to post.")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup) 

	return CHOOSING

# Create new expense 
# post values to provided endpoint to update the db
# TODO: On successful submit, for the relevant budget limit, display value and
# if no threshold set, ask if user wants to set the limits
def postExpense(update: Update, context: CallbackContext):
	chat_ID = update.message.chat_id
	# Check for empty fields. Timestamp, Amount, Category has to be filled always
	required_inputs = ['Amount','Timestamp','Category']
	if all([context.user_data['input'][key] for key in required_inputs]):
	# if all([inputs['Amount'], context.user_data['input']['Timestamp'], context.user_data['input']['Category']):
		# Initiate the POST. If successfull, you will get a primary key value
		# and a Success bool as True
		try:
			context.bot.sendChatAction(chat_id=chat_ID, action='Typing')
			r = requests.post(env.get("URL_POST_EXPENSE"),
							json={	"timestamp":context.user_data['input']['Timestamp'],
									"description":context.user_data['input']['Description'],
									"proof":context.user_data['input']['Proof'],
									"amount":context.user_data['input']['Amount'],
									"category":context.user_data['input']['Category']
								},
							params={'chat_id':chat_ID})
			utils.logger.debug('request: %s', r.url)
			response = r.json() 
			utils.logger.debug("POST response: "+repr(response))
			if response['Success'] is not True:     # some error 
				text = ("Failed!"
						+"\nComment: " +response['Comment']
						+"\nError: "+response['Error']['Message']+".")
			else:       # no errors
				# empty the fields
				context.user_data['input']['Timestamp'] = []
				context.user_data['input']['Description'] = []
				context.user_data['input']['Proof'] = []
				context.user_data['input']['Category'] = []
				context.user_data['input']['Amount'] = []
				text = ("Expense recorded! Expense id is: "+str(response['Data']['id'])
						+"\nPlease select an option from below.")
		except Exception as e:
			text = ("Something went wrong."
					+"\n"
					+"\nNo connection to the server.")   
			utils.logger.error("Post failed with error: "+repr(e))
	else:	# fields empty or amount empty
		text = ("Please complete filling in the fields.")
	
	context.bot.send_message(chat_id=chat_ID,
                    text = text,
                    reply_markup = reply_markups.newExpenseMarkup)
	
	return CHOOSING

# TODO: Add pipeline to accept proof as images and post to API