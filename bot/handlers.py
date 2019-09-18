from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup

from bot import reply_markups
from bot.utils import logger
from bot.globals import *

# TODO: space out commands to ease tapping on phone
# TODO: handler for fallbacks!
# Flow: Wake the bot
def start(bot, update, user_data):
	chat_ID = str(update.message.from_user.id)
	first_name = update.message.chat.first_name
	logger.info('Chat ID : %s', chat_ID)
	text = ("Welcome "+first_name+", I am Icarium"
			+"\n"
			+"\nPlease type your confirmation code for verification")
	#bot.sendChatAction(chat_id=chat_ID, action="typing")
	bot.send_message(chat_id=chat_ID,
					text=text,
					reply_markup = ReplyKeyboardRemove())
	
	return TYPING_REPLY

# verify identity
# TODO: limit number of retries?
def verify(bot, update, user_data):
	verificationNumber = update.message.text
	if verificationNumber == str(update.message.from_user.id):
		# Initialise some variables
		user_data['input'] = {}
		user_data['input']['Timestamp'] = []
		user_data['input']['Description'] = []
		user_data['input']['Proof'] = []
		user_data['input']['Category'] = []
		user_data['input']['Amount'] = []
		user_data['key'] = []
		#TS : NOTSMKP, DESCR : NODESCRMKP ,PRF : NOPRFMKP, CAT : NOCATMKP, AMT : NOAMTMKP 
		user_data['markups'] = dict(zip([key for key, values in user_data['input'].items()],
										reply_markups.expenseFlowMarkups))
		# Do other background stuff

		# Output to user
		update.message.reply_text("Great! Successfully verified. Choose an option from below",
							  reply_markup = reply_markups.mainMenuMarkup)
		return ConversationHandler.END
	else:
		text = ("Wrong code!"
				+"\n"
				+"\nPlease type your confirmation code for verification")
		bot.send_message(chat_id=str(update.message.from_user.id),
						text=text,
						reply_markup = ReplyKeyboardRemove())
		return TYPING_REPLY

# Conversation end
def home(bot, update, user_data):
	chat_ID = str(update.message.from_user.id)
	user_data['key'] = []
	bot.send_message(chat_id=chat_ID,
		text="Main Options",
		reply_markup = reply_markups.mainMenuMarkup)
	return ConversationHandler.END

# Flow: Create new expense 
def new (bot, update, user_data):
	text = ("Select field to fill in from below, once ready, tap Submit."
			+"\nOr tap Abort to return to Main menu")
	bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markups.newExpenseMarkup) 
	return CHOOSING

# Timestamp column: YYYY-MM-DD HH:MM:SS
# TODO: Use /done to navigate back to new()
# TODO: Add options to select time from X <timeframe> ago eg 1 hour, 2 weeks
def timestamp(bot, update, user_data):
	user_data['key'] = "Timestamp"
	text = ("Select the current time below,"
			+"\nor type in the timestamp in the format 'YYYY-MM-DD HH:MM:SS'"
			+"\nor type how long ago the expense occured in the format"
			+"\n'<digit> <timeframe>' for example, 1 hour, 6 days, 10 weeks."
			+"\n"
			+"\nOr  /cancel  to return to choose other options."
			+"\n"
			+"\nOr  /home  to return to Main Menu")
	#time = update.message.date
	utc_datetime = datetime.datetime.utcnow()
	local_datetime = (utc_datetime + datetime.timedelta(hours=UTC_OFFSET)).strftime("%Y-%m-%d %H:%M:%S")
	currentTime = [[KeyboardButton(local_datetime)]]
	currentTimeMarkup = ReplyKeyboardMarkup(currentTime, resize_keyboard=True)
	bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = currentTimeMarkup)
	
	return TYPING_REPLY

# Description column
# TODO: Add feature: set how many months back to look
# TODO: Add bot message just before the query to state how far back we are looking
# TODO: Add a check to see if there is sufficient data depending on number of descr to query
# TODO: For each of the top ten descriptions, attach the most common amount
def description(bot, update, user_data):
	# get the date from 3 months back
	dt0 = (datetime.datetime.utcnow()+ datetime.timedelta(hours=3))
	for _ in range(3):  dt0 = subtract_one_month(dt0)
	date = dt0.strftime("%Y-%m-%d %H:%M:%S")[:10] #only the date, not time
	top_descr = []
	# send a get request to obtain top ten results in a json
	try:
		bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		r = requests.get(env.get("URL_SORTDESC")+date)
		response = r.json() 
		if response['Success'] is not True:     # some error 
			text = ("Failed!"
					+"\nComment: " +response['Comment']
					+"\nError: "+response['Error']+".")
		else:       # no errors
			# append the top ten descriptions to the reply markup list
			for descr in response['Data']:
				top_descr.append([KeyboardButton(descr['Description'])])
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
		logger.info(e)
		reply_markup = ReplyKeyboardRemove()
	user_data['key'] = "Description"
	bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	return TYPING_REPLY

