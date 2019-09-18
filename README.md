### To run the bot

			1. On initial start up:
            - Rename the `.env_sample` file to `.env`
            - Run $. ./.env
            - Unless server is shutdown, no need to run the env file on subsequent deploys. Delete.
			2. then run:
					
					$ python3 myexpensesbot.py

## Prerequisites

* python 3.6+
* python-telegram-bot 11+

## Code layout

				.
				├── bot												- Bot sources
				│   ├── globals.py						- constant vars
				│   ├── handlers.py						- Bot handlers go here
				│   ├── reply_markups.py			- Keyboards and markups definitions
				│   └── utils.py							- Other utility functions
				├── botscript.sh
				├── myexpensesbot.py					- Main Program
				├── README.md
				└── .env_sample								- Environment variables										

## Config variables required:

			- TOKEN								Bot Token from @Botfather
			- URL_EXPENSE					API Request endpoint [POST] to database
			- URL_SORTDESC				GET Request endpoint		
			- URL_CATEGORIES			GET Request endpoint
