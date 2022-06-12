import pendulum
from sources import *
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator


dag_historical = DAG(
    dag_id='exchange_rates_etl__historical',
    schedule_interval='@once',
    catchup=True,
    start_date=pendulum.today('UTC')
)

start = EmptyOperator(dag=dag_historical, task_id='exchange_rates_etl__historical_start')

collect_data = PythonOperator(
    dag=dag_historical,
    task_id='collect_data',
    python_callable=func_collect_data,
    provide_context=True,
    op_kwargs={
        'url': SOURCES_API_URL_HIST,
        'params': SOURCES_API_PARAMS,
        'start_date': SOURCES_HIST_START_DATE
    }
)

insert_data = PythonOperator(
    dag=dag_historical,
    task_id='insert_data',
    python_callable=func_insert_data,
    provide_context=True,
)

clean_path = PythonOperator(
    dag=dag_historical,
    task_id='clean_path',
    python_callable=func_clean_path,
    provide_context=True,
    trigger_rule='all_done'
)

start >> collect_data >> insert_data >> clean_path
