import json
import pendulum
import datetime
import requests
from sources import *
from bson import Decimal128
from airflow import DAG
from pymongo import MongoClient
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator


dag_historical = DAG(
    dag_id='exchange_rates_etl__historical',
    schedule_interval='@once',
    catchup=True,
    start_date=pendulum.today('UTC')
)


def _collect_data():
    end = pendulum.now()
    start = end.add(years=-1)
    with requests.Session() as s:
        response = s.get(
            url=SOURCES_API_URL_HIST,
            params={   # union of default API parameters and start/end date
                **SOURCES_API_PARAMS,
                **{'start_date': start.strftime('%Y-%m-%d'), 'end_date': end.strftime('%Y-%m-%d')}
            }
        )
        data_raw = response.json()
    with open('/tmp/historical.json', 'w') as f:
        json.dump(obj=data_raw['rates'], fp=f)


def _insert_data():
    with open('/tmp/historical.json', 'r') as f:
        data = json.load(fp=f)
    print(data)
    with MongoClient(SOURCES_DB_URI) as client:
        collection = client[SOURCES_DB_NAME][SOURCES_COLL_NAME]
        for k, v in data.items():
            rate = v.get(SOURCES_TO_CURR, None)
            rate = Decimal128(str(round(rate, 2))) if rate is not None else None
            collection.insert_one({
                'from_currency': SOURCES_FROM_CURR,
                'to_currency': SOURCES_TO_CURR,
                'rate': rate,
                'time': datetime.datetime.strptime(k, '%Y-%m-%d')
            })


def _clean_path():
    os.remove('/tmp/historical.json')


start = EmptyOperator(dag=dag_historical, task_id='exchange_rates_etl__historical_start')

collect_data = PythonOperator(
    dag=dag_historical,
    task_id='collect_data',
    python_callable=_collect_data,
    provide_context=True,
)

insert_data = PythonOperator(
    dag=dag_historical,
    task_id='insert_data',
    python_callable=_insert_data,
    provide_context=True,
)

clean_path = PythonOperator(
    dag=dag_historical,
    task_id='clean_path',
    python_callable=_clean_path,
    provide_context=True,
    trigger_rule='all_done'
)

start >> collect_data >> insert_data >> clean_path
