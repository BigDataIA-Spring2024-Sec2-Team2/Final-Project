from fastapi import FastAPI
from routers import custom_search, news_loader, profile

app = FastAPI()

# app.include_router(custom_search.router, tags=['search'], prefix='/search')
app.include_router(news_loader.router, tags=['news'], prefix='/news')
app.include_router(profile.router, tags=['profile'], prefix='/profile')