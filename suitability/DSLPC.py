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

# if "stop" not in st.session_state:
#     st.session_state.stop = True
#     nltk.download('stopwords')
#### USER AVATAR AND RESPONSE
@st.cache_data
def user_avatar_lpc():
  # Load the image and convert it to base64
  with open('data/avatar_user.png', 'rb') as image_file_user:
    encoded_string_user = base64.b64encode(image_file_user.read()).decode()
  # Base64 encoded image string from the previous step
  avatar_base64_user = encoded_string_user  # This is the base64 string you got earlier
  
  # Construct the base64 image string for use in HTML
  avatar_url_user = f'data:image/png;base64,{avatar_base64_user}'
  return avatar_url_user

avatar_url_user = user_avatar_lpc()

def show_user_answer_lpc(message_text,avatar_url_user):
  # Markdown to replicate the chat message
  # avatar_url = "https://avatars.githubusercontent.com/u/45109972?s=40&v=4"  # Replace this with any avatar URL or a local file path
  

  st.markdown(f"""
  <div style='display: flex; align-items: flex-start; padding: 10px; justify-content: flex-end;'>
      <div style='background-color: #F7F9FA; padding: 10px 15px; border-radius: 10px; margin-right: 10px; display: inline-block; text-align: right; max-width: 60%;'>
          <span style='font-size: 16px;'>{message_text}</span>
      </div>
      <div style='flex-shrink: 0;'>
          <img src='{avatar_url_user}' alt='avatar' style='width: 40px; height: 40px; border-radius: 50%;'>
      </div>
  </div>
  """, unsafe_allow_html=True)

#### AI AVATAR AND RESPONSE
@st.cache_data
def ai_avatar_lpc():
  # Load the image and convert it to base64
  with open('data/avatar_ai.png', 'rb') as image_file_lpc:
    encoded_string_lpc = base64.b64encode(image_file_lpc.read()).decode()
  # Base64 encoded image string from the previous step
  avatar_base64_lpc = encoded_string_lpc  # This is the base64 string you got earlier
  
  # Construct the base64 image string for use in HTML
  avatar_lpc = f'data:image/png;base64,{avatar_base64_lpc}'
  return avatar_lpc

avatar_lpc = ai_avatar_lpc()

