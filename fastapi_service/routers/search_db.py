from fastapi import FastAPI, APIRouter, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import pandas as pd
import jwt
import os
from snowflake_connector import SnowflakeConnector
from mongo_connector import MongoDBManager

load_dotenv()

router = APIRouter()
snowflake_client = SnowflakeConnector()
mongo_manager = MongoDBManager()

# JWT config
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

# oauth2 scheme
tokenUrl = os.getenv('TOKEN_URL')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl)

# password encryption
schemes = os.getenv('SCHEMES')
deprecated = os.getenv('DEPRECATED')
pwd_context = CryptContext(schemes=schemes, deprecated=deprecated)


def data_retriever(to_find):

    if to_find:
        to_find = to_find.lower().split()
        where_clause = f"WHERE TITLE LIKE '%{to_find[0]}%'"

        for i in range(1,len(to_find)):
            statement = f"OR TITLE LIKE '%{to_find[i]}%'"
            where_clause+=statement

    else:
        where_clause = ""

    sql_query = f"""
        SELECT *
        FROM ARTICLES
        {where_clause}
        ORDER BY PUBLISH_DATE DESC;
    """
    result = snowflake_client.execute_query(sql_query)
    
    return(result)


@router.get('/db')
async def searcher(to_search:str, authorization: str = Header(None)):

    if authorization is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = parts[1]
    try:
        token_decode = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM, ])
        email: str = token_decode.get("sub")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Token has expired")
    
    result = data_retriever(to_search)

    return {"result": result}
    

    
