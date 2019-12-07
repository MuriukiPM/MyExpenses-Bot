from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup
import pymongo

from bot import reply_markups
from libs import utils
from bot.globals import *

# Flow for expense reports begins here
def expensesReport(update: Update, context: CallbackContext):
	"""Initiator for the expenses report flow"""
	text = ("Select an option from below to proceed."
			+"\nOr tap Abort to return to Main menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markups.expensesReportMarkup) 
	
	return CHOOSING

# View total expenses for the current month
# select month
# TODO: Provide better status messages when fetching data from servers
# FIXME: deal with incorrect input: if not month: use regex on dispatch handler
def totalByMonth(update: Update, context: CallbackContext):
	"""Flow to view current expenses for this month"""
	month_map = {'01':'Jan','02':'Feb','03':'Mar','04':'April','05':'May','06':'June','07':'July','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
	#get the local time
	dt0 = datetime.datetime.utcnow()+ datetime.timedelta(hours=UTC_OFFSET)
	date = dt0.strftime("%Y-%m-%d %H:%M:%S")[:7] #only current the year and month
	cacert_path = utils.dev()
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
					+"\nPlease select from below the month for which you'd like to view expenses for"
					+"\nOr type  /cancel  to abort.")
			markup = reply_markups.monthsMarkup
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
							+"\nOr select from below the month for which you'd like to view expenses for"
							+"\nOr type  /home  to finish")
					markup = reply_markups.monthsMarkup
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
							+"\nOr type  /edit  to modify the set limits."
							+"\nOr select from below the month for which you'd like to view expenses for")
					markup = reply_markups.monthsMarkup
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

# View total expenses for the current month
# confirm the month and display
# TODO: add provision for changing the year
# FIXME: deal with incorrect input: if not month: use regex on dispatch handler
def selectMonth(update: Update, context: CallbackContext):
	"""Flow to fetch various expense totals for the month and display"""
	month = (update.message.text).lower()
	#get the local time
	dt0 = datetime.datetime.utcnow()+ datetime.timedelta(hours=UTC_OFFSET)
	date = dt0.strftime("%Y-%m-%d %H:%M:%S")[:7] #only current the year and month
	month_map = {'jan':'01','feb':'02','mar':'03','apr':'04','may':'05','june':'06','july':'07','aug':'08','sept':'09','oct':'10','nov':'11','dec':'12'}
	cacert_path = utils.dev() #if in dev mode use local cert for mongo ssl connection
	#try fetching expenses from pg
	try:
		context.bot.sendChatAction(chat_id=update.message.chat_id, action='Typing')
		r = requests.get(url=env.get('URL_VIEW_EXPENSE')+date[:5]+month_map[month])
		res_pg = r.json()
		if res_pg['Data'] is not None and res_pg['Success'] is not True:     
			text = ("Failed!"
					+"\nComment: " +res_pg['Comment']
					+"\nError: "+str(res_pg['Error'])+"."
                    +"\nType  /home  to return to main menu")
			markup = reply_markups.expensesReportMarkup
		if res_pg['Data'] is None: 
			text = ("You have not entered any expenses for "+month+" - "+date[:4]
					+"\nPlease type  /cancel  to abort."
                    +"\nOr select from below the month for which you'd like to view expenses for") 
			markup = reply_markups.monthsMarkup
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
							+"\nPlease type  /home  to finish"
                            +"\nOr select from below the month for which you'd like to view expenses for.") 
					markup = reply_markups.monthsMarkup
				else:
					#pick the non-empty fields
					res_mg_ = {key: value for key, value in res_mg['limits'].items() if value != ""}
					#create the reply
					text = ("Expenses by Category for "+month+" - "+date[:4]
							+"\n"
							+"\n{}".format(utils.convertExp_Lim(res_pg['Data'], res_mg_))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nType  /home  to return to main menu"
							+"\nOr type  /edit  to modify the set limits."
							+"\nOr select from below the month for which you'd like to view expenses for.") 
					markup = reply_markups.monthsMarkup
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

	# markup = ReplyKeyboardRemove()
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup)

	return TYPING_REPLY

# View total expenses for the current year for a selected category
# select category
# TODO: add provision for changing the year
# TODO: Also display the current budget limits alongside, if they are set
def totalByCategory(update: Update, context: CallbackContext):
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
				categories = [[KeyboardButton('Total expenses for '+category['Category'])] for category in response['Data']]
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
			utils.logger.error(e)
			reply_markup = ReplyKeyboardRemove()
	else:
		categories = [[KeyboardButton('Total expenses for '+cat)] for cat in context.user_data['allCats']]
		reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
		text = ("Select a category from below."
				+"\nOr type  /cancel  to choose other options."
				+"\nOr type  /home  to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup)
	
	return TYPING_REPLY

# View total expenses for the current year for a selected category
# confirm the category and display
def selectCategory(update: Update, context: CallbackContext):
	"""Flow to fetch various expense totals for the year for the selected category and display"""
	category = update.message.text.split('Total expenses for ')[1]
	year = 2019
	utils.logger.debug(category)
	conn, error = utils.connect()
	if error is None:
		rows, error = utils.getsqlrows(conn=conn)
		if error is None:
			MonthnCat = utils.gettotals(sqlrows=rows)
			expenses = MonthnCat.loc[category, year]
			# utils.logger.debug(expenses.to_dict())
			categories = [[KeyboardButton('Total expenses for '+cat)] for cat in context.user_data['allCats']]
			reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
			# utils.logger.debug("\n{}".format(utils.convertJson(expenses.to_dict())))
			# utils.logger.debug("\nTotal : {}".format(expenses.sum()))
			text = ("Current "+category+" expenses for "+str(year)
					+"\n{}".format(utils.convertJson(expenses.to_dict()))
					+"\nTotal : {}".format(expenses.sum())
					+"\nType  /cancel  to choose other options."
					+"\nOr Select a category to view expenses for from below."
					+"\nOr type  /home  to return to Main Menu")
			# utils.logger.debug(text)
		else: 
			utils.logger.error(error)
			text = ("Something went wrong!"
					+"\nType  /cancel  to choose other options."
					+"\nOr type  /home  to return to Main Menu")
			reply_markup = ReplyKeyboardRemove()
	else: 
		utils.logger.error(error)
		text = ("Something went wrong!"
				+"\nType  /cancel  to choose other options."
				+"\nOr type  /home  to return to Main Menu")
		reply_markup = ReplyKeyboardRemove()
	context.bot.send_message(chat_id=update.message.chat_id,
							text = text,
							reply_markup = reply_markup)
	
	return TYPING_REPLY

# View total expenses for the current year for a selected category
# display and allow other category selection for the selected year
def nextCategory(update: Update, context: CallbackContext):
	"""Provide user with keyboards to select other categories"""
	# Choose relevant reply markup
	markup = context.user_data['markups'][context.user_data['currentExpCat']]		
	text = ("Great! Choose next option to populate." 
			+"\nOr if done, tap Submit to post." 
			+"\nOr tap Abort to return to Main Menu")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup) 

	return CHOOSING