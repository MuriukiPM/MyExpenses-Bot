from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

# Predefine Main menu keyboard
mainMenu = [[KeyboardButton("New Expense")], 
            [KeyboardButton("Expenses Report"), KeyboardButton("Budget")],
            [KeyboardButton("Search Expenses"), KeyboardButton("List Expenses")]]

newExpense = [  [KeyboardButton("Timestamp"), KeyboardButton("Description")],
                [KeyboardButton("Proof"), KeyboardButton("Category")],
                [KeyboardButton("Amount"), KeyboardButton("Submit")], 
                [KeyboardButton("Main Menu")]]

newExpenseNoTs = [
    [KeyboardButton("Description"), KeyboardButton("Proof"), KeyboardButton("Category")],
    [KeyboardButton("Amount"), KeyboardButton("Submit"), KeyboardButton("Main Menu")]]

newExpenseNoDescr = [
    [KeyboardButton("Timestamp"), KeyboardButton("Proof"), KeyboardButton("Category")],
    [KeyboardButton("Amount"), KeyboardButton("Submit"), KeyboardButton("Main Menu")]]

newExpenseNoPrf = [
    [KeyboardButton("Timestamp"), KeyboardButton("Description"), KeyboardButton("Category")],
    [KeyboardButton("Amount"), KeyboardButton("Submit"), KeyboardButton("Main Menu")]]

newExpenseNoAmt = [
    [KeyboardButton("Timestamp"), KeyboardButton("Description"), KeyboardButton("Proof")],
    [KeyboardButton("Category"), KeyboardButton("Submit"), KeyboardButton("Main Menu")]]

newExpenseNoCat = [
    [KeyboardButton("Timestamp"), KeyboardButton("Description"), KeyboardButton("Proof")],
    [KeyboardButton("Amount"), KeyboardButton("Submit"), KeyboardButton("Main Menu")]]

budgetLimits = [[KeyboardButton("Set Budget Limits")],
                [KeyboardButton("View Budget Limits")],
                [KeyboardButton("Update Budget Limits")],
                [KeyboardButton("Main Menu")]]

expenseStats = [[KeyboardButton("View Expenses By Month")],
                [KeyboardButton("View Expenses By Category")],
                [KeyboardButton("Main Menu")]]

setLimits = [[KeyboardButton("View Budget Limits")],
             [KeyboardButton("Update Budget Limits")]]

months = [
    [KeyboardButton("Jan"), KeyboardButton("Feb"), KeyboardButton("Mar")],
    [KeyboardButton("Apr"), KeyboardButton("May"), KeyboardButton("June")],
    [KeyboardButton("July"), KeyboardButton("Aug"), KeyboardButton("Sept")],
    [KeyboardButton("Oct"), KeyboardButton("Nov"), KeyboardButton("Dec")]]

expenseList = [[KeyboardButton("List Expenses By Count")],
                [KeyboardButton("List Expenses By Date")],
                [KeyboardButton("Main Menu")]]

expenseSearch = [[KeyboardButton("Search Expenses By Expense ID")],
                [KeyboardButton("Search Expenses By Keyphrase")],
                [KeyboardButton("Main Menu")]]

backnHomeInline = [[InlineKeyboardButton("Back", callback_data="/cancel"), 
                    InlineKeyboardButton("Home", callback_data="/home")]]

donenBacknHomeInline = [[InlineKeyboardButton("Done", callback_data="/done"),
                        InlineKeyboardButton("Back", callback_data="/cancel"), 
                        InlineKeyboardButton("Home", callback_data="/home")]]

newExpenseNoAmtMarkup = ReplyKeyboardMarkup(newExpenseNoAmt, resize_keyboard=True, one_time_keyboard=True)

newExpenseNoPrfMarkup = ReplyKeyboardMarkup(newExpenseNoPrf, resize_keyboard=True, one_time_keyboard=True)

newExpenseNoDescrMarkup = ReplyKeyboardMarkup(newExpenseNoDescr, resize_keyboard=True, one_time_keyboard=True)

newExpenseNoTsMarkup = ReplyKeyboardMarkup(newExpenseNoTs, resize_keyboard=True, one_time_keyboard=True)

newExpenseNoCatMarkup = ReplyKeyboardMarkup(newExpenseNoCat, resize_keyboard=True, one_time_keyboard=True)

budgetLimitsMarkup = ReplyKeyboardMarkup(budgetLimits, resize_keyboard=True, one_time_keyboard=True)

expenseStatsMarkup = ReplyKeyboardMarkup(expenseStats, resize_keyboard=True, one_time_keyboard=True)

expenseListMarkup = ReplyKeyboardMarkup(expenseList, resize_keyboard=True, one_time_keyboard=True)

expenseSearchMarkup = ReplyKeyboardMarkup(expenseSearch, resize_keyboard=True, one_time_keyboard=True)

newExpenseMarkup = ReplyKeyboardMarkup(newExpense, resize_keyboard=True, one_time_keyboard=True)

setLimitsMarkup = ReplyKeyboardMarkup(setLimits, resize_keyboard=True, one_time_keyboard=True)

monthsMarkup = ReplyKeyboardMarkup(months, resize_keyboard=True, one_time_keyboard=True)

mainMenuMarkup = ReplyKeyboardMarkup(mainMenu, resize_keyboard=True, one_time_keyboard=True)

backnHomeInlineMarkup = InlineKeyboardMarkup(backnHomeInline, resize_keyboard=True)

donenBacknHomeInlineMarkup = InlineKeyboardMarkup(donenBacknHomeInline, resize_keyboard=True)

# must follow a certain order
expenseFlowMarkups = [	newExpenseNoTsMarkup, newExpenseNoDescrMarkup, newExpenseNoPrfMarkup, 
                        newExpenseNoCatMarkup, newExpenseNoAmtMarkup]