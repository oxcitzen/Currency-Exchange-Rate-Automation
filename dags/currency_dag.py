from airflow import DAG
from datetime import datetime, timedelta
#from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.contrib.sensors.file_sensor import FileSensor
from mysql_queries import run_mysql_queries  
from currency_rates import run_currency_api


def prepare_email(**kwargs):
    
    task_instance = kwargs['ti']
    output_file_path = task_instance.xcom_pull(task_ids='run_mysql_script', key="output_file_path")
    print(f"Received {output_file_path} from XCom")
    
    task_instance.xcom_push(key="email_files", value=output_file_path)
    print(f"Pushed {output_file_path} to XCom for email attachment")


def send_email(**kwargs):
    # Pull the files list from XCom
    task_instance = kwargs['ti']
    file = f"/usr/local/airflow/store_files_airflow/currency_rates_{task_instance.xcom_pull(task_ids='prepare_email', key='email_files')}.csv"
    print(f"File path: /usr/local/airflow/store_files_airflow/currency_rates_{file}.csv")
    
    # Send the email
    email_operator = EmailOperator(
        task_id='send_email',
        to='example@gmail.com',  #Replace with target email, use list if more than one target user
        subject='Weekly report generated',
        html_content=""" <h1>Congratulations! Your currency reports are ready.</h1> """,
        files=[file, '/usr/local/airflow/store_files_airflow/currency_rates_graph.png'],  
    )
    email_operator.execute(context=kwargs)


default_args = {
    'owner': 'Airflow',
    'start_date': datetime.now() - timedelta(minutes=1),
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}


with DAG('currency_dag', default_args=default_args, schedule_interval='@weekly', catchup=False) as dag:

    t1 = PythonOperator(
        task_id='run_currency_script',
        python_callable=run_currency_api, 
        provide_context=True,
    )
    
    t2 = FileSensor(
        task_id='check_currency_file_exists',
        filepath='/usr/local/airflow/store_files_airflow/currency_rates.csv',
        fs_conn_id='fs_default',
        poke_interval=10,
        timeout=150,
        soft_fail=True
    )
    
    
    t3 = FileSensor(
        task_id='check_currency_image_file_exists',
        filepath='/usr/local/airflow/store_files_airflow/currency_rates_graph.png',
        fs_conn_id='fs_default',
        poke_interval=10,
        timeout=150,
        soft_fail=True
    )
    
    t4 = PythonOperator(
        task_id='run_mysql_script',
        python_callable=run_mysql_queries,  
        provide_context=True,  
    )
    
    t5 = PythonOperator(
        task_id='prepare_email',
        python_callable=prepare_email,  
        provide_context=True,  
    )
      
    t6 = PythonOperator(
        task_id='send_email',
        python_callable=send_email,  
        provide_context=True,  
    )
    

    t1 >> [t2, t3] >> t4 >> t5 >> t6
