from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup
import pymongo

from bot import reply_markups
from libs import utils
from bot.globals import *

# TODO: space out commands to ease tapping on phone
# TODO: handler for fallbacks!
# Flow: Wake the bot
def start(update: Update, context: CallbackContext):
	chat_ID = str(update.message.from_user.id)
	first_name = update.message.chat.first_name
	#utils.logger.info('Chat ID : %s', chat_ID)
	text = ("Welcome "+first_name+", I am Icarium"
			+"\n"
			+"\nPlease type your confirmation code for verification")
	context.bot.send_message(chat_id=chat_ID,
					text=text,
					reply_markup = ReplyKeyboardRemove())
	
	return TYPING_REPLY

# verify identity and initialise various stuff
# TODO: limit number of retries?
# TODO: streamline this a bit more
def verify(update: Update, context: CallbackContext):
	mode = env.get("ENV_MODE","")
	if mode=="dev": verificationNumber = env.get("DEV_CHATID","")
	else: verificationNumber = update.message.text
	#utils.logger.info(verificationNumber)
	if verificationNumber == str(update.message.from_user.id):
		# Initialise some variables
		context.user_data['input'] = {}
		context.user_data['input']['Timestamp'] = []
		context.user_data['input']['Description'] = []
		context.user_data['input']['Proof'] = []
		context.user_data['input']['Category'] = []
		context.user_data['input']['Amount'] = []
		context.user_data['limits'] = {}
		context.user_data['allCats'] = []
		context.user_data['currentExpCat'] = [] #the current expenses category
		context.user_data['currentLimitCat'] = [] #the current limit category
		#TS : NOTSMKP, DESCR : NODESCRMKP ,PRF : NOPRFMKP, CAT : NOCATMKP, AMT : NOAMTMKP 
		context.user_data['markups'] = dict(zip([key for key, values in context.user_data['input'].items()],
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
		context.bot.send_message(chat_id=str(update.message.from_user.id),
						text=text,
						reply_markup = ReplyKeyboardRemove())
		return TYPING_REPLY

# Conversation end
def home(update: Update, context: CallbackContext):
	chat_ID = str(update.message.from_user.id)
	# end of conv, so clear some stuff
	context.user_data['currentExpCat'] = []
	context.user_data['limits'] = {}
	#send
	context.bot.send_message(chat_id=chat_ID,
		text="Main Options",
		reply_markup = reply_markups.mainMenuMarkup)
	return ConversationHandler.END

# Flow: Create new expense 
def newExpense (update: Update, context: CallbackContext):
	text = ("Select a field to fill in from below, once ready, tap Submit."
			+"\nOr tap Abort to return to Main menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markups.newExpenseMarkup) 
	return CHOOSING

# Timestamp column: YYYY-MM-DD HH:MM:SS
# TODO: Use /done to navigate back to new()
# FIXME: deal with incorrect input: if not month: use regex on dispatch handler
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

# Description column
# TODO: Add feature: set how many months back to look
# TODO: Add bot message just before the query to state how far back we are looking
# TODO: Add a check to see if there is sufficient data depending on number of descr to query
# TODO: For each of the top ten descriptions, attach the most common amount
def description(update: Update, context: CallbackContext):
	#get the local time
	dt0 = datetime.datetime.utcnow()+ datetime.timedelta(hours=UTC_OFFSET)
	# get the date from 3 months back from now
	for _ in range(3):  dt0 = utils.subtract_one_month(dt0)
	date = dt0.strftime("%Y-%m-%d %H:%M:%S")[:10] #only the date, not time
	top_descr = []
	# send a get request to obtain top ten results in a json
	try:
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		r = requests.get(env.get("URL_SORTDESC")+date)
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
		utils.logger.info(e)
		reply_markup = ReplyKeyboardRemove()
	context.user_data['currentExpCat'] = "Description"
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	return TYPING_REPLY

# Category column
# TODO: Consider using userdata saved categories
def category(update: Update, context: CallbackContext):
	categories = []
	# get the categories
	try:
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		r = requests.get(env.get("URL_CATEGORIES"))
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
		utils.logger.info(e)
		reply_markup = ReplyKeyboardRemove()
	context.user_data['currentExpCat'] = "Category" #update the check for most recently updated field
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
	return TYPING_REPLY

# Proof column
# TODO: Accept image, base64 encode, return string -- <EDIT> (string too long)
def proof(update: Update, context: CallbackContext):
	context.user_data['currentExpCat'] = "Proof"
	text = ("Type in the proof. Or  /cancel  to choose other options."
			+"\nOr  /home  to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = ReplyKeyboardRemove())
	return TYPING_REPLY

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

# Confirmation of entered value
def verifyValue(update: Update, context: CallbackContext):
	"""Verify various inputs to proceed"""
	data = update.message.text #grab the reply text

	# if the timestamp was just set
	if (context.user_data['currentExpCat'] == 'Timestamp'):
		try: #if datetime object can be obtained from input
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
	#If amount was just entered, provide summary of values
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

# Final value to post
def value(update: Update, context: CallbackContext):
	"""Provide user with keyboards to select other input categories"""
	# Choose relevant reply markup
	markup = context.user_data['markups'][context.user_data['currentExpCat']]		
	text = ("Great! Choose next option to populate." 
			+"\nOr if done, tap Submit to post." 
			+"\nOr tap Abort to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup) 

	return CHOOSING

# Post values to provided endpoint to update the db
# TODO: On successful submit, for all limits selected, display value and
# if no threshold set, ask if user wants to set the limits
def postExpense(update: Update, context: CallbackContext):
	# Check for empty fields. Timestamp, Amount, Category has to be filled always
	if context.user_data['input']['Amount'] and context.user_data['input']['Timestamp'] and context.user_data['input']['Category']:
		# Initiate the POST. If successfull, you will get a primary key value
		# and a Success bool as True
		try:
			context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
			r = requests.post(env.get("URL_POST_EXPENSE"),
							json={	"Timestamp":context.user_data['input']['Timestamp'],
									"Description":context.user_data['input']['Description'],
									"Proof":context.user_data['input']['Proof'],
									"Amount":context.user_data['input']['Amount'],
									"Category":context.user_data['input']['Category']
									}
								)
			response = r.json() 
			#utils.logger.info(response)
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
				text = ("Post Successful! Post id is: "+response['Comment']
						+"\nPlease select an option from below.")
		except Exception as e:
			text = ("Something went wrong."
					+"\n"
					+"\nNo connection to the server.")   
			utils.logger.info("Post failed with error: "+str(e))
	else:	# fields empty or amount empty
		text = ("Please complete filling in the fields.")
	
	context.bot.send_message(chat_id=update.message.chat_id,
                    text = text,
                    reply_markup = reply_markups.newExpenseMarkup)
	
	return CHOOSING

# Flow for expense reports begins here
def expensesReport(update: Update, context: CallbackContext):
	"""Initiator for the expenses report flow"""
	text = ("Select an option from below to proceed."
			+"\nOr tap Abort to return to Main menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markups.expensesReportMarkup) 
	
	return CHOOSING

# set limits
def setLimits(update: Update, context: CallbackContext):
	"""Initiate flow to set values for each limit category"""
	#get current categories from pgdb if not already fetched
	if len(context.user_data['limits']) == 0: #not yet fetched
		categories = []
		try:
			context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
			r = requests.get(env.get("URL_CATEGORIES"))
			response = r.json() 
			if response['Success'] is not True:     # some error 
				text = ("Failed!"
						+"\nComment: " +response['Comment']
						+"\nError: "+response['Error']+".")
			else:       # no errors
				# append the categories to the reply markup list and to limit dict
				categories = [[KeyboardButton(category['Category'])] for category in response['Data']]
				context.user_data['limits'] = {category['Category']:"" for category in response['Data']}
				reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
				text = ("Select a category from below."
						+"\nOr  /cancel  to choose other options."
						+"\nOr  /home  to return to Main Menu")
		except Exception as e:
			text = ("Something went wrong."
					+"\n"
					+"\nNo connection to the db server."
					+"\n"
					+"Or  /cancel to choose other options."
					+"\nOr  /home  to return to Main Menu")   
			utils.logger.info(e)
			reply_markup = ReplyKeyboardRemove()
	else:
		categories = [[KeyboardButton(key)] for key in context.user_data['limits'].keys()]
		reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
		text = ("Select a category from below."
				+"\nOr type  /cancel  to choose other options."
				+"\nOr type  /home  to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
	return CHOOSING

# Select the category and request for limit value
def limitKey(update: Update, context: CallbackContext):
	data = update.message.text
	context.user_data['currentLimitCat'] = data
	text = ("Type the limit value for the "+data+" category"
			+"\nOr  /cancel  to choose other categories")
	reply_markup = ReplyKeyboardRemove()
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)

	return TYPING_REPLY

# update the limit value
# TODO: better error message on empty category tracker
def limitValue(update: Update, context: CallbackContext):
	"""Store the input value for the limit category"""
	data = update.message.text #grab the reply text
	#update the limit value
	if context.user_data['currentLimitCat'] == []:
		text = ("You have made an incorrect selection")
		reply_markup = reply_markups.expensesReportMarkup
	else:
		context.user_data['limits'][context.user_data['currentLimitCat']] =  data
		text = ("Received "+data+" as your "+context.user_data['currentLimitCat']+" limit value."
			+"\nChoose the next category to update." 
			"\nOr type  /done  to review." 
			+"\nOr type /home to return to Main Menu")
		categories = [[KeyboardButton(key)] for key in context.user_data['limits'].keys()]
		reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
	return CHOOSING

# Review limits before posting
def reviewLimits(update: Update, context: CallbackContext):
	"""Check all input limits before writing to nosql db"""
	text = ("Limits to post are as follows"
			+"\n"
			+"\n{}".format(utils.convertJson(context.user_data['limits']))
			+"\n"
			+"\nType /submit to post the limits. Or /edit to edit values"
			+"\nType /home to abort and return to main menu")
	reply_markup = ReplyKeyboardRemove()
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)

	return TYPING_REPLY

# Post the limit values to the nosql db: mongo atlas
# TODO: Deal with failed post better
def postLimits(update: Update, context: CallbackContext):
	"""Insert the input limits to nosql db or choose to update if not first time"""
	cacert_path = utils.dev() #if in dev mode use local cert for mongo ssl connection
	try: 
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		client = pymongo.MongoClient(env.get("MONGO_HOST"),
									ssl=True,
									ssl_ca_certs=cacert_path)
		db = client.get_database(env.get("MONGO_DATABASE_NAME"))
		collection = db.get_collection(env.get("MONGO_COLLECTION_NAME"))
		res = collection.find_one({"_id":update.message.chat_id})
		if res is None: #no limit values have been set for the user
			res = collection.insert_one({'_id':update.message.chat_id, 'limits':context.user_data['limits']}).acknowledged
			#if acknowledged
			if res: text = ("Successfully set the limit values." 
						   +"\n"
						   +"\n type  /home  to return to main menu or choose one of the options below") 
			text = ("Failed to set the limit values."
			        +"\n"
					+"\n type  /home  to return to main menu or choose one of the options below") 
			markup = reply_markups.setLimitsMarkup
			context.user_data['limits'] = {} #clear limits
		else: 
			text = ("You have already set limit values. Type  /update  to update the limits"
					+"\nOr tap below to view the limits")
			res = res['limits']
			#pick the non-empty fields
			limitstoUpdate = {key: value for key, value in context.user_data['limits'].items() if value != ""}
			#update the document
			for key in limitstoUpdate.keys(): res[key] = limitstoUpdate[key]
			context.user_data['limits'] = res
			markup = ReplyKeyboardMarkup([[KeyboardButton("View limits")]], resize_keyboard=True)
		client.close()
	except Exception as error:
		text = ("ERROR: "+str(error))
		markup = reply_markups.setLimitsMarkup
		utils.logger.error(error)
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup)

	return CHOOSING

# View values set for limits
def viewLimits(update: Update, context: CallbackContext):
	if env.get("DEV_CACERT_PATH",None) is None:	cacert_path = None
	else: cacert_path = env.get("HOME", "") + env.get("DEV_CACERT_PATH",None)
	#utils.logger.info(cacert_path)
	try:
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		client = pymongo.MongoClient(env.get("MONGO_HOST"),
									ssl=True,
									ssl_ca_certs=cacert_path)
		db = client.get_database(env.get("MONGO_DATABASE_NAME"))
		collection = db.get_collection(env.get("MONGO_COLLECTION_NAME"))
		res = collection.find_one({"_id":update.message.chat_id})
		if res is None: #no limit values have been set for the user
			text = ("Please set limit values")
			reply_markup = reply_markups.expensesReportMarkup
			#do something else
		else:
			text = ("Your values for the limits are :"
					+"\n{}".format(utils.convertJson(res['limits']))
					+"\n"
					+"\nSelect an option from below or type  /home  to return to Main Menu")
			reply_markup = reply_markups.expensesReportMarkup
		client.close()
	except Exception as error:
		text = ("ERROR: "+str(error))
		reply_markup = reply_markups.expensesReportMarkup
		utils.logger.info(error)
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
	return CHOOSING

# Update the limit values with review
# TODO: Complete this!
def updateLimitsWRVW(update: Update, context: CallbackContext):
	"""Input and update limits in nosql db"""
	pass
	return CHOOSING

# Update limits without review
def updateLimitsnoRVW(update: Update, context: CallbackContext):
	"""Update the limits previously set immediately"""
	if env.get("DEV_CACERT_PATH",None) is None:	cacert_path = None
	else: cacert_path = env.get("HOME", "") + env.get("DEV_CACERT_PATH",None)
	#logger.info(cacert_path)
	try: 
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		client = pymongo.MongoClient(env.get("MONGO_HOST"),
									ssl=True,
									ssl_ca_certs=cacert_path)
		db = client.get_database(env.get("MONGO_DATABASE_NAME"))
		collection = db.get_collection(env.get("MONGO_COLLECTION_NAME"))
		res = collection.find_one_and_update({"_id":update.message.chat_id}, 
											{'$set':{"limits":context.user_data['limits']}},
			 								return_document=pymongo.ReturnDocument.AFTER,)
		text = ("Success")
		context.user_data['limits'] = {} #clear limits
		if res is None: text = ("failed!")
		markup = reply_markups.expensesReportMarkup
		client.close()
	except Exception as error:
		text = ("ERROR: "+str(error))
		markup = reply_markups.setLimitsMarkup
		utils.logger.error(error)
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup)

	return CHOOSING

# View total expenses for the current month
# TODO: Provide better status messages when fetching data from servers
# FIXME: deal with incorrect input: if not month: use regex on dispatch handler
def totalByMonth(update: Update, context: CallbackContext):
	"""Flow to view current expenses for this month"""
	month_map = {'01':'Jan','02':'Feb','03':'Mar','04':'April','05':'May','06':'June','07':'July','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
	#get the local time
	dt0 = datetime.datetime.utcnow()+ datetime.timedelta(hours=UTC_OFFSET)
	date = dt0.strftime("%Y-%m-%d %H:%M:%S")[:7] #only current the year and month
	if env.get("DEV_CACERT_PATH",None) is None:	cacert_path = None
	else: cacert_path = env.get("HOME", "") + env.get("DEV_CACERT_PATH",None)
	#logger.info(cacert_path)
	#try fetching expenses from pg
	try:
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		r = requests.get(url=env.get('URL_VIEW_EXPENSE')+date)
		res_pg = r.json()
		if res_pg['Data'] is not None and res_pg['Success'] is not True:     # some error 
			text = ("Failed!"
					+"\nComment: " +res_pg['Comment']
					+"\nError: "+str(res_pg['Error'])+".")
			markup = reply_markups.expensesReportMarkup
		if res_pg['Data'] is None: #no expenses for current month
			text = ("You have not entered any expenses for "+month_map[date[5:7]]+" - "+date[:4]
					+"\nPlease type in full the month for which you'd like to view expenses for eg May, December"
					+"\nOr type  /cancel  to abort.")
			markup = ReplyKeyboardRemove()
			context.bot.send_message(chat_id=update.message.chat_id,
									text = text,
									reply_markup = markup)

			return TYPING_REPLY
		else:       # no errors
			#get the sum
			sum_exp = 0
			for exp in res_pg['Data']: sum_exp += exp['Metric']
			#try fetching expenses limits from mongo
			try: 
				context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
				client = pymongo.MongoClient(env.get("MONGO_HOST"),
											ssl=True,
											ssl_ca_certs=cacert_path)
				db = client.get_database(env.get("MONGO_DATABASE_NAME"))
				collection = db.get_collection(env.get("MONGO_COLLECTION_NAME"))
				res_mg = collection.find_one({"_id":update.message.chat_id})
				if res_mg is None: #no limit values have been set for the user
					text = ("Expenses by Category for "+month_map[date[5:7]]+" - "+date[:4]
							+"\n"
							+"\n{}".format(utils.convertList(res_pg['Data']))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nTo view the expenses in comparison to limits, please type" 
							+"  /edit  to input limits"
							+"\nOr type in full the month for which you'd like to view expenses for eg May, December"
							+"\nOr type  /home  to finish")
					markup = ReplyKeyboardRemove()
					context.bot.send_message(chat_id=update.message.chat_id,
									text = text,
									reply_markup = markup)

					return TYPING_REPLY
				else:
					#pick the non-empty fields
					res_mg_ = {key: value for key, value in res_mg['limits'].items() if value != ""}
					#create the reply
					text = ("Expenses by Category for "+month_map[date[5:7]]+" - "+date[:4]
							+"\n"
							+"\n{}".format(utils.convertExp_Lim(res_pg['Data'], res_mg_))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nType  /home  to return to main menu"
							+"\nOr type in full the month for which you'd like to view expenses for eg May, December")
					markup = ReplyKeyboardRemove()
					context.bot.send_message(chat_id=update.message.chat_id,
									text = text,
									reply_markup = markup)

					return TYPING_REPLY
			except Exception as error:
				text = ("ERROR: "+str(error))
				markup = reply_markups.expensesReportMarkup
				utils.logger.error(error)
	except Exception as error:
		text = ("Something went wrong."
				+"\n"
				+"\nNo connection to the db server."
				+"\n"
				+"Type in the category. Or  /cancel  to choose other options."
				+"\nOr  /home  to return to Main Menu")   
		markup = reply_markups.expensesReportMarkup
		utils.logger.error(error)
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup)

	return CHOOSING

# Confirm the month and display
# TODO: add provision for changing the year
# FIXME: deal with incorrect input: if not month: use regex on dispatch handler
def selectMonth(update: Update, context: CallbackContext):
	"""Flow to fetch various data and display"""
	month = (update.message.text).lower()
	#get the local time
	dt0 = datetime.datetime.utcnow()+ datetime.timedelta(hours=UTC_OFFSET)
	date = dt0.strftime("%Y-%m-%d %H:%M:%S")[:7] #only current the year and month
	month_map = {'january':'01','february':'02','march':'03','april':'04','may':'05','june':'06','july':'07','august':'08','september':'09','october':'10','november':'11','december':'12'}
	cacert_path = utils.dev() #if in dev mode use local cert for mongo ssl connection
	#utils.logger.info(cacert_path)
	#try fetching expenses from pg
	try:
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		r = requests.get(url=env.get('URL_VIEW_EXPENSE')+date[:5]+month_map[month])
		res_pg = r.json()
		if res_pg['Data'] is not None and res_pg['Success'] is not True:     
			text = ("Failed!"
					+"\nComment: " +res_pg['Comment']
					+"\nError: "+str(res_pg['Error'])+".")
			markup = reply_markups.expensesReportMarkup
		if res_pg['Data'] is None:
			text = ("You have not entered any expenses for "+month+" - "+date[:4]
					+"\nPlease type in full the month for which you'd like to view expenses for eg May, December"
					+"\nOr type  /cancel  to abort.")
		else:       # no errors
			#get the sum
			sum_exp = 0
			for exp in res_pg['Data']: sum_exp += exp['Metric']
			#try fetching data from mongo
			try: 
				context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
				client = pymongo.MongoClient(env.get("MONGO_HOST"),
											ssl=True,
											ssl_ca_certs=cacert_path)
				db = client.get_database(env.get("MONGO_DATABASE_NAME"))
				collection = db.get_collection(env.get("MONGO_COLLECTION_NAME"))
				res_mg = collection.find_one({"_id":update.message.chat_id})
				if res_mg is None: #no limit values have been set for the user.
					text = ("Expenses by Category for "+month+" - "+date[:4]
							+"\n"
							+"\n{}".format(utils.convertList(res_pg['Data']))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nTo view the expenses in comparison to limits, please type"
							+"  /edit  to input limits"
							+"\nOr type in full the month for which you'd like to view expenses for eg May, December"
							+"\nOr type  /home  to finish")
				else:
					#pick the non-empty fields
					res_mg_ = {key: value for key, value in res_mg['limits'].items() if value != ""}
					#create the reply
					text = ("Expenses by Category for "+month+" - "+date[:4]
							+"\n"
							+"\n{}".format(utils.convertExp_Lim(res_pg['Data'], res_mg_))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nType  /home  to return to main menu"
							+"\nOr type in full the month for which you'd like to view expenses")
			except Exception as error:
				text = ("ERROR: "+str(error))
				markup = reply_markups.expensesReportMarkup
				utils.logger.error(error)
	except Exception as error:
		text = ("Something went wrong."
				+"\n"
				+"\nNo connection to the db server."
				+"\n"
				+"Type in the category. Or  /cancel  to choose other options."
				+"\nOr  /home  to return to Main Menu")   
		markup = reply_markups.expensesReportMarkup
		utils.logger.error(error)

	markup = ReplyKeyboardRemove()
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup)

	return TYPING_REPLY

# View total expenses for the current year for a selected category
# TODO: add provision for changing the year
def totalByCat(update: Update, context: CallbackContext):
	#get current categories from pgdb if not already fetched
	if len(context.user_data['allCats']) == 0: #not yet fetched
		categories = []
		try:
			context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
			r = requests.get(env.get("URL_CATEGORIES"))
			response = r.json() 
			if response['Success'] is not True:     # some error 
				text = ("Failed!"
						+"\nComment: " +response['Comment']
						+"\nError: "+response['Error']+".")
			else:       # no errors
				# append the categories to the reply markup list and to limit dict
				categories = [[KeyboardButton(category['Category'])] for category in response['Data']]
				context.user_data['allCats'] = [category['Category'] for category in response['Data']]
				reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
				text = ("Select a category from below."
						+"\nOr  /cancel  to choose other options."
						+"\nOr  /home  to return to Main Menu")
		except Exception as e:
			text = ("Something went wrong."
					+"\n"
					+"\nNo connection to the db server."
					+"\n"
					+"Or  /cancel to choose other options."
					+"\nOr  /home  to return to Main Menu")   
			utils.logger.info(e)
			reply_markup = ReplyKeyboardRemove()
	else:
		categories = [[KeyboardButton(cat)] for cat in context.user_data['allCats']]
		reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
		text = ("Select a category from below."
				+"\nOr type  /cancel  to choose other options."
				+"\nOr type  /home  to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
	return CHOOSING

def selectCat(update: Update, context: CallbackContext):
	# cat = update.message.text
	conn, error = utils.connect()
	if error is None:
		rows, error = utils.getsqlrows(conn=conn)
		if error is None:
			MonthnCat = utils.gettotals(sqlrows=rows)
			utils.logger.info((MonthnCat.loc['Housing', 2019].values))
		else: utils.logger.info(error)
	else: utils.logger.info(error)

	return

def error(update: Update, context: CallbackContext):
	"""Log Errors caused by Updates."""
	utils.logger.warning('Update "%s" caused error "%s"', update, context.error)
