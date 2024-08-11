import streamlit as st
import openai
from openai import OpenAI
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from xhtml2pdf import pisa
from io import BytesIO
########################################################
# API KEYS and CREDENTIALS
########################################################
api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
client = gspread.authorize(creds)
# Google Sheets connection function
def google_connection_gsheet_courseoutline_ops(client):
    # Open the Google Sheet
    spreadsheet = client.open("Data Science Fellowship Curriculum")
    return spreadsheet

########################################################
# ACCESS Data Science Fellowship Curriculum GSHEET
########################################################
if "spreadsheet_courseoutline_ops" not in st.session_state:
    st.session_state.spreadsheet_courseoutline_ops = google_connection_gsheet_courseoutline_ops(client)


# Load CSV file containing the cohort's main topics and subtopics
def load_and_generate_course_outline(spreadsheet):
    worksheet = spreadsheet.worksheet("Data Science Fellowship Cohort")
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
  
  # df = pd.read_csv(filepath)
    course_outline = {}
    
    for _, row in df.iterrows():
        sprint = row['Sprint Number']
        main_topic = row['Main Topic']
        subtopic = row['Sub-Topics']
        
        if sprint not in course_outline:
            course_outline[sprint] = {}
        if main_topic not in course_outline[sprint]:
            course_outline[sprint][main_topic] = []
        course_outline[sprint][main_topic].append(subtopic)
    
    return course_outline

# Function to retrieve and generates additional information about specific course topics
def generate_additional_content(query, collection):
    retrieved_docs = retrieve_documents(query, collection)
    context = ' '.join([doc['text'] for doc in retrieved_docs])
    
    prompt = f"Based on the following information:\n\n{context}\n\nAnswer the following question:\n{query}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that provides detailed educational content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content.strip()

# Function to enhance course outline 
def enhance_course_outline(course_outline, collection):
    enhanced_outline = {}
    for sprint, topics in course_outline.items():
        enhanced_outline[sprint] = {}
        for main_topic, subtopics in topics.items():
            enhanced_outline[sprint][main_topic] = {}
            for subtopic in subtopics:
                query = f"Provide detailed information and educational content about {subtopic} in the context of {main_topic}."
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant that provides detailed educational content."},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=500
                )
                additional_content = response.choices[0].message.content.strip()
                enhanced_outline[sprint][main_topic][subtopic] = additional_content
    return enhanced_outline


# Load and generate the course outline from the CSV file
course_outline = load_and_generate_course_outline(st.session_state.spreadsheet_courseoutline_ops)


# Streamlit UI
st.title("Sprint Navigator")

st.markdown("""
The Sprint Navigator is a meticulously crafted course outline, designed to provide a clear and organized view of the program's main 
topics and sub-topics, divided into four distinct Sprints. This Navigator acts as both a strategic planning tool and a detailed 
guide for fellows, helping them steer through their learning journey with confidence.
""")

selected_sprints = {}

for sprint in course_outline.keys():
    if f"outline_{sprint}" not in st.session_state:
        # Enhance only if it hasn't been done before
        st.session_state[f"outline_{sprint}"] = enhance_course_outline({sprint: course_outline[sprint]}, None)
    selected_sprints[sprint] = st.session_state[f"outline_{sprint}"]

# Display the enhanced course outline with detailed content
if selected_sprints:
    for sprint, topics in selected_sprints.items():
        with st.expander(f"{sprint}", expanded=True):
            for main_topic, subtopics in topics[sprint].items():
                st.write(f"Main Topic: {main_topic}")
                for subtopic, content in subtopics.items():
                    st.write(f"  Subtopic: {subtopic}")
                    st.write(f"    Content:\n{content}\n")

st.write(st.session_state["outline_Sprint 3"])

# # Dynamic checkbox generation with session state
# selected_sprints = {}

# for sprint in course_outline.keys():
#     if st.checkbox(sprint, key=f"checkbox_{sprint}"):
#         if f"outline_{sprint}" not in st.session_state:
#             # Enhance only if it hasn't been done before
#             st.session_state[f"outline_{sprint}"] = enhance_course_outline({sprint: course_outline[sprint]}, None)
#         selected_sprints[sprint] = st.session_state[f"outline_{sprint}"]

# # Display the enhanced course outline with detailed content
# if selected_sprints:
#     for sprint, topics in selected_sprints.items():
#         with st.expander(f"{sprint}", expanded=True):
#             for main_topic, subtopics in topics[sprint].items():
#                 st.write(f"Main Topic: {main_topic}")
#                 for subtopic, content in subtopics.items():
#                     st.write(f"  Subtopic: {subtopic}")
#                     st.write(f"    Content:\n{content}\n")

