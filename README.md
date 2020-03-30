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

## Docker

$ docker image build -t myexpensesbot:V0.1 .

Using cloud build (most recent local commit). Requires gcloud project ID

$ gcloud builds submit --project $project --config=deploy/cloudbuild.yaml --substitutions _IMAGE_ID=myexpensesbot,_PROJECT_ID=$project,_REV_ID=$(git rev-parse HEAD),_ENV_ID=staging .

### To test locally

$ docker container run --rm --network="host" myexpensesbot:V0.1

Run on cloud instance using image from container repo (requires access to pull image)

$ docker container run -d --rm --network="host" gcr.io/$project/myexpensesbot:$(git rev-parse HEAD)

## Code layout

			.
			├── bot									- Bot sources
			│   ├── globals.py						- constant vars
			│   ├── handlers.py						- Bot handlers go here
			│   ├── reply_markups.py				- Keyboards and markups definitions
			│   └── utils.py						- Other utility functions
			├── botscript.sh
			├── myexpensesbot.py					- Main Program
			├── README.md
			└── .env_sample							- Environment variables										

## Config variables required:

			- TOKEN								Bot Token from @Botfather
			- URL_POST_EXPENSE					API Request endpoint [POST] to database
			- URL_SORTDESC						GET Request endpoint		
			- URL_CATEGORIES					GET Request endpoint
			- URL_VIEW_EXPENSE					GET Request endpoint
			- MONGO_HOST						URL of MONGO database host
			- MONGO_DATABASE_NAME				Name of the Mongo db.collection to be used
>
> ## TODO:
>
>	- Update readme