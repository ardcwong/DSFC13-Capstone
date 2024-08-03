import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
import base64
import json
from datetime import datetime

########################################################
# API KEYS and CREDENTIALS
########################################################
api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]


########################################################
# SUITABILITY
########################################################


# Define the questions
questions = [
    "What is your highest level of education completed?",
    "Do you have any prior experience in programming or data analysis? If yes, please describe.",
    "Do you prefer structured learning environments with a clear curriculum, or do you thrive in self-paced, unstructured settings?",
    "How many hours per week can you realistically dedicate to learning data science?",
    "What are your long-term career goals in the field of data science?"
]

# Streamlit app setup
st.title("Data Science Learning Path Classifier")
st.write("Please answer the following questions to determine your suitability for different learning paths in data science.")

# Google Sheets connection function
def google_connection(client):
    # Open the Google Sheet
    spreadsheet = client.open("Data Science Learning Path Classifier")
    return spreadsheet

# Function to write feedback and chat history to Google Sheet
def write_feedback_to_gsheet(spreadsheet, feedback, chat_history):
    sheet = spreadsheet.sheet1
    chat_history_json = json.dumps(chat_history)
    sheet.append_row([str(datetime.now()), feedback, chat_history_json])
    return sheet

# Initialize Google Sheets connection if not already in session state
if "spreadsheet_DSLPC" not in st.session_state:
    # Google Sheets setup using st.secrets
    credentials = st.secrets["gcp_service_account"]  # Make sure to add your credentials in Streamlit secrets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    st.session_state.spreadsheet_DSLPC = google_connection(client)




@st.fragment
def suitability():
    if 'classification' not in st.session_state:
        st.session_state.classification = []
    with st.container(height=400):
        # Initialize or retrieve session state
        if 'responses' not in st.session_state:
            st.session_state.responses = []
        if 'question_index' not in st.session_state:
            st.session_state.question_index = 0
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        

        # Initialize the first question in the chat history if not already done
        if st.session_state.question_index == 0 and not st.session_state.chat_history:
            first_question = questions[st.session_state.question_index]
            st.session_state.chat_history.append(("AI", first_question))

        # Display the entire chat history with user responses on the right
        for role, message in st.session_state.chat_history:
            st.chat_message(role).write(message)
            
    with st.container():
        # Function to display the current question and collect user response
        def display_question():
            if st.session_state.question_index < len(questions):
                current_question = questions[st.session_state.question_index]
                user_response = st.chat_input("Your response:")
                if user_response:
                    st.session_state.responses.append(user_response)
                    st.session_state.chat_history.append(("User", user_response))
                    st.session_state.question_index += 1
                    if st.session_state.question_index < len(questions):
                        next_question = questions[st.session_state.question_index]
                        st.session_state.chat_history.append(("AI", next_question))
                    st.rerun(scope="fragment")

        # Function to get classification from OpenAI
        def get_classification():
            questions_responses = ""
            for i, question in enumerate(questions):
                questions_responses += f"{i+1}. {question}\n   - Response: {st.session_state.responses[i]}\n"
            # If my responses is not enough for you to classify me, ask the me to press the reset button, otherwise, please describe my suitability for each and recommend the most suitable one for me.
            # Inform me that in case I want to change any of my responses only, I can press the reset button.
            
            prompt = f"""
            Check if my responses are related to the questions being asked.
            Classify my suitability for a data science bootcamp, self-learning, or a master's program based on my responses to the questions: {questions_responses}.

        
            """

            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that classifies education suitability and recommends the most suitable learning path. "},
                        {"role": "user", "content": prompt}
                    ]
                )
                classification = response.choices[0].message.content.strip()
                return classification
            except Exception as e:
                st.error(f"Error: {e}")
                return None

        # Main logic
        if st.session_state.question_index < len(questions):
            display_question()
        else:
            if st.session_state.responses and st.session_state.question_index == len(questions):
                classification = get_classification()
                
                if classification:
                    st.session_state.chat_history.append(("AI", classification))
                    st.session_state.question_index += 1
                    st.session_state.classification = classification
                    st.rerun()

   
             
    # Reset button
    col1, col2 = st.columns([10, 2])
    with col1:
        if st.session_state.classification:
            sentiment_mapping = [0,1]
            feedback = st.feedback("thumbs")        
            if feedback is not None:
                st.markdown(feedback)
                feedback_score = {sentiment_mapping[feedback]}
                st.markdown(f"You selected: {sentiment_mapping[feedback]}")
                sheet = write_feedback_to_gsheet(st.session_state.spreadsheet_DSLPC, feedback_score, st.session_state.chat_history)
                st.success("Thank you for your feedback!")
                st.session_state.classification = []
                st.rerun()   
        
    with col2:
        
        if st.button("Reset", use_container_width = True):
            st.session_state.responses = []
            st.session_state.question_index = 0
            st.session_state.chat_history = []
            st.session_state.classification = []
            st.rerun()   

    # st.dataframe(st.session_state.chat_history)

