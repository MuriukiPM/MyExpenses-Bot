from telegram import KeyboardButton, ReplyKeyboardMarkup

# Predefine Main menu keyboard
mainMenu = [[KeyboardButton("New Expense")], 
            [KeyboardButton("Expenses Report"),KeyboardButton("Search Expenses")]]

newExpense = [  [KeyboardButton("Timestamp"), KeyboardButton("Description")],
                [KeyboardButton("Proof"), KeyboardButton("Category")],
                [KeyboardButton("Amount"), KeyboardButton("Submit")], 
                [KeyboardButton("Abort")]]

newExpenseNoTs = [
    [KeyboardButton("Description"), KeyboardButton("Proof"), KeyboardButton("Category")],
    [KeyboardButton("Amount"), KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoDescr = [
    [KeyboardButton("Timestamp"), KeyboardButton("Proof"), KeyboardButton("Category")],
    [KeyboardButton("Amount"), KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoPrf = [
    [KeyboardButton("Timestamp"), KeyboardButton("Description"), KeyboardButton("Category")],
    [KeyboardButton("Amount"), KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoAmt = [
    [KeyboardButton("Timestamp"), KeyboardButton("Description"), KeyboardButton("Proof")],
    [KeyboardButton("Category"), KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoCat = [
    [KeyboardButton("Timestamp"), KeyboardButton("Description"), KeyboardButton("Proof")],
    [KeyboardButton("Amount"), KeyboardButton("Submit"), KeyboardButton("Abort")]]

expensesReport = [[KeyboardButton("Set Limits")],
                [KeyboardButton("View Limits")],
                [KeyboardButton("Update Limits")],
                [KeyboardButton("View Expenses By Month")],
                [KeyboardButton("View Expenses By Category")],
                [KeyboardButton("Abort")]]

setLimits = [[KeyboardButton("View Limits")],
             [KeyboardButton("Update Limits")]]

newExpenseNoAmtMarkup = ReplyKeyboardMarkup(newExpenseNoAmt, resize_keyboard=True)

newExpenseNoPrfMarkup = ReplyKeyboardMarkup(newExpenseNoPrf, resize_keyboard=True)

newExpenseNoDescrMarkup = ReplyKeyboardMarkup(newExpenseNoDescr, resize_keyboard=True)

newExpenseNoTsMarkup = ReplyKeyboardMarkup(newExpenseNoTs, resize_keyboard=True)

newExpenseNoCatMarkup = ReplyKeyboardMarkup(newExpenseNoCat, resize_keyboard=True)

expensesReportMarkup = ReplyKeyboardMarkup(expensesReport, resize_keyboard=True)

newExpenseMarkup = ReplyKeyboardMarkup(newExpense, resize_keyboard=True)

setLimitsMarkup = ReplyKeyboardMarkup(setLimits, resize_keyboard=True)

mainMenuMarkup = ReplyKeyboardMarkup(mainMenu, resize_keyboard=True)

# must follow a certain order
expenseFlowMarkups = [	newExpenseNoTsMarkup, newExpenseNoDescrMarkup, newExpenseNoPrfMarkup, 
                        newExpenseNoCatMarkup, newExpenseNoAmtMarkup]