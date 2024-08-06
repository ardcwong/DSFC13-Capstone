import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
import base64
import json
from datetime import datetime
import pytz
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


# Define the timezone for the Philippines
philippines_timezone = pytz.timezone('Asia/Manila')

########################################################
# API KEYS and CREDENTIALS
########################################################
api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]

if "stop" not in st.session_state:
    st.session_state.stop = True
    nltk.download('stopwords')

def remove_stopwords(response):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(response)
    filtered_response = [word for word in word_tokens if word.lower() not in stop_words]
    return ' '.join(filtered_response)



########################################################
# SUITABILITY
########################################################


# Define the questions
questions = [
    "What is your highest level of education?",
    "Do you have a background in mathematics, statistics, or computer science?",
    "Do you have any work experience related to data science or any technical field? If so, please describe your role(s).",
    "How many years of professional experience do you have?",
    "Are you familiar with any programming languages? If yes, which ones?",
    "Do you have any experience with data analysis tools or software (e.g., Python, R, SQL, Excel)?",
    "Have you worked on any data science projects or competitions?",
    "Do you have experience with machine learning algorithms?",
    "Do you prefer structured learning with a defined curriculum or self-paced learning?",
    "How much time can you dedicate to studying each week?",
    "What type of learner are you (visual, auditory, reading/writing, kinesthetic)?",
    "What are your short-term and long-term career goals in data science?",
    "Are you looking to make a career switch to data science, or do you want to enhance your current role with data science skills?",
    "Are you willing to invest in a master's degree, which typically requires a significant financial and time commitment?",
    "Do you need to balance your studies with work or other commitments?",
    "Do you prefer learning in a classroom setting, online, or a hybrid approach?",
    "Are there any specific areas of data science you are particularly interested in (e.g., machine learning, data visualization, big data)?",
    "Have you ever attended any data science workshops or courses? If so, please describe them.",
    "How do you handle complex problem-solving and analytical tasks?",
    "Do you have a network or community for support in your learning journey?"

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
    # chat_history_json = json.dumps(chat_history)
    # chat_history_df = pd.DataFrame([chat_history])
    # chat_history_list = chat_history_df.values.tolist()[0]
    # flattened_chat_history = [item for sublist in chat_history for item in sublist]
    chat_history_list = pd.DataFrame(chat_history)[[1]].T.values.flatten().tolist()
    # chat_history_list = chat_history.values.flatten().tolist()
    # chat_history_json = chat_history.iloc[0].to_json(orient="records")
    sheet.append_row([str(datetime.now(philippines_timezone)), feedback] + chat_history_list)
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
    with st.container(height=450, border=None):
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

            # Apply the stopwords removal to the responses
            # filtered_responses = [remove_stopwords(response) for response in st.session_state.responses]

            questions_responses = ""
            for i, question in enumerate(questions):
                questions_responses += f"{i+1}. {question}\n - Responses: {st.session_state.responses[i]}\n"


            
            # If my responses is not enough for you to classify me, ask the me to press the reset button, otherwise, please describe my suitability for each and recommend the most suitable one for me.
            # Inform me that in case I want to change any of my responses only, I can press the reset button.
            # Classify my suitability for a data science bootcamp, self-learning, or a master's program based on my responses to the questions: {questions_responses}.
            
            # prompt = f"""
            # Classify my suitability for a data science bootcamp, self-learning, and a master’s program based on my responses to the question:{questions_responses}.
            # Suitability:
            #     1. Bootcamp: 
            #     2. Self-Learning:
            #     3. Master's Program:
            
            # Overall Recommendation: 
            
            # """

            # prompt = f"""
            # Based on my responses to the questions listed below, please evaluate whether the responses are relevant to the questions asked. Subsequently, classify my suitability for the following data science learning pathways: Bootcamp, Self-Learning, and a Master’s Program.
            
            # Questions and Responses:
            # {questions_responses}
            
            # Suitability:
            # 1. Bootcamp: 
            # 2. Self-Learning:
            # 3. Master's Program:
            
            # Finally, provide an overall recommendation on the most suitable learning pathway for me, considering my responses:
            # Overall Recommendation:
            # """
             # Classify my suitability for a data science bootcamp, self-learning, and a master’s program based on my responses to the question:{questions_responses}.
            prompt = f"""
            Classify and explain my suitability for the following data science learning pathway: Eskwelabs' bootcamp, self-learning, or a master's degree, and recommend the most suitable learning pathway based on the {questions_responses} provided. 
           
            
            *1. Eskwelabs Bootcamp:* Suitability and Explanation
            *2. Self-Learning:* Suitability and Explanation
            *3. Master's Program:* Suitability and Explanation

            
            Overall Recommendation:
            """


# You are a helpful assistant that classifies education suitability and recommends the most suitable learning path. "},
            # Before you classify suitability and recommend the most suitable learning path, check first if every response is related to the question being asked.
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                    	{"role": "system", "content": f"You are an expert education bot designed to classify the suitability either Highly Suitable, Moderately Suitable, Slightly Suitable, or Not Suitable for each learning pathway of the user, and recommends the most suitable learning pathway for users in their data science journey. Based on the user's responses to a series of questions, you will classify and explain the suitability of the user to each of the following learning path: Eskwelabs bootcamp, self-learning, or a master's degree., and you will recommend the most suitable learning path."},
                        {"role": "user", "content": prompt},
                        # {"role": "assistant", "content": prompt}
                    ]
                    #temperature = 0.7 You are an expert in classifying user's suitability to data science learning pathways (e.g., as bootcamp, self-learning, or a master’s program), and in recommending the most suitable learning path. Before you classify suitability and recommend the most suitable learning path, check first if every response is related to the question being asked.
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

   

    col1, col2 = st.columns([10, 2])

        
    with col2:
        
        if st.button("Reset", use_container_width = True, help = "To update your answer, please press the RESET button to start over and answer the questions again. Feel free to make any necessary improvements or corrections to enhance your response."):
            st.session_state.responses = []
            st.session_state.question_index = 0
            st.session_state.chat_history = []
            st.session_state.classification = []
            st.session_state.feedback_up = []
            st.session_state.feedback_down = []
            st.rerun()   



