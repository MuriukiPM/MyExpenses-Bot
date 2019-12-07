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
# Flow: Wake the bot
def start(update: Update, context: CallbackContext):
	chat_ID = str(update.message.from_user.id)
	first_name = update.message.chat.first_name
	utils.logger.debug('Chat ID : %s', chat_ID)
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
	utils.logger.debug(verificationNumber)
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

# Error handler
def error(update: Update, context: CallbackContext):
	"""Log Errors caused by Updates."""
	utils.logger.warning('Update "%s" caused error "%s"', update, context.error)