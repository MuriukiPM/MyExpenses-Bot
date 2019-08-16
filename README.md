### To run the bot
 1. Rename the `config_sample.py` file under the bot/ subfolder to `config.py`
 2. in your config.py file, add the config secrets listed in 'Config' below
 3. then run:

   $ python myexpensesbot.py

## Prerequisites
* python-telegram-bot 11+

## Code layout
    bot/              		Bot sources
		*config.py						secret keys
		globals.py						constant vars
		handlers.py  					Bot handlers go here	
		reply_markups.py    	Keyboards and markups definitions
		utils.py            	Other utility functions

    myexpensesbot.py    Main Program

## Config
- TOKEN								Bot Token from @Botfather
- URL_EXPENSE	    		API Request URL [POST] to database
- URL_SORTDESC		
- URL_CATEGORIES	
