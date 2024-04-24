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
run_url = config['Cloud Functions']['nytimes']


ny_timess_rss = {
    "task_world":["https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "world", "nytimes/nytimes-world.csv"],
    "task_us":["https://rss.nytimes.com/services/xml/rss/nyt/US.xml", "us", "nytimes/nytimes-us.csv"],
    "task_europe":["https://rss.nytimes.com/services/xml/rss/nyt/Europe.xml", "europe", "nytimes/nytimes-europe.csv"],
    "task_education":["https://rss.nytimes.com/services/xml/rss/nyt/Education.xml", "education", "nytimes/nytimes-education.csv"],
    "task_economy":["https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml", "economy", "nytimes/nytimes-economy.csv"],
    "task_technology":["https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "technology", "nytimes/nytimes-technology.csv"],
    "task_sports":["https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml", "sports", "nytimes/nytimes-sports.csv"],
    "task_baseball":["https://rss.nytimes.com/services/xml/rss/nyt/Baseball.xml", "baseball", "nytimes/nytimes-baseball.csv"],
    "task_football":["https://rss.nytimes.com/services/xml/rss/nyt/Soccer.xml", "football", "nytimes/nytimes-football.csv"],
    "task_tennis":["https://rss.nytimes.com/services/xml/rss/nyt/Tennis.xml", "tennis", "nytimes/nytimes-tennis.csv"],
    "task_health":["https://rss.nytimes.com/services/xml/rss/nyt/Health.xml", "health", "nytimes/nytimes-health.csv"],
    "task_environment":["https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml", "environment", "nytimes/nytimes-environment.csv"],
    "task_travel":["https://rss.nytimes.com/services/xml/rss/nyt/Travel.xml", "travel", "nytimes/nytimes-travel.csv"],
    "task_golf":["https://rss.nytimes.com/services/xml/rss/nyt/Golf.xml", "golf", "nytimes/nytimes-golf.csv"],
    "task_politics":["https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml", "politics", "nytimes/nytimes-politics.csv"],
    "task_middleeast":["https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml", "middleeast", "nytimes/nytimes-middleeast.csv"],
    "task_job":["https://rss.nytimes.com/services/xml/rss/nyt/Jobs.xml", "job", "nytimes/nytimes-job.csv"],
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
    dag_id="dag_nytimes",
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

for key, values in ny_timess_rss.items():
    parallel_task = PythonOperator(
        task_id=key,
        python_callable=call_cloudFunction,
        dag=dag,
        provide_context=True,
        op_args=values
    )
    
    parallel_tasks.append(parallel_task)
    
    
start_task >> parallel_tasks >> end_task