from os import environ as env

import requests, json, datetime
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup
import pymongo

from bot import reply_markups
from libs import utils
from bot.globals import *

def cancelInlineButton(update: Update, context: CallbackContext):
    context.user_data['inputYear'] = ''
    text = ("Select an option from below to proceed.")
    context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                            text = text,
                            reply_markup = reply_markups.expenseStatsMarkup) 
    
    return CHOOSING

# Flow for expense reports begins here
# TODO: Improve expenses report conversation flow
# TODO: Temporarily store results from mongo, pg queries in memory to speed up?
def expensesReport(update: Update, context: CallbackContext):
	"""
		Initiate expense reporting
	"""
	context.user_data['inputYear'] = ''
	text = ("Select an option from below to proceed.")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markups.expenseStatsMarkup) 
	
	return CHOOSING

# View total expenses for a given month
# TODO: Provide better status messages when fetching data from servers
# TODO: show all of the current year's expenses alongside total amount for each expense category in that month
def totalByMonth(update: Update, context: CallbackContext):
	"""
		Start the flow to view current expenses for a given month
	"""
	utc_datetime = datetime.datetime.utcnow()
	local_datetime = (utc_datetime + datetime.timedelta(hours=UTC_OFFSET))
	year = str(local_datetime.year)
	text = ("Using '"+year+"' as the selected year"
			+"\n"
			+"\nPlease select an option or retype the year in full for which to view expenses")
	reply_markup = reply_markups.donenBacknHomeInlineMarkup
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = reply_markup) 
	
	return CHOOSING

# View total expenses for the current month
# select year
def selectYearWMonth(update: Update, context: CallbackContext):
	"""
		display month list for the provided year
	"""
	year = update.message.text
	context.user_data['inputYear'] = year
	text = ("Received '"+year+"' as the selected year"
			+"\nPlease select from below the month for which you'd like to view expenses for"
			+"\nor type in the year in full for which to view expenses"
			+"\nOr type  /cancel  to abort.")
	markup = reply_markups.monthsMarkup
	context.bot.send_message(chat_id=update.message.chat_id,
							text = text,
							reply_markup = markup)

	return CHOOSING