def show_ai_response_lpc(message_text,avatar_lpc):
  # Markdown to replicate the chat message
  # avatar_url = "https://avatars.githubusercontent.com/u/45109972?s=40&v=4"  # Replace this with any avatar URL or a local file path
  

  st.markdown(f"""
  <div style='display: flex; align-items: flex-start; padding: 10px; justify-content: flex;'>
      <div style='flex-shrink: 0;'>
          <img src='{avatar_lpc}' alt='avatar' style='width: 40px; height: 40px; border-radius: 50%;'>
      </div>
      <div style='background-color: #FCFCFC; padding: 10px 15px; border-radius: 10px; margin-left: 10px; display: inline-block; text-align: left; max-width: 85%;'>
          <span style='font-size: 16px;'>{message_text}</span>
      </div>

  </div>
  """, unsafe_allow_html=True)

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
    "Do you have a background in mathematics, statistics, or computer science? If so, could you share about your experience in any of the these?",
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

            # for role, message in st.session_state.chat_history:
            #     if st.session_state.chat_history
                
            for role, message in st.session_state.chat_history:
                if role == "User":
                    show_user_answer_lpc(message,avatar_url_user)
                elif role == "AI":
                    show_ai_response_lpc(message,avatar_lpc)
            
            
       
        with tab1:


            
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
                    st.markdown("""<div style='text-align: center;'>This program offers a comprehensive curriculum designed to equip 
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
                if role == "User":
                    show_user_answer_lpc(message,avatar_url_user)
                elif role == "AI":
                    show_ai_response_lpc(message,avatar_lpc)
            
           
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
                    # Define the system message with the summarized information
                    system_message = """
                    You are an expert education bot designed to classify the suitability either Highly Suitable, Moderately Suitable, Slightly Suitable, or Not Suitable for each learning pathway of the user, 
                    and recommends the most suitable learning pathway for users in their data science journey. Based on the user's responses to a series of questions, you will classify and explain the suitability 
                    of the user to each of the following learning path: Eskwelabs bootcamp, self-learning, or a master's degree., and you will recommend the most suitable learning path.
                    
                    Consider the following details in your responses:
                    
                    - **Prerequisites:** Basic to intermediate Python skills, basic statistics and linear algebra, strong analytical and problem-solving abilities.
                    - **Program Structure:** Duration of a few months, full-time or part-time. Hands-on, project-based learning covering data wrangling, EDA, machine learning, and data visualization.
                    - **Time Commitment:** Significant time investment required for coursework, self-study, and team collaboration.
                    - **Cost and Financial Aid:** Tuition varies; financial aid options may be available.
                    - **Career Outcomes:** High job placement rates, career services, and networking opportunities.
                    - **Suitability:** Ideal for those passionate about data science, with clear career goals in related fields.
                    - **Application Process:** Includes a technical assessment and interview.
                    - **Community and Culture:** Emphasizes collaboration, inclusivity, and strong alumni engagement.
                    - **Diversity and Inclusion:** Focuses on promoting diversity in tech.
                    
                    Use this information to help users determine if they are suitable for the Eskwelabs bootcamp.
                    """
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                        	{"role": "system", "content": system_message},
                            {"role": "user", "content": prompt},
                            # {"role": "assistant", "content": prompt}
                        ],
                        max_tokens = 700
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
    
###############################################      

# FIXED HEADER

###############################################       
# Inject CSS to create a fixed container
# st.markdown("""
#     <style>
#     .fixed-container {
#         position: fixed;
#         top: 0;
#         width: 100%;
#         background-color: white;
#         z-index: 1000;

#     }
#     </style>
    
#     <div class="fixed-container">
#         <h1><br>Data Science Learning Path Classifier</h1>
#     </div>
# """, unsafe_allow_html=True)



st.title("Data Science Learning Path Classifier")
# Streamlit app setup
if 'BeginAssessment' not in st.session_state:
    st.session_state.BeginAssessment = True


col_main1, col_main2, col_main3 = st.columns([1,2,0.5])
with col_main1:
    with st.expander("**Our Bot**", expanded=st.session_state.BeginAssessment):
        st.write("Are you unsure about the best way to pursue your data science journey? Our intelligent classifier bot is here to help! By answering a few simple questions about your background, preferences, and goals, our bot will recommend the most suitable learning pathway for you.")

with col_main2:
    with st.expander("**How it works**", expanded=st.session_state.BeginAssessment):
        st.markdown("""
        1. Answer Questions: *Provide responses to a series of questions about your current experience, learning preferences, time commitment, and budget.*<br>
        2. Get Classified: *Based on your answers, our classifier bot will evaluate and determine the most appropriate learning pathway for you:* 
        :gray-background[**Eskwelabs' Bootcamp**], :gray-background[**Self-Learning**], :gray-background[**Master's Degree**]""", unsafe_allow_html=True)
with col_main3:
    if st.button("Start Over", disabled=st.session_state.BeginAssessment, type="primary", use_container_width = True, help = "To update your answer, please press the RESET button to start over and answer the questions again. Feel free to make any necessary improvements or corrections to enhance your response."):
        st.session_state.responses = []
        st.session_state.question_index = 0
        st.session_state.chat_history = []
        st.session_state.classification = []
        st.session_state.feedback_up = []
        st.session_state.feedback_down = []
        st.session_state.BeginAssessment = True
        st.rerun()       

    
if st.session_state.BeginAssessment == True:    
    with st.container(border=None):
        s1, s2, s3 = st.columns([1,8,1])
        with s2:
            st.markdown("")
            st.markdown("")
            st.markdown(f"<h2 style='text-align: center;'>Start Your Journey</h2>", unsafe_allow_html=True)
            st.markdown("""<h5 style='text-align: center;color: #e76f51;'><b><i>Simply click "Begin Assessment" </b></i><i>
            and follow the prompts to receive your personalized learning pathway recommendation. Empower your data science career with the right guidance tailored to your needs!.</h5>""", unsafe_allow_html=True)
            cs1,cs2,cs3 = st.columns([1,1,1])
            with cs2:
                if st.button("Begin Assessment", type="primary", use_container_width = True):
                    st.session_state.BeginAssessment = False
                    st.rerun()
                    

else: 
    # st.session_state.BeginAssessment == False:
    suitability()

        

if st.toggle("Show Work Flow", label_visibility="collapsed"):
    wf1, wf2 = st.columns([8,2])
    with wf1:
        with st.expander("Work Flow: How It Actually Works", expanded = True):
            st.image('data/DSLPC_WorkFlow.png')





       
