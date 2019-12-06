from os import environ as env
import logging
import datetime
from configparser import ConfigParser

import pandas as pd
import numpy as np
import psycopg2

# Enable logging
# https://docs.python.org/3/library/logging.html#logrecord-attributes
level = logging.INFO
if env.get("ENV_MODE") == "dev": level = logging.DEBUG
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s:%(lineno)d',
                    level=level)

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
        if value and (key != 'retrieved'):
            items.append('{} : {}'.format(key, value))

    return "\n".join(items).join(['\n', '\n'])

def convertList(data):
    facts = list()

    for item in data:
        facts.append('{} : {}'.format(item['Category'], item['Metric']))
    
    return ("\n".join(facts).join(['\n', '\n']))

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

def connect():
    """ Connect to the PostgreSQL database server and quick test"""
    
    conn = None
    err = None
    try: 
        # connect to the PostgreSQL server
        logger.info('Connecting to the PostgreSQL database...')
        params = {"host":env.get("DB_HOST"),"database":env.get("DB_NAME"),"user":env.get("DB_USER"),
                "password":env.get("DB_PASSWORD"),"port":env.get("DB_PORT")}
        logger.debug("connstr: "+str(params))
        conn = psycopg2.connect(**params)
      
        # create a cursor
        cur = conn.cursor()
        
        # execute a statement
        cur.execute('SELECT version()')
 
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        logger.info("PostgreSQL database version: "+str(db_version))
       
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        err = error
       
    return conn, err

def getsqlrows(conn):
    """getsqlrows queries the database for rows"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * from expenses")
        rows = cur.fetchall()
        logger.info("Num of rows: "+str(len(rows)))
        cur.close()
        conn.close()

        return rows, None
    except (Exception, psycopg2.Error) as error:
        conn.close()

        return None, error

def getdatatable(sqlrows):
    """getdatatable creates a table with expense rows from rows returned from sql query"""
    month_map = {1:'Jan',2:'Feb',3:'Mar',4:'April',5:'May',6:'June',7:'July',8:'Aug',9:'Sept',10:'Oct',11:'Nov',12:'Dec'}
    day_map = {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}
    df = pd.DataFrame(data=sqlrows,columns=['rowid','timestamp','description','proof','amount','category'])
    df_raw = df.copy()
    df['timestamp']=pd.to_datetime(df['timestamp'])
    df['hour']=df['timestamp'].apply(lambda time: time.hour)
    df['month']=df['timestamp'].apply(lambda time: time.month).map(month_map)
    df['year']=df['timestamp'].apply(lambda time: time.year)
    df['day_of_week']=df['timestamp'].apply(lambda time: time.dayofweek).map(day_map)
    
    return df_raw, df

def gettotals(sqlrows):
    """gettotals creates a multi-index table of sum of expenses sorted by category and month"""
    _, df = getdatatable(sqlrows=sqlrows)
    months = df.month.unique()
    MonthnCat = df.groupby(['category','year','month'])['amount'].sum().unstack(1)
    MonthnCat = MonthnCat.reindex(pd.MultiIndex.from_product([MonthnCat.index.levels[0], months], names=['category', 'month']))
    MonthnCat.fillna(value=0.0, inplace=True)
    MonthnCat = MonthnCat.astype('int')

    return MonthnCat