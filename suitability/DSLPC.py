import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
import base64


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


@st.fragment
def suitability():    
    with st.container(height=500):
            # Initialize or retrieve session state
        if 'responses' not in st.session_state:
            st.session_state.responses = []
        if 'question_index' not in st.session_state:
            st.session_state.question_index = 0
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # # Display the entire chat history
        # for role, message in st.session_state.chat_history:
        #     st.chat_message(role).write(message)
        # Display the entire chat history with user responses on the right
        for role, message in st.session_state.chat_history:
            st.chat_message(role).write(message)
                
    with st.container(border = False):
        # Function to display the current question and collect user response
        def display_question():
            if st.session_state.question_index < len(questions):
                current_question = questions[st.session_state.question_index]
                # st.chat_message("AI").write(current_question)
                st.session_state.chat_history.append(("AI", current_question))
                user_response = st.chat_input("Your response:")
                st.rerun(scope="fragment")
                if user_response:
                    st.session_state.responses.append(user_response)
                    
                    st.session_state.chat_history.append(("User", user_response))
                    st.session_state.question_index += 1
                    # st.rerun(scope="fragment")
    
    # Function to get classification from OpenAI
    def get_classification():
        questions_responses = ""
        for i, question in enumerate(questions):
            questions_responses += f"{i+1}. {question}\n   - Response: {st.session_state.responses[i]}\n"
    
        prompt = f"""
        Classify the following person’s suitability for a data science bootcamp, self-learning, or a master's program based on their responses to the questions:
        {questions_responses}
        Suitability:
        """
    
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies education suitability."},
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
                st.session_state.chat_history.append(("Suitability", classification))
                st.session_state.question_index += 1
                st.rerun(scope="fragment")
    
            # with st.container(border=True):
        #     suitability()    

############################
# RUN SUITABILITY
############################
suitability()

