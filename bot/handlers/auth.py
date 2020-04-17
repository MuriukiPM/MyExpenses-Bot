from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup
import pymongo

from bot import reply_markups
from libs import utils
from bot.globals import TYPING_REPLY

# TODO: space out commands to ease tapping on phone
# TODO: handler for fallbacks!
# TODO: Check if user exists on DB, if not, create user using messege fields
def start(update: Update, context: CallbackContext):
	'''
		Flow: Wake the bot
	'''
	try:
		chat = update.message.chat
		chat_ID, first_name, last_name, username = str(update.message.from_user.id), getattr(chat,"first_name"), getattr(chat,"last_name"), getattr(chat,"username")
	except Exception as e:
		utils.logger.error(e)
	# utils.logger.debug('Chat ID : %s', chat_ID)
	utils.logger.debug('first_name: %s', first_name)
	utils.logger.debug('last_name: %s', last_name)
	utils.logger.debug('username: %s', username)
	try:
		# headers = {"Authorization": "Bearer <Token>",
		# 		   "MYEXPENSES-REST-API-KEY": "<key>"}
		# r = requests.get(url=env.get("URL_USERBYCHATID"),
		# 				params={'chat_id':chat_ID}),
		# 				headers=headers)
		r = requests.get(url=env.get("URL_USER_BY_CHATID"),
						params={'chat_id':chat_ID})
		utils.logger.debug('request: %s', r.url)
		response = r.json()
		utils.logger.debug("GET USER: "+repr(response))
		if response['Success'] is True:     # user found 
			utils.logger.debug("User found!")
		else:	# create user
			try:
				r = requests.post(url=env.get("URL_POST_USER"),
								  json={"chatID": chat_ID,
										"firstName": first_name,
										"lastName": last_name,
										"userName": username
										}
								)
				utils.logger.debug('request: %s', r.url)
				response = r.json()
				utils.logger.debug("POST USER: "+repr(response))
				if response['Success'] is True:     # user found 
					utils.logger.debug("User account created!")
				else:
					utils.logger.error("User account create failed")
			except Exception as e:
				text = ("Something went wrong."
						+"\n"
						+"\nNo connection to the server.")   
				utils.logger.error("User signup failed with error: "+str(e))
	except Exception as e:
		text = ("Something went wrong."
				+"\n"
				+"\nNo connection to the server.")   
		utils.logger.error("User query failed with error: "+str(e))
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
	utils.logger.debug("verificationNumber: %s",verificationNumber)
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
		context.user_data['inputYear'] = '' #the typed year vealue
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
	context.user_data['inputYear'] = ''
	#send
	context.bot.send_message(chat_id=chat_ID,
		text="Main Options",
		reply_markup = reply_markups.mainMenuMarkup)
	return ConversationHandler.END

# Error handler
# TODO: update to show more context: calling function etc
def error(update: Update, context: CallbackContext):
	"""Log Errors caused by Updates."""
	utils.logger.error('Update "%s" caused error "%s"', update.message['text'], context.error)

# TODO: Add step to end session/after period of inactivity
# to require verification on next session
# TODO: Add SMS verification