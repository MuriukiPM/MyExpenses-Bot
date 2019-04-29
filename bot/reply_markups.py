##
from telegram import KeyboardButton, ReplyKeyboardMarkup

# Predefine Main menu keyboard
mainMenu = [[KeyboardButton("New Expense")], 
            [KeyboardButton("View Expenses"),KeyboardButton("Search Expenses")]]

newExpense = [  [KeyboardButton("Timestamp"), KeyboardButton("Description")],
                [KeyboardButton("Proof"), KeyboardButton("Amount")],
                [KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoTs = [
    [KeyboardButton("Description"), KeyboardButton("Proof"), KeyboardButton("Amount")],
    [KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoDescr = [
    [KeyboardButton("Timestamp"), KeyboardButton("Proof"), KeyboardButton("Amount")],
    [KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoPrf = [
    [KeyboardButton("Timestamp"), KeyboardButton("Description"), KeyboardButton("Amount")],
    [KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoAmt = [
    [KeyboardButton("Timestamp"), KeyboardButton("Description"), KeyboardButton("Proof")],
    [KeyboardButton("Submit"), KeyboardButton("Abort")]]

newExpenseNoAmtMarkup = ReplyKeyboardMarkup(newExpenseNoAmt, resize_keyboard=True)

newExpenseNoPrfMarkup = ReplyKeyboardMarkup(newExpenseNoPrf, resize_keyboard=True)

newExpenseNoDescrMarkup = ReplyKeyboardMarkup(newExpenseNoDescr, resize_keyboard=True)

newExpenseNoTsMarkup = ReplyKeyboardMarkup(newExpenseNoTs, resize_keyboard=True)

newExpenseMarkup = ReplyKeyboardMarkup(newExpense, resize_keyboard=True)

mainMenuMarkup = ReplyKeyboardMarkup(mainMenu, resize_keyboard=True)

expenseFlowMarkups = [	newExpenseNoTsMarkup, newExpenseNoDescrMarkup,
                        newExpenseNoPrfMarkup, newExpenseNoAmtMarkup]