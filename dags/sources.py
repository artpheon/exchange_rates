import os
import json
import datetime
import requests
from typing import Dict
from pymongo import MongoClient
from pymongo.collection import Collection
from airflow.exceptions import AirflowException
from bson import Decimal128


SOURCES_CONN_ID = 'mongodb'
SOURCES_DB_URI = os.environ.get('AIRFLOW_CONN_MONGODB')
SOURCES_DB_NAME = 'exchange_rates'
SOURCES_COLL_NAME = 'rates'
SOURCES_FROM_CURR = 'BTC'
SOURCES_TO_CURR = 'USD'
SOURCES_API_URL = 'https://api.exchangerate.host/latest'
SOURCES_API_URL_HIST = 'https://api.exchangerate.host/timeseries'
SOURCES_API_PARAMS = {'source': 'crypto', 'base': SOURCES_FROM_CURR, 'symbols': SOURCES_TO_CURR}
SOURCES_HIST_START_DATE = '2021-06-10'


def func_collect_data(url: str, params: Dict, start_date: str = None, **context):
    if start_date:
        params = {
            **params,
            **{'start_date': start_date, 'end_date': datetime.date.today().isoformat()}
        }
    with requests.Session() as s:
        response = s.get(url, params=params)
        response.raise_for_status()
        data_raw = response.json()
    if not data_raw['success']:
        raise AirflowException('Received data is not OK, wrong URL/parameters')
    run_id = context['run_id']
    with open(f'/tmp/{run_id}.json', 'w') as f:
        json.dump(fp=f, obj=data_raw)


def prepare_data(raw_data: Dict, date: str):
    rate = raw_data.get(SOURCES_TO_CURR, None)
    rate = Decimal128(str(rate)) if rate is not None else None
    return {
        'from_currency': SOURCES_FROM_CURR,
        'to_currency': SOURCES_TO_CURR,
        'rate': rate,
        'date': datetime.datetime.fromisoformat(date)
    }

def insert_data(doc: Dict, coll: Collection):
    coll.find_one_and_update(
        filter={k: v for k, v in doc.items() if k != 'rate'},
        update={
            '$set': {'rate': doc['rate']}
        },
        upsert=True
    )


def func_insert_data(**context):
    run_id = context['run_id']
    with open(f'/tmp/{run_id}.json', 'r') as f:
        data_raw = json.load(fp=f)
    with MongoClient(SOURCES_DB_URI) as client:
        collection = client[SOURCES_DB_NAME][SOURCES_COLL_NAME]
        if data_raw.get('timeseries', None) is not None:
            data_raw = data_raw['rates']
            for k, v in data_raw.items():
                insert_data(doc=prepare_data(raw_data=v, date=k), coll=collection)
        else:
            insert_data(doc=prepare_data(raw_data=data_raw['rates'], date=data_raw['date']),
                        coll=collection)


def func_clean_path(**context):
    run_id = context['run_id']
    os.remove(f'/tmp/{run_id}.json')
