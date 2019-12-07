from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup
import pymongo

from bot import reply_markups
from libs import utils
from bot.globals import TYPING_REPLY, CHOOSING 

# Set limits
# select the category
# TODO: Add check for whether all limits have been set and transition to update?
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
				categories = [[KeyboardButton('Set limit for '+category['Category'])] for category in response['Data']]
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
			utils.logger.error(e)
			reply_markup = ReplyKeyboardRemove()
	else:
		categories = [[KeyboardButton('Set limit for '+key)] for key in context.user_data['limits'].keys()]
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
	data = update.message.text.split('Set limit for ')[1]
	context.user_data['currentLimitCat'] = data
	text = ("Type the limit value for the "+data+" category"
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
		reply_markup = reply_markups.expensesReportMarkup
		context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
		return CHOOSING
	else:
		context.user_data['limits'][context.user_data['currentLimitCat']] =  data
		text = ("Received "+data+" as your "+context.user_data['currentLimitCat']+" limit value."
				+"\nChoose the next category to update." 
				+"\nOr type  /done  to review." 
				+"\nOr type /home to return to Main Menu")
		categories = [[KeyboardButton("Set limit for "+key)] for key in context.user_data['limits'].keys()]
		reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
		context.bot.send_message(chat_id=update.message.chat_id,
						text = text,
						reply_markup = reply_markup)
		
		return TYPING_REPLY


# Set limits
# review limits before posting
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

# Set limits
# post the limit values to the nosql db: mongo atlas
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
			text = ("You have already set limit values. To update only the values you've set above, type  /update  "
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