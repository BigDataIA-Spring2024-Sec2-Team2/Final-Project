import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()
    
# Function to get Snowflake connection
def get_snowflake_connection():
    snowflake_config = {
        "user": os.getenv('sf_user'),
        "password": os.getenv('sf_password'),
        "account": os.getenv('sf_account'),
        "database": os.getenv('sf_database'),
        "schema": os.getenv('sf_schema')
    }
    return snowflake.connector.connect(**snowflake_config)

def execute_query(connection, query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()