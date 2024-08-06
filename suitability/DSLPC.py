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
    # "Do you prefer structured learning with a defined curriculum or self-paced learning?",
    # "How much time can you dedicate to studying each week?",
    # "What type of learner are you (visual, auditory, reading/writing, kinesthetic)?",
    # "What are your short-term and long-term career goals in data science?",
    # "Are you looking to make a career switch to data science, or do you want to enhance your current role with data science skills?",
    # "Are you willing to invest in a master's degree, which typically requires a significant financial and time commitment?",
    # "Do you need to balance your studies with work or other commitments?",
    # "Do you prefer learning in a classroom setting, online, or a hybrid approach?",
    # "Are there any specific areas of data science you are particularly interested in (e.g., machine learning, data visualization, big data)?",
    # "Have you ever attended any data science workshops or courses? If so, please describe them.",
    # "How do you handle complex problem-solving and analytical tasks?",
    # "Do you have a network or community for support in your learning journey?"

]


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

def program_info_page_switch():
    if st.button("Program Information",type="primary", use_container_width = True, help = "Go to Program Information page"):  
        return st.switch_page("Program_Information/pi_app.py")


@st.fragment
def suitability():
    if 'classification' not in st.session_state:
        st.session_state.classification = []
    
        # Initialize or retrieve session state
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        
    if st.session_state.classification:
        # Display the entire chat history with user responses on the right
        # for role, message in st.session_state.chat_history:
        tab1, tab2 = st.tabs(["Suitability and Recommendation", "Your Responses"])
        with tab2:
            # Display the entire chat history with user responses on the right
            for role, message in st.session_state.chat_history:
                st.chat_message(role).write(message)
       
        with tab1:
            colSO1, colSO2 = st.columns([7,3])
            with colSO2:
                if st.button("Start Over", type="primary", use_container_width = True, help = "To update your answer, please press the RESET button to start over and answer the questions again. Feel free to make any necessary improvements or corrections to enhance your response."):
                    st.session_state.responses = []
                    st.session_state.question_index = 0
                    st.session_state.chat_history = []
                    st.session_state.classification = []
                    st.session_state.feedback_up = []
                    st.session_state.feedback_down = []
                    st.session_state.BeginAssessment = True
                    st.rerun()   

            
            st.chat_message(st.session_state.chat_history[-1][0]).write(st.session_state.chat_history[-1][1])
            # st.write(st.session_state.chat_history)
        
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
        
            col1, col2, col3 = st.columns([1,6,1])
            with col2:
                with st.container():
                    st.markdown("<h6 style='text-align: center;color: #e76f51;'>Data Science Fellowship (DSF) Program by Eskwelabs</h6>", unsafe_allow_html=True)
                    st.markdown("""<div style='text-align: center;'>The Data Science Fellowship (DSF) Program by Eskwelabs offers a comprehensive curriculum designed to equip 
                    participants with practical skills through hands-on projects and sprints. The program includes projects on customer segmentation, 
                    credit fraud detection, recommender engines, and generative AI, each aiming to provide actionable insights and enhance strategic 
                    decision-making. Various payment options are available, including early bird discounts, installment plans, and study-now-pay-later 
                    schemes. Interested individuals can apply online, explore past capstone projects, and consult with admissions advisors for 
                    personalized guidance. Additional resources and details about the program, including tuition fees and refund policies, 
                    are accessible via the Eskwelabs website or interactive with our Program Information Chatbot for more information by clicking this "Program Information" button.</div>
                    """, unsafe_allow_html=True)
                    st.markdown("")
                    cola, colb, colc = st.columns([1,1,1,])
                    with colb:
                        program_info_page_switch()

    
    
    
    else:
    
    
    
    
        with st.container(height=450, border=None):

              
    
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
            
            if st.button("Start Over", type="primary", use_container_width = True, help = "To update your answer, please press the RESET button to start over and answer the questions again. Feel free to make any necessary improvements or corrections to enhance your response."):
                st.session_state.responses = []
                st.session_state.question_index = 0
                st.session_state.chat_history = []
                st.session_state.classification = []
                st.session_state.feedback_up = []
                st.session_state.feedback_down = []
                st.session_state.BeginAssessment = True
                st.rerun()   



st.title("Data Science Learning Path Classifier")
# Streamlit app setup
if 'BeginAssessment' not in st.session_state:
    st.session_state.BeginAssessment = True


col_main1, col_main2 = st.columns([1,2])
with col_main1:
    with st.expander("**Our Bot**", expanded=st.session_state.BeginAssessment):
        st.write("Are you unsure about the best way to pursue your data science journey? Our intelligent classifier bot is here to help! By answering a few simple questions about your background, preferences, and goals, our bot will recommend the most suitable learning pathway for you.")

with col_main2:
    with st.expander("**How it works**", expanded=st.session_state.BeginAssessment):
        st.markdown("""
        1. Answer Questions: *Provide responses to a series of questions about your current experience, learning preferences, time commitment, and budget.*<br>
        2. Get Classified: *Based on your answers, our classifier bot will evaluate and determine the most appropriate learning pathway for you:* 
        :gray-background[**Eskwelabs' Bootcamp**], :gray-background[**Self-Learning**], :gray-background[**Master's Degree**]""", unsafe_allow_html=True)

if st.session_state.BeginAssessment == True:    
    with st.container(height=450, border=None):
        s1, s2, s3 = st.columns([1,8,1])
        with s2:
            st.markdown(f"<h2 style='text-align: center;'>Start Your Journey</h2>", unsafe_allow_html=True)
            st.markdown("""<h5 style='text-align: center;color: #e76f51;'><b><i>Simply click "Begin Assessment" </b></i><i>
            and follow the prompts to receive your personalized learning pathway recommendation. Empower your data science career with the right guidance tailored to your needs!.</h5>""", unsafe_allow_html=True)
            cs1,cs2,cs3 = st.columns([1,1,1])
            with cs2:
                if st.button("Begin Assessment", type="primary", use_container_width = True):
                    st.session_state.BeginAssessment = False
                    # st.rerun()
                    

else: 
    # st.session_state.BeginAssessment == False:
    suitability()

        







       
