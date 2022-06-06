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


dag_current = DAG(
    dag_id='exchange_rates_etl__current',
    schedule_interval=datetime.timedelta(hours=3),
    catchup=False,
    start_date=pendulum.today('UTC')
)

start = EmptyOperator(dag=dag_current, task_id='exchange_rates_etl__current_start')


def _collect_data(**context):
    with requests.Session() as s:
        response = s.get(SOURCES_API_URL, params=SOURCES_API_PARAMS)
        response.raise_for_status()
    data_raw = response.json()
    data = {
        'from_currency': SOURCES_FROM_CURR,
        'to_currency': SOURCES_TO_CURR,
        'rate': str(round(data_raw['rates'][SOURCES_TO_CURR], 2)),
        'time': datetime.datetime.utcnow().isoformat()
    }
    run_id = context['run_id']
    with open(f'/tmp/{run_id}.json', 'w') as f:
        json.dump(fp=f, obj=data)


def _insert_data(**context):
    run_id = context['run_id']
    with open(f'/tmp/{run_id}.json', 'r') as f:
        data = json.load(fp=f)
    data['rate'] = Decimal128(data['rate'])
    data['time'] = datetime.datetime.fromisoformat(data['time'])
    with MongoClient(SOURCES_DB_URI) as client:
        collection = client[SOURCES_DB_NAME][SOURCES_COLL_NAME]
        collection.insert_one(data)


def _clear_data(**context):
    run_id = context['run_id']
    os.remove(f'/tmp/{run_id}.json')


collect_data = PythonOperator(
    dag=dag_current,
    task_id='collect_data',
    python_callable=_collect_data,
    provide_context=True,
)

insert_data = PythonOperator(
    dag=dag_current,
    task_id='insert_data',
    python_callable=_insert_data,
    provide_context=True,
)

clear_data = PythonOperator(
    dag=dag_current,
    task_id='clear_data',
    python_callable=_clear_data,
    provide_context=True,
    trigger_rule='all_done'
)

start >> collect_data >> insert_data >> clear_data