# View total expenses for the current month
# use default year and display
def viewByMonth(update: Update, context: CallbackContext):
	"""
		fetch and display expenses totals for the selected month, for the current year
	"""
	month_map = {
		'01':'Jan',
		'02':'Feb',
		'03':'Mar',
		'04':'April',
		'05':'May',
		'06':'June',
		'07':'July',
		'08':'Aug',
		'09':'Sep',
		'10':'Oct',
		'11':'Nov',
		'12':'Dec'}
	# chat_ID = update.message.chat_id
	chat_ID = update.callback_query.message.chat_id
	#get the local time
	dt0 = datetime.datetime.utcnow()+ datetime.timedelta(hours=UTC_OFFSET)
	date = dt0.strftime("%Y-%m-%d %H:%M:%S")[:7] #only current the year and month
	cacert_path = utils.dev()
	#try fetching expenses from pg
	try:
		context.bot.sendChatAction(chat_id=chat_ID, action='Typing')
		r = requests.get(url=env.get('URL_VIEW_EXPENSE'),
						params={'chat_id':chat_ID,'date':date})
		res_pg = r.json()
		if res_pg['Data'] is not None and res_pg['Success'] is not True:     # some error 
			text = ("Failed!"
					+"\nComment: " +res_pg['Comment']
					+"\nError: "+str(res_pg['Error'])+".")
			markup = reply_markups.expenseStatsMarkup
		if res_pg['Data'] is None: #no expenses for current month
			text = ("You have not entered any expenses for "+month_map[date[5:7]]+" - "+date[:4]
					+"\nPlease select from below the month for which you'd like to view expenses for"
					+"\nOr type  /cancel  to abort.")
			markup = reply_markups.monthsMarkup
			context.bot.send_message(chat_id=chat_ID,
									text = text,
									reply_markup = markup)

			return TYPING_REPLY
		else:       # no errors
			#get the sum
			sum_exp = 0
			for exp in res_pg['Data']: sum_exp += exp['Metric']
			#try fetching expenses limits from mongo
			try: 
				context.bot.sendChatAction(chat_id=chat_ID, action='Typing')
				client = pymongo.MongoClient(env.get("MONGO_HOST"),
											ssl=True,
											ssl_ca_certs=cacert_path)
				db = client.get_database(env.get("MONGO_DATABASE_NAME"))
				collection = db.get_collection(env.get("MONGO_COLLECTION_NAME"))
				res_mg = collection.find_one({"_id":chat_ID})
				if res_mg is None: #no limit values have been set for the user
					text = ("Expenses by Category for "+month_map[date[5:7]]+" - "+date[:4]
							+"\n{}".format(utils.convertList(res_pg['Data']))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nTo view the expenses in comparison to the budget limits, please type" 
							+"  /edit  to input budget limits"
							+"\nOr select from below the month for which you'd like to view expenses for"
							+"\nOr type  /home  to finish")
					markup = reply_markups.monthsMarkup
					context.bot.send_message(chat_id=chat_ID,
									text = text,
									reply_markup = markup)

					return TYPING_REPLY
				else:
					#pick the non-empty fields
					res_mg_ = {key: value for key, value in res_mg['limits'].items() if value != ""}
					#create the reply
					text = ("Expenses by Category for "+month_map[date[5:7]]+" - "+date[:4]
							+"\n{}".format(utils.convertExp_Lim(res_pg['Data'], res_mg_))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nType  /home  to return to main menu"
							+"\nType  /cancel  to choose other options."
							+"\nOr type  /edit  to modify the set budget limits."
							+"\nOr select from below the month for which you'd like to view expenses for")
					markup = reply_markups.monthsMarkup
					context.bot.send_message(chat_id=chat_ID,
									text = text,
									reply_markup = markup)

					return TYPING_REPLY
			except Exception as error:
				text = ("ERROR: "+str(error))
				markup = reply_markups.backnHomeInlineMarkup
				utils.logger.error(error)
	except Exception as error:
		text = ("Something went wrong.")
		markup = reply_markups.backnHomeInlineMarkup
		utils.logger.error(error)
	context.bot.send_message(chat_id=chat_ID,
					text = text,
					reply_markup = markup)

	return CHOOSING

