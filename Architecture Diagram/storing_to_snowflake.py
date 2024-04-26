import snowflake.connector
from google.cloud import storage


SNOWFLAKE_ACCOUNT = 'rylgxtl-ak42073'
SNOWFLAKE_USER = 'narayani1999'
SNOWFLAKE_PASSWORD = 'Y3nHpRMKE5pvn25'
SNOWFLAKE_DATABASE = 'News'
SNOWFLAKE_SCHEMA = 'web_scrape_files'


GCS_BUCKET_NAME = 'web-scraped-clean-data'
GCS_FOLDER_PATH = 'abcnews_cleaned/'
GCS_CREDENTIALS_JSON = 'cloudfunction.json'


conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA
)
conn.cursor().execute(f'USE SCHEMA {SNOWFLAKE_SCHEMA}')


client = storage.Client.from_service_account_json(GCS_CREDENTIALS_JSON)
bucket = client.get_bucket(GCS_BUCKET_NAME)


stage_name = 'gcs_stage'
conn.cursor().execute(f'CREATE OR REPLACE STAGE {stage_name}')


table_name = 'test'
table_columns = 'title VARCHAR, link VARCHAR, publish_date TIMESTAMP, description VARCHAR, image_url VARCHAR, category VARCHAR, source VARCHAR'


create_table_sql = f'CREATE OR REPLACE TABLE {table_name} ({table_columns})'
conn.cursor().execute(create_table_sql)


file_paths = [blob.name for blob in bucket.list_blobs(prefix=GCS_FOLDER_PATH)]
for file_path in file_paths:
    file_name = file_path.split('/')[-1]
    conn.cursor().execute(f'COPY INTO {table_name} FROM @{stage_name}/{file_path} FILE_FORMAT=(TYPE=CSV)')
