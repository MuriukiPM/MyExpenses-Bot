## Deployment instructions

### Local Development

#### Host

##### Pre-requisites

1. python 3.6+
2. python-telegram-bot 12.2.0, pandas 0.25.1, numpy 1.17.1, dnspython 1.16.0, pymongo 3.9.0, requests 2.23.0, psycopg2 2.8.3
2. You will need a running myexpensesAPI service

##### Build and Run

1. Clone the app.
2. Make sure to edit and rename the [env-sample][env] file to _.env_. Set up the indicated environment variables.

``` sh
$ cd myexpensesbot
$ . ./.env && python3 myexpensesbot.py
```

#### Docker

```sh
$ docker image build -t myexpensesbot:V0.1 .
```

Using cloud build (most recent local commit). Requires gcloud project ID

```sh
$ gcloud builds submit --project $project --config=deploy/cloudbuild.yaml --substitutions _IMAGE_ID=myexpensesbot,_PROJECT_ID=$project,_REV_ID=$(git rev-parse HEAD),_ENV_ID=staging .
```

##### To test locally

```sh
$ docker container run --rm --network="host" myexpensesbot:V0.1
```

Run on cloud instance using image from container repo (requires access to pull image)

```sh
$ docker container run -d --rm --network="host" gcr.io/$project/myexpensesbot:$(git rev-parse HEAD)
```

[env]: </.env-sample>