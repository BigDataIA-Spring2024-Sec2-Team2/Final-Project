import streamlit as st
from streamlit_option_menu import option_menu
from components.user_profile import signup_and_preferences
from components.news_dashboard import news_nest_app, news_nest_top, search
from components.watch_news_dashboard import watch_news
from components.google_search import google_search

def tabs():
  options = ["News Dashboard", "Watch News","Google Search","User Profile"]
  icons = ['cloud-upload-fill','gear-fill', 'clipboard-data-fill','clipboard-data-fill'] 

  nav_menu = option_menu(None, options, 
    icons=icons, 
    menu_icon="cast", 
    key='nav_menu',
    default_index=0, 
    orientation="horizontal"
  )

  nav_menu

  if st.session_state["nav_menu"] == "News Dashboard" or st.session_state["nav_menu"]==None:
    search()
    news_nest_top()
    news_nest_app()
  elif st.session_state["nav_menu"] == "Watch News":
    watch_news()
  elif st.session_state["nav_menu"] == "Google Search":
    google_search()
  elif st.session_state["nav_menu"] == "User Profile":
    signup_and_preferences()
