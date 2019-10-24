from os import environ as env
import logging
import datetime
from configparser import ConfigParser

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

# Accept list of dicts object and dict object and return formatted strings
def convertExp_Lim(exp_data, lim_data):
    """Given the values of expenses per category and 
       the values of the limits, return a 
       formatted string with the expenses and limits
    """
    facts = list()
    for item in exp_data:
        if item['Category'] not in lim_data.keys():
            facts.append('{} :\t {} of __ spent'.format(item['Category'], item['Metric']))
        else: facts.append('{} :\t {} of {} spent'.format(item['Category'], item['Metric'], lim_data[item['Category']]))
    
    return ("\n".join(facts).join(['\n', '\n']))
    
# How many months back to look.
def subtract_one_month(dt0):
	dt1 = dt0.replace(day=1)
	dt2 = dt1 - datetime.timedelta(days=1)
	return dt2.replace(day=1)

# Config parser
def config(filename, section='Environment'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to Environment
    configs = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            configs[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return configs
  
# Check if dev and return various vars needed
def dev():
    if env.get("DEV_CACERT_PATH",None) is None:	cacert_path = None
    else: cacert_path = env.get("HOME", "") + env.get("DEV_CACERT_PATH",None)
    
    return cacert_path