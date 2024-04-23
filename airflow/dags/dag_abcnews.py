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
run_url = config['Cloud Functions']['abcnews']


abc_news_rss = {
    "task_top":["https://abcnews.go.com/abcnews/topstories", "top", "abcnews/abcnews-top-story.csv"],
    "task_us":["https://abcnews.go.com/abcnews/usheadlines", "us", "abcnews/abcnews-us.csv"],
    "task_international":["https://abcnews.go.com/abcnews/internationalheadlines", "international", "abcnews/abcnews-international.csv"],
    "task_politics":["https://abcnews.go.com/abcnews/politicsheadlines", "politics", "abcnews/abcnews-politics.csv"],
    "task_technology":["https://abcnews.go.com/abcnews/technologyheadlines", "technology", "abcnews/abcnews-technology.csv"],
    "task_health":["https://abcnews.go.com/abcnews/healthheadlines", "health", "abcnews/abcnews-health.csv"],
    "task_entertainment":["https://abcnews.go.com/abcnews/entertainmentheadlines", "entertainment", "abcnews/abcnews-entertainment.csv"],
    "task_travel":["https://abcnews.go.com/abcnews/travelheadlines", "travel", "abcnews/abcnews-travel.csv"],
    "task_sports":["https://abcnews.go.com/abcnews/sportsheadlines", "sports", "abcnews/abcnews-sports.csv"]
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
    dag_id="dag_abcnews",
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

for key, values in abc_news_rss.items():
    parallel_task = PythonOperator(
        task_id=key,
        python_callable=call_cloudFunction,
        dag=dag,
        provide_context=True,
        op_args=values
    )
    
    parallel_tasks.append(parallel_task)
    
    
start_task >> parallel_tasks >> end_task