suitability()

def program_info_page_switch():
    if st.button("Program Information"):  
        return st.switch_page("Program_Information/pi_app.py")
        
if st.session_state.classification:
    # Display the entire chat history with user responses on the right
    # for role, message in st.session_state.chat_history:
    st.chat_message(st.session_state.chat_history[-1][0]).write(st.session_state.chat_history[-1][1])
    # st.write(st.session_state.chat_history)
    program_info_page_switch()
    
    if 'feedback_up' not in st.session_state:
        st.session_state.feedback_up = []
    if 'feedback_down' not in st.session_state:
        st.session_state.feedback_down = []

    
    if st.session_state.feedback_up == 1:
        st.markdown("<h6 style='text-align: center;'>.&emsp;.&emsp;.&emsp;.&emsp;.</h6>", unsafe_allow_html=True)
        st.markdown("<h6 style='text-align: center;'>You selected 👍🏻 Thanks for your feedback!</h6>", unsafe_allow_html=True)
        st.markdown("<h6 style='text-align: center;'>.&emsp;.&emsp;.&emsp;.&emsp;.</h6>", unsafe_allow_html=True)

    elif st.session_state.feedback_up == 0:
        st.markdown("<h6 style='text-align: center;'>.&emsp;.&emsp;.&emsp;.&emsp;.</h6>", unsafe_allow_html=True)
        st.markdown("<h6 style='text-align: center;'>You selected 👎🏻 Thanks for your feedback!</h6>", unsafe_allow_html=True)
        st.markdown("<h6 style='text-align: center;'>.&emsp;.&emsp;.&emsp;.&emsp;.</h6>", unsafe_allow_html=True)
    else:
        st.markdown("<h6 style='text-align: center;'>.&emsp;.&emsp;.&emsp;.&emsp;.</h6>", unsafe_allow_html=True)
        st.markdown("<h6 style='text-align: center;'>Could you please give a thumbs up if you find these recommendations specific and tailored to your responses, or a thumbs down if you do not?</h6>", unsafe_allow_html=True)
        f1,f2,f3,f4 = st.columns([4,1,1,4])
        
    
    
        if f2.button("👍🏻", use_container_width = True, help = "This response helpful"):
            feedback_score = 1
            sheet = write_feedback_to_gsheet(st.session_state.spreadsheet_DSLPC, feedback_score, st.session_state.chat_history)
            st.session_state.feedback_up = feedback_score
            st.rerun() 
        elif f3.button("👎🏻", use_container_width = True, help = "This response unhelpful"):
            feedback_score = 0
            sheet = write_feedback_to_gsheet(st.session_state.spreadsheet_DSLPC, feedback_score, st.session_state.chat_history)
            st.session_state.feedback_down = feedback_score
            st.rerun() 
        st.markdown("<h6 style='text-align: center;'>.&emsp;.&emsp;.&emsp;.&emsp;.</h6>", unsafe_allow_html=True)
        
