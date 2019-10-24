#!/usr/bin/env bash
cd ~/myexpensesbot/
chmod +x myexpensesbot.py
. ./.env
nohup ~/myexpensesbot/myexpensesbot.py &