# Category column
def category(bot, update, user_data):
	categories = []
	# get the categories
	try:
		bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		r = requests.get(env.get("URL_CATEGORIES"))
		response = r.json() 
		if response['Success'] is not True:     # some error 
			text = ("Failed!"
					+"\nComment: " +response['Comment']
					+"\nError: "+response['Error']+".")
		else:       # no errors
			# append the top ten descriptions to the reply markup list
			for cateogry in response['Data']:
				categories.append([KeyboardButton(cateogry['Category'])])
			reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
			text = ("Select a category from below or type in the category. Or  /cancel  to return to choose other options."
					+"\nOr  /home  to return to Main Menu")
	except Exception as e:
		text = ("Something went wrong."
				+"\n"
				+"\nNo connection to the db server."
				+"\n"
				+"Type in the category. Or  /cancel  to return to choose other options."
				+"\nOr  /home  to return to Main Menu")   
		logger.info(e)
		reply_markup = ReplyKeyboardRemove()
	user_data['key'] = "Category" #update the check for most recently updated field
	bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	return TYPING_REPLY

# Proof column
def proof(bot, update, user_data):
	user_data['key'] = "Proof"
	text = ("Type in the proof. Or  /cancel  to choose other options."
			+"\nOr  /home  to return to Main Menu")
	bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = ReplyKeyboardRemove())
	return TYPING_REPLY

# Amount column
# TODO: Add keys of most common amounts
def amount(bot, update, user_data):
	user_data['key'] = "Amount"
	text = ("Type in the amount. Or /cancel to return to choose other options."
			+"\nOr /home to return to Main Menu")
	bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = ReplyKeyboardRemove())
	return TYPING_REPLY

# Post values to POST method on API
def post(bot, update, user_data):
	#logger.info(user_data['input'])
	# Check for empty fields. Description, Amount, Category has to be filled always
	if user_data['input']['Amount'] and user_data['input']['Description'] and user_data['input']['Category']:
		# Initiate the POST. If successfull, you will get a primary key value and a Success bool as True
		try:
			bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
			r = requests.post(env.get("URL_EXPENSE"),
							json={	"Timestamp":user_data['input']['Timestamp'],
									"Description":user_data['input']['Description'],
									"Proof":user_data['input']['Proof'],
									"Amount":user_data['input']['Amount'],
									"Category":user_data['input']['Category']
									}
								)
			response = r.json() 
			#logger.info(response)
			if response['Success'] is not True:     # some error 
				text = ("Failed!"
						+"\nComment: " +response['Comment']
						+"\nError: "+response['Error']['Message']+".")
			else:       # no errors
				# empty the fields
				user_data['input']['Timestamp'] = []
				user_data['input']['Description'] = []
				user_data['input']['Proof'] = []
				user_data['input']['Category'] = []
				user_data['input']['Amount'] = []
				text = ("Post Successful! Post id is: "+response['Comment']
						+"\nPlease select an option from below.")
		except Exception as e:
			text = ("Something went wrong."
					+"\n"
					+"\nNo connection to the server.")   
			logger.info("Post failed with error: "+str(e))
	else:	# fields empty or amount empty
		text = ("Please complete filling in the fields.")
	
	bot.send_message(chat_id=update.message.chat_id,
                    text = text,
                    reply_markup = reply_markups.newExpenseMarkup)
	return CHOOSING

# Confirmation of entered value
def verifyValue(bot, update, user_data):
	#grab the reply text 
	data = update.message.text

	# if the timestamp was just set
	if (user_data['key'] == 'Timestamp'):
		try:
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
	#logger.info(data)
	#parse to relevant key
	user_data['input'][user_data['key']] =  data
	text = ("Received '"+data+"' as your "+user_data['key']+" value."
			+"\n"
			+"\nType  /done  to proceed or type in a different value to change the "
			+user_data['key']+" value." 
			+"\nOr  /cancel  to choose other options ")
	markup = ReplyKeyboardRemove()
	if (user_data['key'] == 'Amount'):
		text = ("Received '"+data+"' as your "+user_data['key']+" value."
			+"\nCurrent entries: "
			+"\nTimestamp: "+str(user_data['input']['Timestamp'])
			+"\nDescription: "+str(user_data['input']['Description'])
			+"\nProof: "+str(user_data['input']['Proof'])
			+"\nCategory: "+str(user_data['input']['Category'])
			+"\nAmount: "+str(user_data['input']['Amount'])
			+"\n"
			+"\nType  /submit  to post or type in a different value to change the "
			+user_data['key']+" value." 
			+"\nOr  /cancel  to Choose other entries to change")
	bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup) 
	
	return TYPING_REPLY

# Final value to post
def value(bot, update, user_data):
	markup = user_data['markups'][user_data['key']]		# Choose relevant reply markup
	text = ("Great! Choose next option to populate. Or if done, tap Submit to post." 
			+"\nOr tap Abort to return to Main Menu")
	bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup) 

	return CHOOSING

def error(bot, update, error):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, error)

# How many months back to look.
def subtract_one_month(dt0):
	dt1 = dt0.replace(day=1)
	dt2 = dt1 - datetime.timedelta(days=1)
	return dt2.replace(day=1)