# View total expenses for the provided month
# confirm the month and display
def selectMonth(update: Update, context: CallbackContext):
	"""
		fetch and display various expense totals for the provided month
	"""
	chat_ID = update.message.chat_id
	month = update.message.text
	if (context.user_data['inputYear'] != ''):
		year = context.user_data['inputYear']
	else:
		# dt0 = datetime.datetime.utcnow()+ datetime.timedelta(hours=UTC_OFFSET)
		# year = dt0.strftime("%Y-%m-%d %H:%M:%S")[:4] #only current the year
		utc_datetime = datetime.datetime.utcnow()
		local_datetime = (utc_datetime + datetime.timedelta(hours=UTC_OFFSET))
		year = str(local_datetime.year)
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
	cacert_path = utils.dev() #if in dev mode use local cert for mongo ssl connection
	#try fetching expenses from pg
	try:
		context.bot.sendChatAction(chat_id=chat_ID, action='Typing')
		date = year+"-"+month_map[month.lower()]
		r = requests.get(url=env.get('URL_VIEW_EXPENSE'),
						params={'chat_id':chat_ID,'date':date})
		res_pg = r.json()
		if res_pg['Data'] is not None and res_pg['Success'] is not True:     
			text = ("Failed!"
					+"\nComment: " +res_pg['Comment']
					+"\nError: "+str(res_pg['Error'])+"."
                    +"\nType  /home  to return to main menu")
			markup = reply_markups.expenseStatsMarkup
		if res_pg['Data'] is None: 
			text = ("You have not entered any expenses for "+month+" - "+year
					+"\nPlease type  /cancel  to choose other options."
                    +"\nOr select from below the month for which you'd like to view expenses for") 
			markup = reply_markups.monthsMarkup
		else:       # no errors
			#get the sum
			sum_exp = 0
			for exp in res_pg['Data']: sum_exp += exp['Metric']
			#try fetching data from mongo
			try: 
				context.bot.sendChatAction(chat_id=chat_ID, action='Typing')
				client = pymongo.MongoClient(env.get("MONGO_HOST"),
											ssl=True,
											ssl_ca_certs=cacert_path)
				db = client.get_database(env.get("MONGO_DATABASE_NAME"))
				collection = db.get_collection(env.get("MONGO_COLLECTION_NAME"))
				res_mg = collection.find_one({"_id":update.message.chat_id})
				if res_mg is None: #no limit values have been set for the user. 
					text = ("Expenses by Category for "+month+" - "+year
							+"\n{}".format(utils.convertList(res_pg['Data']))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nTo view the expenses in comparison to the budget limits, please type"
							+"  /edit  to input budget limits"
							+"\nPlease type  /home  to finish"
                            +"\nOr select from below the month for which you'd like to view expenses for.") 
					markup = reply_markups.monthsMarkup
				else:
					#pick the non-empty fields
					res_mg_ = {key: value for key, value in res_mg['limits'].items() if value != ""}
					#create the reply
					text = ("Expenses by Category for "+month+" - "+year
							+"\n{}".format(utils.convertExp_Lim(res_pg['Data'], res_mg_))
							+"\nTotal expenses: {}".format(sum_exp)
							+"\nType  /home  to return to main menu"
							+"\nType  /cancel  to choose other options."
							+"\nOr type  /edit  to modify the set budget limits."
							+"\nOr select from below the month for which you'd like to view expenses for.") 
					markup = reply_markups.monthsMarkup
			except Exception as error:
				text = ("ERROR: "+str(error))
				markup = reply_markups.expenseStatsMarkup
				utils.logger.error(error)
	except Exception as error:
		text = ("Something went wrong."
				+"\n"
				+"\nNo connection to the db server."
				+"\n"
				+"Type in the category. Or  /cancel  to choose other options."
				+"\nOr  /home  to return to Main Menu")   
		markup = reply_markups.expenseStatsMarkup
		utils.logger.error(error)

	context.bot.send_message(chat_id=chat_ID,
					text = text,
					reply_markup = markup)

	return TYPING_REPLY

# View total expenses for the selected year for a selected category
# TODO: Also display the current budget limits alongside, if they are set
def totalByCategory(update: Update, context: CallbackContext):
	"""
		Flow to view current expenses for a given month starts here
	"""
	chat_ID = update.message.chat_id
	utc_datetime = datetime.datetime.utcnow()
	local_datetime = (utc_datetime + datetime.timedelta(hours=UTC_OFFSET))
	year = str(local_datetime.year)
	#get current categories from pgdb if not already fetched
	if len(context.user_data['allCats']) == 0: #not yet fetched
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
				reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Main Menu')]], resize_keyboard=True) 
			else:       # no errors
				# append the categories to the reply markup list and to limit dict
				categories = [[KeyboardButton('Total expenses for '+category['Category'])] for category in response['Data']]
				context.user_data['allCats'] = [category['Category'] for category in response['Data']]
				reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
				text = ("Using '"+year+"' as the selected year"
						+"\n"
						+"\nTo proceed, select a category from below."
						+"\nor type in the year in full for which to view expenses"
						+"\nOr  /cancel  to choose other options "
						+"\nOr  /home  to return to Main Menu")
		except Exception as e:
			text = ("Something went wrong."
					+"\n"
					+"\nNo connection to the db server.")
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Main Menu')]], resize_keyboard=True)    
			utils.logger.error(e)
	else:
		categories = [[KeyboardButton('Total expenses for '+cat)] for cat in context.user_data['allCats']]
		reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
		text = ("Using '"+year+"' as the selected year"
				+"\n"
				+"\nTo proceed, select a category from below."
				+"\nor type in the year in full for which to view expenses"
				+"\nOr  /cancel  to choose other options "
				+"\nOr  /home  to return to Main Menu")
	context.bot.send_message(chat_id=chat_ID,
					text = text,
					reply_markup = reply_markup)
	
	return TYPING_REPLY

