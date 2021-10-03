from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


dag_params = {
    'dag_id': 'pg2pg',
    'start_date':datetime(2021, 10, 2),
    'schedule_interval': '@once'
}

def _transfer_data():
    src = PostgresHook(postgres_conn_id='pg_x')
    dest = PostgresHook(postgres_conn_id='pg_y')
    src_conn = src.get_conn()
    cursor = src_conn.cursor()
    dest_conn = dest.get_conn()
    dest_cursor = dest_conn.cursor()
    cursor.execute("SELECT * FROM tb_trx_src")
    dest.insert_rows(table="tb_trx_dest", rows=cursor)
    
    
with DAG(**dag_params) as dag:
    
    t1 = DummyOperator(task_id='start', dag=dag)

    t2 = PythonOperator(
        task_id='transfer_data',
        # provide_context=True,
        python_callable=_transfer_data,
        dag=dag)
    
    t1 >> t2
