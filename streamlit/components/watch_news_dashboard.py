import streamlit as st
from streamlit.components.v1 import iframe

def watch_news(video_links=None):
    st.subheader(":red[Watch Latest News Shorts]")


    if video_links:
        for i, link in enumerate(video_links):
            st.write(f"## Video {i+1}")
            st.markdown(f"### Link to News: {i+1}")
            iframe(link, width=640, height=360)
    else:
        st.write(":red[No video links available.]")


