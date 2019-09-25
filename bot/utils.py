import logging
import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def convertJson(data):
    facts = list()
    for key, value in data.items():
        if key !='ID' and key !='ChatID':
            facts.append('{} : {}'.format(key, value))

    return ("\n".join(facts).join(['\n', '\n']))

def convertDict(user_data):
    items = list()

    for key, value in user_data.items():
        if value and (key is not 'retrieved'):
            items.append('{} : {}'.format(key, value))

    return "\n".join(items).join(['\n', '\n'])

# How many months back to look.
def subtract_one_month(dt0):
	dt1 = dt0.replace(day=1)
	dt2 = dt1 - datetime.timedelta(days=1)
	return dt2.replace(day=1)