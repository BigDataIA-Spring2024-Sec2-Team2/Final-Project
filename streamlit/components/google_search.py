import streamlit as st
import requests
import configparser

config = configparser.ConfigParser()
config.read('./configuration.properties')
base_url = config['APIs']['base_url_auth']

def google_search():
    
    
    st.subheader(":red[Read latest news on google...]")
    
    with st.form(key='search', clear_on_submit=True):
        google_search = st.text_input(':blue[Search on google news:]', placeholder='Search on google news:')
        sub = st.form_submit_button('Search')
        
        if sub:
            url = base_url + '/search/serp?to_search=' + google_search
            access_token = st.session_state["access_token"]
            token_type = st.session_state["token_type"]
            # Making the POST request
            headers = {
                "Authorization": "{} {}".format(token_type, access_token),
                'Content-Type': 'application/json',
            }
            response = requests.get(url, headers=headers)
            
            news_data = []
            for result in response['result']:
                formatted_result = {}
                formatted_result['Title'] = result.get('TITLE',"")
                formatted_result['Image_url'] = result.get('IMAGE_URL',"")
                formatted_result['Source'] = result.get('SOURCE',"")
                formatted_result['Publish_Date'] = result.get('PUBLISH_DATE',"")
                news_data.append(formatted_result)
                
            
            def display_popup_card(news_item):
                st.write("### " + news_item["Title"])
                st.image(news_item["Image"], use_column_width=True)
                st.write(news_item["Source"])
                st.write(news_item["Publish_date"])

                # Add a close button
                if st.button("Close"):
                    st.write("Popup closed.")

            col_count = 4
            for i in range(0, len(news_data), col_count):
                cols = st.columns(col_count)
                for j in range(col_count):
                    if i + j < len(news_data):
                        with cols[j]:
                            st.image(news_data[i + j]["Image_url"], use_column_width=True)
                            if st.button(news_data[i + j]["Title"]):
                                selected_news = news_data[i + j]
                                st.write("---")
                                display_popup_card(selected_news)
    