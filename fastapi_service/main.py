from fastapi import FastAPI
from routers import news_loader, profile, search_db

app = FastAPI()

app.include_router(search_db.router, tags=['search'], prefix='/search')
app.include_router(news_loader.router, tags=['news'], prefix='/news')
app.include_router(profile.router, tags=['profile'], prefix='/profile')