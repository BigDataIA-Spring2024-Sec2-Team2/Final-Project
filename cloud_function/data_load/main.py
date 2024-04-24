import functions_framework
import os
import snowflake.connector


@functions_framework.http
def clean_data(request):
    ''' HTTP Cloud Function.
    read file from sourde bucket clean the data and load the clean data into destination bucket
    '''
    request_json = request.get_json(silent=True)
    request_args = request.args
    if request_json and 'file_name' in request_json:
        file_name = request_json['file_name']
    elif request_args and 'file_name' in request_args:
        file_name = request_json['file_name']
    else:
        file_name = None

    if file_name is None:
        return "Fail"

    SNOWFLAKE_ACCOUNT = os.environ.get('SNOWFLAKE_ACCOUNT')
    SNOWFLAKE_USER = os.environ.get('SNOWFLAKE_USER')
    SNOWFLAKE_PASSWORD = os.environ.get('SNOWFLAKE_PASSWORD')
    SNOWFLAKE_DATABASE = os.environ.get('SNOWFLAKE_DATABASE')
    SNOWFLAKE_SCHEMA = os.environ.get('SNOWFLAKE_SCHEMA')

    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    try:
        cursor = conn.cursor()
        cursor.execute(f"COPY INTO watch FROM '@stage_gcs_bucket_keyword/{file_name}' FILE_FORMAT = (FORMAT_NAME = 'news_ff') ON_ERROR = 'CONTINUE'")
        cursor.close()

        return "Success"
        
    except Exception as e:
        print(e)
        return "Fail"


