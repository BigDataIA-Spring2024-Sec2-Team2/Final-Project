import os
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import json
import requests
import google.oauth2.id_token
import google.auth.transport.requests
import configparser

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/dags/cloudfunction.json'
request = google.auth.transport.requests.Request()

config = configparser.ConfigParser()
config.read('/opt/airflow/dags/configuration.properties')
run_url = config['Cloud Functions']['cbcnews']


cbc_news_rss = {
    "task_world":["https://www.cbc.ca/webfeed/rss/rss-world", "world", "cbcnews/cbcnews-world.csv"],
    "task_politics":["https://www.cbc.ca/webfeed/rss/rss-politics", "politics", "cbcnews/cbcnews-politics.csv"],
    "task_business":["https://www.cbc.ca/webfeed/rss/rss-business", "business", "cbcnews/cbcnews-business.csv"],
    "task_health":["https://www.cbc.ca/webfeed/rss/rss-health", "health", "cbcnews/cbcnews-health.csv"],
    "task_technology":["https://www.cbc.ca/webfeed/rss/rss-technology", "technology", "cbcnews/cbcnews-technology.csv"],
    "task_art":["https://www.cbc.ca/webfeed/rss/rss-arts", "art", "cbcnews/cbcnews-art.csv"],
    "task_sports":["https://www.cbc.ca/webfeed/rss/rss-sports", "sports", "cbcnews/cbcnews-sports.csv"],
    "task_football":["https://www.cbc.ca/webfeed/rss/rss-sports-soccer", "football", "cbcnews/cbcnews-football.csv"],
    "task_olympics":["https://www.cbc.ca/webfeed/rss/rss-sports-olympics", "olympics", "cbcnews/cbcnews-olympics.csv"],
}

def call_cloudFunction(base_url, category, file_name, **kwargs):
    TOKEN = google.oauth2.id_token.fetch_id_token(request, run_url)
    r = requests.post(
        run_url, 
        headers={'Authorization': f"Bearer {TOKEN}", "Content-Type": "application/json"},
        data=json.dumps({"base_url": base_url, 'category': category, 'file_name': file_name})
    )
    
    if r.status_code != 200:
        Exception("The Site can not be loaded")
        
    status, reason, args = r.text.split(" | ")
    if status == "Fail":
        Exception("reason")
    
    if "No New Data" in reason:
        kwargs['ti'].xcom_push(key='newdata_status', value=False)
    kwargs['ti'].xcom_push(key='newdata_status', value=True)

dag = DAG(
    dag_id="dag_cbcnews",
    schedule=None,
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    max_active_runs=10
)

# Define tasks
start_task = DummyOperator(task_id='start', dag=dag)
end_task = DummyOperator(task_id='end', dag=dag)

# Define parallel tasks
parallel_tasks = []
task_after_parallel_tasks = []

for key, values in cbc_news_rss.items():
    parallel_task = PythonOperator(
        task_id=key,
        python_callable=call_cloudFunction,
        dag=dag,
        provide_context=True,
        op_args=values
    )
    
    parallel_tasks.append(parallel_task)
    
    
start_task >> parallel_tasks >> end_task