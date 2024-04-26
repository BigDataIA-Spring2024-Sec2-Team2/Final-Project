import streamlit as st
from streamlit_option_menu import option_menu
from components.user_profile import signup_and_preferences
from components.news_dashboard import news_nest_app
from components.watch_news_dashboard import watch_news
from components.google_search import google_search

def tabs():
  st.title("Welcome to NewsNest")
  options = ["News Dashboard", "Watch News","Google Search","User Profile"]
  icons = ['cloud-upload-fill','gear-fill', 'clipboard-data-fill','clipboard-data-fill'] 

  login_menu = option_menu(None, options, 
    icons=icons, 
    menu_icon="cast", 
    key='nav_menu',
    default_index=0, 
    orientation="horizontal"
  )

  login_menu

  backend_video_links = [
    "https://abcnews.go.com/US/video/full-pink-moon-revealed-timelapse-footage-109594961"
  ]

  if st.session_state["nav_menu"] == "News Dashboard":
    news_nest_app()
  elif st.session_state["nav_menu"] == "Watch News":
    watch_news(backend_video_links)
  elif st.session_state["nav_menu"] == "Google Search":
    google_search()
  elif st.session_state["nav_menu"] == "User Profile":
    signup_and_preferences()
  else:
    news_nest_app()