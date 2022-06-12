import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from sources import *


dag_current = DAG(
    dag_id='exchange_rates_etl__current',
    schedule_interval=datetime.timedelta(hours=3),
    catchup=False,
    start_date=pendulum.today('UTC')
)

start = EmptyOperator(dag=dag_current, task_id='exchange_rates_etl__current_start')

collect_data = PythonOperator(
    dag=dag_current,
    task_id='collect_data',
    python_callable=func_collect_data,
    provide_context=True,
    op_kwargs={
        'url': SOURCES_API_URL,
        'params': SOURCES_API_PARAMS
    }
)

insert_data = PythonOperator(
    dag=dag_current,
    task_id='insert_data',
    python_callable=func_insert_data,
    provide_context=True,
)

clean_path = PythonOperator(
    dag=dag_current,
    task_id='clean_path',
    python_callable=func_clean_path,
    provide_context=True,
    trigger_rule='all_done'
)

start >> collect_data >> insert_data >> clean_path