suitability()


# if st.session_state.classification:
#     feedback = st.feedback("thumbs")        
#     if feedback:
#         sheet = write_feedback_to_gsheet(st.session_state.spreadsheet_DSLPC, feedback, st.session_state.chat_history)
#         st.success("Thank you for your feedback!")
#         st.session_state.responses = []
#         st.session_state.question_index = 0
#         st.session_state.chat_history = []
#         st.session_state.classification = []
#         st.write(pd.DataFrame(sheet.get_all_records()))
#         st.rerun() 






# ##############################################
# @st.fragment
# def suitability():    
#     with st.container(height=500):
#             # Initialize or retrieve session state
#         if 'responses' not in st.session_state:
#             st.session_state.responses = []
#         if 'question_index' not in st.session_state:
#             st.session_state.question_index = 0
#         if 'chat_history' not in st.session_state:
#             st.session_state.chat_history = []
        
#         # # Display the entire chat history
#         # for role, message in st.session_state.chat_history:
#         #     st.chat_message(role).write(message)
#         # Display the entire chat history with user responses on the right
#         for role, message in st.session_state.chat_history:
#             st.chat_message(role).write(message)
                
#     with st.container(border = False):
#         # Function to display the current question and collect user response
#         def display_question():
#             if st.session_state.question_index < len(questions):
#                 current_question = questions[st.session_state.question_index]
#                 # st.chat_message("AI").write(current_question)
#                 st.session_state.chat_history.append(("AI", current_question))

                
#                 user_response = st.chat_input("Your response:")
#                 # st.rerun(scope="fragment")
#                 if user_response:
#                     st.session_state.responses.append(user_response)
                    
#                     st.session_state.chat_history.append(("User", user_response))
#                     st.session_state.question_index += 1
#                     st.rerun(scope="fragment")
    
#     # Function to get classification from OpenAI
#     def get_classification():
#         questions_responses = ""
#         for i, question in enumerate(questions):
#             questions_responses += f"{i+1}. {question}\n   - Response: {st.session_state.responses[i]}\n"
    
#         prompt = f"""
#         Classify the following person’s suitability for a data science bootcamp, self-learning, or a master's program based on their responses to the questions:
#         {questions_responses}
#         Suitability:
#         """
    
#         try:
#             response = openai.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant that classifies education suitability."},
#                     {"role": "user", "content": prompt}
#                 ]
#             )
#             classification = response.choices[0].message.content.strip()
#             return classification
#         except Exception as e:
#             st.error(f"Error: {e}")
#             return None
    
#     # Main logic
#     if st.session_state.question_index < len(questions):
#         display_question()
#     else:
#         if st.session_state.responses and st.session_state.question_index == len(questions):
#             classification = get_classification()
#             if classification:
#                 st.session_state.chat_history.append(("Suitability", classification))
#                 st.session_state.question_index += 1
#                 st.rerun(scope="fragment")
    
#             # with st.container(border=True):
#         #     suitability()    

# ############################
# # RUN SUITABILITY
# ############################
# suitability()