# View total expenses for the selected year for a selected category
# select year and display categories
def selectYearWCategory(update: Update, context: CallbackContext):
	"""
		Store a provided year, display category list
	"""
	chat_ID = update.message.chat_id
	year = update.message.text
	context.user_data['inputYear'] = year
	#get current categories from pgdb if not already fetched
	if len(context.user_data['allCats']) == 0: #not yet fetched
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
				reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Main Menu')]], resize_keyboard=True) 
			else:       # no errors
				# append the categories to the reply markup list and to limit dict
				categories = [[KeyboardButton('Total expenses for '+category['Category'])] for category in response['Data']]
				context.user_data['allCats'] = [category['Category'] for category in response['Data']]
				reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
				text = ("Received '"+year+"' as the selected year"
						+"\nSelect a category from below."
						+"\nor type in the year in full for which to view expenses"
						+"\nOr  /cancel  to choose other options."
						+"\nOr  /home  to return to Main Menu")
		except Exception as e:
			text = ("Something went wrong."
					+"\n"
					+"\nNo connection to the db server.")
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Main Menu')]], resize_keyboard=True) 
			utils.logger.error(e)
	else:
		categories = [[KeyboardButton('Total expenses for '+cat)] for cat in context.user_data['allCats']]
		reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
		text = ("Received '"+year+"' as the selected year"
				+"\nSelect a category from below."
				+"\nor type in the year in full for which to view expenses"
				+"\nOr  /cancel  to choose other options."
				+"\nOr  /home  to return to Main Menu")
	context.bot.send_message(chat_id=chat_ID,
					text = text,
					reply_markup = reply_markup)
	
	return TYPING_REPLY

# View total expenses for the current year for a selected category
# confirm the category and display
def selectCategory(update: Update, context: CallbackContext):
	"""
		Flow to fetch various expense totals for the selected year for the selected category 
		and display
	"""
	category = update.message.text.split('Total expenses for ')[1]
	if (context.user_data['inputYear'] != ''):
		year = int(context.user_data['inputYear'])
	else:
		utc_datetime = datetime.datetime.utcnow()
		local_datetime = (utc_datetime + datetime.timedelta(hours=UTC_OFFSET))
		year = local_datetime.year
	utils.logger.debug(category)
	conn, error = utils.connect()
	if error is None:
		rows, error = utils.getsqlrows(conn=conn, chat_id=str(update.message.from_user.id))
		if error is None:
			MonthnCat = utils.gettotals(sqlrows=rows)
			expenses = MonthnCat.loc[category, year]
			categories = [[KeyboardButton('Total expenses for '+cat)] for cat in context.user_data['allCats']]
			reply_markup = ReplyKeyboardMarkup(categories, resize_keyboard=True)
			text = (category+" expenses for "+str(year)
					+"\n{}".format(utils.convertJson(expenses.to_dict()))
					+"\nTotal : {}".format(expenses.sum())
					+"\nType  /cancel  to choose other options."
					+"\nOr Select a category to view expenses for from below."
					+"\nOr type in the year in full for which to view expenses"
					+"\nOr type  /home  to return to Main Menu")
			# utils.logger.debug(text)
		else: 
			utils.logger.error("Error fetching pandas rows: "+repr(error))
			text = ("Something went wrong on the server")
			reply_markup = reply_markups.backnHomeInlineMarkup
	else: 
		utils.logger.error(error)
		text = ("Something went wrong!")
		reply_markup = reply_markups.backnHomeInlineMarkup
	context.bot.send_message(chat_id=update.message.chat_id,
							text = text,
							reply_markup = reply_markup)
	
	return TYPING_REPLY

# View total expenses for the current year for a selected category
# display and allow other category selection for the selected year
def nextCategory(update: Update, context: CallbackContext):
	"""
		Provide user with keyboards to select other categories
	"""
	# Choose relevant reply markup
	markup = context.user_data['markups'][context.user_data['currentExpCat']]		
	text = ("Great! Choose next option to populate." 
			+"\nOr if done, tap Submit to post.")
	context.bot.send_message(chat_id=update.message.chat_id,
					text = text,
					reply_markup = markup) 

	return CHOOSING
