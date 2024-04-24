from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import os

from dotenv import load_dotenv
import pymongo
import certifi 

load_dotenv()

class signup_data(BaseModel):
  email: str
  username: str
  password: str
  interests: str
  notify_about: str

class login_data(BaseModel):
  email: str
  password: str

app = FastAPI()

# JWT config
SECRET_KEY = os.getenv('SECRET_KEY', "your_secret_key")
ALGORITHM = os.getenv('ALGORITHM', "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60))

# Mongo config
mongo_url = os.getenv('mongo_url')
db_name = os.getenv('db_name')
collection_name = os.getenv('collection_name')

# oauth2 scheme
tokenUrl = os.getenv('TOKEN_URL', "token")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl)

# password encryption
schemes = os.getenv('SCHEMES', "bcrypt")
deprecated = os.getenv('DEPRECATED', "auto")
pwd_context = CryptContext(schemes=schemes, deprecated=deprecated)

def get_mongo_clien():
    try:
        connection = pymongo.MongoClient(mongo_url,tlsCAFile=certifi.where())
        return connection
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise
    

def verify_password(plain_password, hashed_password):
  ''' verify the passowrd for login '''
  return pwd_context.verify(plain_password, hashed_password)

def get_user(email: str):
  ''' get user data from db with email '''
  client = get_mongo_clien()
  db = client[db_name]
  collection = db[collection_name]
  result = collection.find_one({"email": email})
  client.close()
  return result

def create_user(email: str, password: str, username: str, interests:str, notify_about: str):
  ''' add new user in db '''
  client = get_mongo_clien()
  db = client[db_name]
  collection = db[collection_name]
  
  hashed_password = pwd_context.hash(password)

  news_categories = {
    "Politics": 0,
    "Business and Finance": 0,
    "Technology": 0,
    "Science": 0,
    "Entertainment": 0,
    "Sports": 0,
    "Lifestyle": 0,
    "Others": 0
  }

  views = news_categories

  interests_list = [interest.strip().capitalize() for interest in interests.lower().split(',')]

  for interest in interests_list:
      found = False
      for category in news_categories:
          if interest.lower() == category.lower():
              news_categories[category] = 1
              found = True
              break
      if not found:
          news_categories["Others"] = 1
  
  notify_about = notify_about.split(", ")

  document = {
    "email": email,
    "username": username,
    "password": hashed_password,
    "interests": news_categories,
    "notify_about": notify_about,
    "views": views

  }
  collection.insert_one(document)
  client.close()
  print("Success in insertion of data")
  return

def authenticate_user(email: str, password: str):
  ''' Authenticate user Login '''
  user = get_user(email)
  if not user:
    return False
  if not verify_password(password, user["password"]):
    return False
  return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  ''' Create access token '''
  to_encode = data.copy()
  if expires_delta:
      expire = datetime.utcnow() + expires_delta
  else:
      expire = datetime.utcnow() + timedelta(minutes=60)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

@app.post("/signup")
async def register(payload: signup_data):
  ''' Endpoint Sign Up new user '''
  email = payload.email
  password = payload.password
  username = payload.username
  interests = payload.interests
  notify_about = payload.notify_about

  if get_user(email):
    raise HTTPException(status_code=400, detail="Email already registered")
  
  create_user(email, password, username, interests, notify_about)
  return {"message": "User registered successfully"}

@app.post("/login")
async def login_for_access_token(payload: login_data):
  ''' Endpoint Login Existing user '''
  email = payload.email
  password = payload.password
  user = authenticate_user(email, password)
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect email or password",
      headers={"WWW-Authenticate": "Bearer"},
    )
  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
    data={"sub": user["email"]}, expires_delta=access_token_expires
  )
  return {"access_token": access_token, "token_type": "bearer"}

