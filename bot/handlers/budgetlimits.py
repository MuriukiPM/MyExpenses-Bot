from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup
import pymongo

from bot import reply_markups
from libs import utils
from bot.globals import TYPING_REPLY, CHOOSING 

# Flow for budget begins here
# TODO: Ask for monthly budgetary limits per category
# TODO: Temporarily store results from mongo, pg queries in memory to speed up?
def budget(update: Update, context: CallbackContext):
	"""Initiator for the budget flow"""
	context.user_data['inputYear'] = ''
	text = ("Select an option from below to proceed.")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markups.budgetLimitsMarkup) 
	
	return CHOOSING

# Set limits
# select the category
# TODO: Add check for whether all limits have been set and transition to update?
def setBudgetLimits(update: Update, context: CallbackContext):
	"""
		Initiate flow to set values for each limit category
	"""
	chat_ID = update.message.chat_id
	#get current categories from pgdb if not already fetched
	if len(context.user_data['limits']) == 0: #not yet fetched
		categories = []
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
				# append the categories to the reply markup list and to limit dict
				categories = [[KeyboardButton('Set budget limit for '+category['Category'])] for category in response['Data']]
				context.user_data['limits'] = {category['Category']:"" for category in response['Data']}
				reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
				text = ("Select a category from below."
						+"\nOr  /cancel  to choose other options."
						+"\nOr  /home  to return to Main Menu")
		except Exception as e:
			text = ("Something went wrong."
					+"\n"
					+"\nNo connection to the db server.")   
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Main Menu')]], resize_keyboard=True) 
			utils.logger.error(e)
	else:
		categories = [[KeyboardButton('Set budget limit for '+key)] for key in context.user_data['limits'].keys()]
		reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
		text = ("Select a category from below."
				+"\nOr type  /cancel  to choose other options."
				+"\nOr type  /home  to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
	return TYPING_REPLY

# Set limits
# confirm the category and request for limit value
def limitKey(update: Update, context: CallbackContext):
	data = update.message.text.split('Set budget limit for ')[1]
	context.user_data['currentLimitCat'] = data
	text = ("Type the budget limit for the "+data+" category"
			+"\nOr  /cancel  to choose other categories")
	reply_markup = ReplyKeyboardRemove()
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)

	return TYPING_REPLY

# Set limits
# confirm limit value
# TODO: better error message on empty category tracker
def limitValue(update: Update, context: CallbackContext):
	"""Store the input value for the limit category"""
	data = update.message.text #grab the reply text
	#update the limit value
	if context.user_data['currentLimitCat'] == []:
		text = ("You have made an incorrect selection")
		reply_markup = reply_markups.budgetLimitsMarkup
		context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
		return CHOOSING
	else:
		context.user_data['limits'][context.user_data['currentLimitCat']] =  data
		text = ("Received "+data+" as your "+context.user_data['currentLimitCat']+" budget limit."
				+"\nChoose the next category to update." 
				+"\nOr select 'Review Budget Limits & Submit' below." 
				+"\nOr type /home to return to Main Menu")
		categories = [[KeyboardButton("Set budget limit for "+key)] for key in context.user_data['limits'].keys()]
		keyboard = [[KeyboardButton("Review Budget Limits & Submit")]] + categories
		utils.logger.debug(keyboard)
		reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
		context.bot.send_message(chat_id=update.message.chat_id,
						text = text,
						reply_markup = reply_markup)
		
		return TYPING_REPLY

# Set limits
# review limits before posting
def reviewBudgetLimits(update: Update, context: CallbackContext):
	"""Check all input limits before writing to nosql db"""
	text = ("Budget limits to post are as follows"
			+"\n"
			+"\n{}".format(utils.convertJson(context.user_data['limits']))
			+"\n"
			+"\nType /submit to post the budget limits. Or /edit to edit values"
			+"\nType /home to abort and return to main menu")
	reply_markup = ReplyKeyboardRemove()
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)

	return TYPING_REPLY

# Set limits
# post the limit values to the nosql db: mongo atlas
# TODO: Deal with failed post better
def postBudgetLimits(update: Update, context: CallbackContext):
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
			if res: text = ("Successfully set the budget limit." 
						   +"\n"
						   +"\n type  /home  to return to main menu or choose one of the options below") 
			text = ("Failed to set the budget limit."
			        +"\n"
					+"\n type  /home  to return to main menu or choose one of the options below") 
			markup = reply_markups.setLimitsMarkup
			context.user_data['limits'] = {} #clear limits
		else: 
			text = ("You have already set budget limits. To update only the values you've set above, type  /update  "
					+"\nOr tap below to view the budget limits")
			res = res['limits']
			#pick the non-empty fields
			limitstoUpdate = {key: value for key, value in context.user_data['limits'].items() if value != ""}
			#update the document
			for key in limitstoUpdate.keys(): res[key] = limitstoUpdate[key]
			context.user_data['limits'] = res
			markup = ReplyKeyboardMarkup([[KeyboardButton("View Budget Limits")]], resize_keyboard=True)
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
# TODO: Show total amount of the all budget limits 
def viewBudgetLimits(update: Update, context: CallbackContext):
	cacert_path = utils.dev()
	try:
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		client = pymongo.MongoClient(env.get("MONGO_HOST"),
									ssl=True,
									ssl_ca_certs=cacert_path)
		db = client.get_database(env.get("MONGO_DATABASE_NAME"))
		collection = db.get_collection(env.get("MONGO_COLLECTION_NAME"))
		res = collection.find_one({"_id":update.message.chat_id})
		if res is None: #no limit values have been set for the user
			text = ("Please set budget limits")
			reply_markup = reply_markups.budgetLimitsMarkup
			#do something else
		else:
			text = ("Your budget limits are :"
					+"\n{}".format(utils.convertJson(res['limits'])))
			reply_markup = reply_markups.budgetLimitsMarkup
		client.close()
	except Exception as error:
		text = ("ERROR: "+str(error))
		reply_markup = reply_markups.budgetLimitsMarkup
		utils.logger.error(error)
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
	cacert_path = utils.dev()
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
		markup = reply_markups.budgetLimitsMarkup
		client.close()
	except Exception as error:
		text = ("ERROR: "+str(error))
		markup = reply_markups.setLimitsMarkup
		utils.logger.error(error)
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup)

	return CHOOSING