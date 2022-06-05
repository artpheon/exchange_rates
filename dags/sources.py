import os

SOURCES_CONN_ID = 'mongodb'
SOURCES_DB_URI = os.environ.get('AIRFLOW_CONN_MONGODB')
SOURCES_DB_NAME = 'exchange_rates'
SOURCES_COLL_NAME = 'rate'
SOURCES_FROM_CURR = 'BTC'
SOURCES_TO_CURR = 'USD'
SOURCES_API_URL = 'https://api.exchangerate.host/latest'
SOURCES_API_PARAMS = {'source': 'crypto', 'base': SOURCES_FROM_CURR, 'symbols': SOURCES_TO_CURR}
