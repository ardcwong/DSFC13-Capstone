import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
import base64
import json
from datetime import datetime
import pytz

# Define the timezone for the Philippines
philippines_timezone = pytz.timezone('Asia/Manila')

########################################################
# API KEYS and CREDENTIALS
########################################################
api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]

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
  st.markdown(f"""
  <div style='display: flex; align-items: flex-start; padding: 10px; justify-content: flex-end;'>
      <div style='background-color: #F7F9FA; padding: 10px 15px; border-radius: 10px; margin-right: 10px; display: inline-block; text-align: right; max-width: 60%; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
          <span style='font-size: 16px;'>{message_text}</span>
      </div>
      <div style='flex-shrink: 0;'>
          <img src='{avatar_url_user}' alt='avatar' style='width: 40px; height: 40px; border-radius: 50%; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
      </div>
  </div>
  """, unsafe_allow_html=True)

#### AI AVATAR AND RESPONSE
@st.cache_data
def ai_avatar_lpc():
  # Load the image and convert it to base64
  with open('data/avatar_ai_lpc.png', 'rb') as image_file_lpc:
    encoded_string_lpc = base64.b64encode(image_file_lpc.read()).decode()
  # Base64 encoded image string from the previous step
  avatar_base64_lpc = encoded_string_lpc  # This is the base64 string you got earlier
  
  # Construct the base64 image string for use in HTML
  avatar_lpc = f'data:image/png;base64,{avatar_base64_lpc}'
  return avatar_lpc

avatar_lpc = ai_avatar_lpc()

def show_ai_response_lpc(message_text,avatar_lpc):
  st.markdown(f"""
  <div style='display: flex; align-items: flex-start; padding: 10px; justify-content: flex;'>
      <div style='flex-shrink: 0;'>
          <img src='{avatar_lpc}' alt='avatar' style='width: 40px; height: 40px; border-radius: 50%;box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
      </div>
      <div style='background-color: #FCFCFC; padding: 10px 15px; border-radius: 10px; margin-left: 10px; display: inline-block; text-align: left; max-width: 85%;box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
          <span style='font-size: 16px;'>{message_text}</span>
      </div>

  </div>
  """, unsafe_allow_html=True)

def remove_stopwords(response):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(response)
    filtered_response = [word for word in word_tokens if word.lower() not in stop_words]
    return ' '.join(filtered_response)


@st.cache_data
def john_avatar():
  # Load the image and convert it to base64
  with open('data/John.png', 'rb') as image_file_john:
    encoded_string_john = base64.b64encode(image_file_john.read()).decode()
  
  # Construct the base64 image string for use in HTML
  john_avatar = f'data:image/png;base64,{encoded_string_john}'
  return john_avatar

john_avatar_lpc = john_avatar()

with st.sidebar:
  st.markdown(
      f"""
      <style>
      .tooltip {{
        position: relative;
        display: inline-block;
        cursor: pointer;
      }}
  
      .tooltip .tooltiptext {{
        visibility: hidden;
        width: 250px;
        background-color: #fff;
        color: #333;
        text-align: left; /* Align text to the left */
        border-radius: 5px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        left: 50%; /* Center the tooltip horizontally */
        bottom: 110%; /* Position the tooltip on top */
        transform: translateX(-50%); /* Center tooltip horizontally */
        opacity: 0;
        transition: opacity 0.3s;
        white-space: normal; /* Allow text to wrap */
        display: flex;
        align-items: flex-end; /* Align content to the bottom */
        justify-content: flex-start; /* Align content to the left */
        box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.1);
        font-size: 12px;
      }}
  
      .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
      }}
      </style>
      <div style='display: flex; align-items: center; justify-content: center; width: 100%;'>
          <div class='tooltip' style='flex-shrink: 0; width: 100%;'>
              <img src='{john_avatar_lpc}' style='width: 100%; height: auto; object-fit: contain;'>
              <span class="tooltiptext">The classifier takes John through a series of questions—By answering questions about his education, skills, and career goals, the classifier quickly identifies that John is ready for the Data Science Fellowship (DSF). It even provides a personalized preparation plan, boosting John’s confidence in his path forward.</span>
          </div>
      </div>
      """,
      unsafe_allow_html=True
  )
st.markdown(
    f"""
    <style>
    .tooltip {{
      position: relative;
      display: inline-block;
      cursor: pointer;
    }}

    .tooltip .tooltiptext {{
      visibility: hidden;
      width: 400px;
      background-color: #fff;
      color: #333;
      text-align: left; /* Align text to the left */
      border-radius: 5px;
      padding: 10px;
      position: absolute;
      z-index: 1;
      left: 50%; /* Position next to the image */
      top: 50%;
      transform: translateX(20%) translateY(-50%); /* Center tooltip box */
      opacity: 0;
      transition: opacity 0.3s;
      white-space: normal; /* Allow text to wrap */
      display: flex;
      align-items: flex-end; /* Align content to the bottom */
      justify-content: flex-start; /* Align content to the left */
      box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.1);
      font-size: 20px;
    }}

    .tooltip:hover .tooltiptext {{
      visibility: visible;
      opacity: 1;
    }}
    </style>
    <div style='display: flex; align-items: center; justify-content: center; width: 100%;'>
        <div class='tooltip' style='flex-shrink: 0; width: 100%;'>
            <img src='{john_avatar_lpc}' style='width: 100%; height: auto; object-fit: contain;'>
            <span class="tooltiptext">Meet John Santos, an aspiring Data Scientist with a background in Electrical Engineering. John’s eager to take the next step in his career, seeking a program that challenges him and prepares him for advanced roles in data science.</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)












########################################################
# SUITABILITY
########################################################
questions = [
    # Educational Background & Experience
    "What is your highest level of education? (e.g., High School, Bachelor's, Master's)",
    "Did you study any STEM-related fields? If yes, which one? (e.g., Yes - Computer Science, No)",
    "Have you taken any mathematics or statistics courses during your studies?",
    "Do you have experience in programming? If yes, which languages? (e.g., Yes - Python, Java, No)",

    # Data Science & Analytics Knowledge
    "What is your current level of knowledge or experience in data science/analytics? (e.g., Beginner, Intermediate, Advanced)",
    "Are you familiar with data analysis tools like Excel, SQL, or Tableau? (e.g., Yes, Somewhat, No)",
    # "Have you worked with machine learning algorithms before? (e.g, Yes, Yes - implemented several models, No, No - but I am interested, ...)",
    "How would you rate your proficiency in mathematics and statistics? (e.g., Beginner, Intermediate, Advanced)",

    # Professional Experience
    "Do you have experience working in a data-related role?",
    "Have you completed any data-related projects? Can you describe one?",

    # Learning Preferences & Availability
    "Do you prefer structured learning with deadlines or self-paced learning?",
    "How much time per week can you commit to learning? (e.g., Less than 10 hours, 10-20 hours, More than 20 hours)",
    "Are you comfortable with a fast-paced and intensive learning environment?",
    "Do you prefer hands-on projects or theoretical learning?",
    "Have you participated in online learning platforms or bootcamps before?",
    "Do you prefer learning in a classroom setting, online, or a hybrid approach?",
    "Do you work better independently or in group settings?",

    # Career Goals & Commitment
    "What are your long-term career goals?",
    "Are you looking to advance in your current role or switch careers?",
    "Are you more interested in applied roles or research-oriented roles?",
    "Are you interested in gaining foundational skills or advanced data science skills?",
    "Are you willing to invest in a master's degree, which typically requires a significant financial and time commitment?",
    "Do you need to balance your studies with work or other commitments?",

    # Special Interests & Problem-Solving
    "Are there any specific areas of data science you are particularly interested in (e.g., machine learning, data visualization, big data)?",
    "How do you handle complex problem-solving and analytical tasks?"
]

# Google Sheets connection function
def google_connection(client):
    # Open the Google Sheet
    spreadsheet = client.open("Data Science Learning Path Classifier")
    return spreadsheet

# Function to write feedback and chat history to Google Sheet
def write_feedback_to_gsheet(spreadsheet, feedback, chat_history):
    sheet = spreadsheet.sheet1
    chat_history_list = pd.DataFrame(chat_history)[[1]].T.values.flatten().tolist()
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


if 'question_index' not in st.session_state:
    st.session_state.question_index = 0

if 'BeginAssessment' not in st.session_state:
    st.session_state.BeginAssessment = True
  
if 'classification' not in st.session_state:
    st.session_state.classification = False

if 'responses' not in st.session_state:
    st.session_state.responses = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'feedback_up' not in st.session_state:
    st.session_state.feedback_up = []
  
if 'feedback_down' not in st.session_state:
    st.session_state.feedback_down = []
  
@st.fragment
def suitability():
    if st.session_state.classification == True:
        # Display the entire chat history with user responses on the right
        col_main11, col_main22, col_main33 = st.columns([1,4,1])    
        with col_main22:
          tab1, tab2 = st.tabs(["Suitability and Recommendation", "Your Responses"])
          with tab2:
              # Display the entire chat history with user responses on the right
                for role, message in st.session_state.chat_history:
                    if role == "User":
                        show_user_answer_lpc(message,avatar_url_user)
                    elif role == "AI":
                        show_ai_response_lpc(message,avatar_lpc)
          with tab1:
              show_ai_response_lpc(st.session_state.chat_history[-1][1],avatar_lpc)
              if st.session_state.feedback_up == 1:
                  show_ai_response_lpc("<b>You selected 👍🏻 Thanks for your feedback!</b>",avatar_lpc)

              elif st.session_state.feedback_up == 0:
                  show_ai_response_lpc("<b>You selected 👎🏻 Thanks for your feedback</b>",avatar_lpc)
              else:
                  show_ai_response_lpc("Could you please give a thumbs up if you find these recommendations specific and tailored to your responses, or a thumbs down if you do not?",avatar_lpc)

                  f1,f2 = st.columns([1,1])

                  if f1.button("👍🏻", use_container_width = True, help = "This response helpful"):
                      feedback_score = 1
                      sheet = write_feedback_to_gsheet(st.session_state.spreadsheet_DSLPC, feedback_score, st.session_state.chat_history)
                      st.session_state.feedback_up = feedback_score
                      st.rerun() 
                  elif f2.button("👎🏻", use_container_width = True, help = "This response unhelpful"):
                      feedback_score = 0
                      sheet = write_feedback_to_gsheet(st.session_state.spreadsheet_DSLPC, feedback_score, st.session_state.chat_history)
                      st.session_state.feedback_down = feedback_score
                      st.rerun() 

              with st.container():
                  content_dsf_ad = """
                  <h6 style='text-align: left;color: #e76f51;'>Learn More about Data Science Fellowship (DSF) Program by Eskwelabs!</h6>
                  <div style='text-align: left;'>This program offers a comprehensive curriculum designed to equip 
                  participants with practical skills through hands-on projects and sprints. The program includes projects on customer segmentation, 
                  credit fraud detection, recommender engines, and generative AI, each aiming to provide actionable insights and enhance strategic 
                  decision-making. Various payment options are available, including early bird discounts, installment plans, and study-now-pay-later 
                  schemes. Interested individuals can apply online, explore past capstone projects, and consult with admissions advisors for 
                  personalized guidance. Additional resources and details about the program, including tuition fees and refund policies, 
                  are accessible via the Eskwelabs website or interactive with our Program Information Chatbot for more information by clicking this <b>"Program Information"</b> button.</div>
                  """
                  show_ai_response_lpc(content_dsf_ad,avatar_lpc)
                  st.markdown("")
                  cola, colb, colc = st.columns([1,0.7,1])
                  with colb:
                      program_info_page_switch()

    else:
        lpc1, lpc2, lpc3 = st.columns([1,4,1])
        with lpc2:
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
              
def display_question():
    if st.session_state.question_index < len(questions):
        current_question = questions[st.session_state.question_index]


# Function to get classification from OpenAI
def get_classification():


    questions_responses = ""
    for i, question in enumerate(questions):
        questions_responses += f"{i+1}. {question}\n - Responses: {st.session_state.responses[i]}\n"

    prompt = f"""
    Based on the {questions_responses} provided, 
    Considering the following factors:
      1. Educational Background & Experience
      2. Data Science & Analytics Knowledge
      3. Professional Experience
      4. Learning Preferences & Availability
      5. Career Goals & Commitment
      6. Special Interests & Problem-Solving
    And considering this information:
      1. Data Analytics Bootcamp is focused on teaching data analytics, storytelling, and visualization, as well as tools like Power BI, SQL (Google BigQuery), and Google Data Studio to help current and future professionals answer business questions with data. We invite fresh grads, career shifters, job promotion seekers, upskillers, freelancers who want to level up, and aspiring data analysts to enroll in this intensive program.
      2. Data Science Fellowship prepares you to enter the data science industry long-term or to upskill yourself in your existing company with industry relevant tools. By the end of the program, you would have completed and presented 5 data science projects to data science experts.
      3. In the Data Science Fellowship (DSF), you can develop skills in machine learning, web scraping, big data analysis, Streamlit, network analytics, Python, and data ethics.
      4. Experience in machine learning algorithms is NOT required for Data Science Fellowship and Data Analytics Bootcamp.
    
    Assess and classify my suitability for the following data science learning pathway: Eskwelabs' Data Science Fellowship, Eskwelabs' Data Analytics Bootcamp, self-learning, or a master's degree, and recommend the most suitable learning pathway.
    If I am suitable for either Data Science Fellowship or Data Analytics Bootcamp, provide an assessment of my readiness for DSF, how I should prepare for DSF if I decided to apply, and suggest if I should consider to start first with DAB before DSF.
    
    Use this format for your response:
    **1. Eskwelabs' Data Science Fellowship:** Suitability 
        \n **Assessment**: Explain
        \n **Recommendation**: 
        
    **2. Eskwelabs' Data Analytics Bootcamp:** Suitability 
        \n **Assessment**: Explain
        \n **Recommendation**:
        
    **3. Self-Learning:** Suitability 
        \n **Assessment**: Explain
        \n **Recommendation**:
        
    **4. Master's Program:** Suitability 
        \n **Assessment**: Explain
        \n **Recommendation**:


    **Most Suitable Learning Path:** Data Science Fellowship, Data Analytics Bootcamp, Self-learning, or Master's Program. 
      \n**Preparation Plan: Recommend a simple preparation plan.

    """
  
    try:
        # Define the system message with the summarized information
        system_message = """
        You are an expert education bot designed to classify the suitability either Highly Suitable, Moderately Suitable, Slightly Suitable, or Not Suitable for each learning pathway of the user whichever is applicable.
        
        Based on the user's responses to a series of questions, you will classify and assess the suitability 
        of the user to each of the following learning path: Eskwelabs' Data Science Fellowship, Eskwelabs' Data Analytics Bootcamp, self-learning, or a master's degree., and you will recommend the most suitable learning path.

        After determining the path, if the user is suitable for Data Science Fellowship, provide an assessment of his readiness for DSF, how he should prepare for DSF if he decided to apply, and suggest if he should consider to start first with DAB before DSF.
        
        The response should begin with a congratulatory or thank you message for completing the assessment.🎉
        End the response with a good luck message on the user's Data Science Journey!🚀 Do not ask for more question or guidance.
        """
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
              {"role": "system", "content": system_message},
              {"role": "user", "content": prompt},
            ],
            temperature = 0.4,
            top_p = 0.5
        )
        classification = response.choices[0].message.content.strip()
        return classification
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def load_test_answers_by_name(name):
    # Define the updated answers for each person
    test_answers = {
        # "Maria Cruz": [
        #     "Bachelor’s in Business Administration", "No", "Basic statistics", "Limited, just basic understanding of Python",
        #     "Basic knowledge from online courses in Excel and SQL", "Proficient in Excel, basic knowledge of SQL", "Basic", "No, currently working as a marketing assistant",
        #     "Analyzed customer survey data using Excel for a marketing campaign", "Prefers structured learning with deadlines", "Can commit 10-15 hours per week",
        #     "Prefers moderate-paced learning", "Prefers hands-on learning", "Completed a course in digital marketing on Coursera", "Prefers online learning",
        #     "Works well independently but appreciates occasional group work", "Transition into a data analyst role in the marketing industry", "Looking to switch careers",
        #     "Interested in applied roles like Data Analyst", "Looking to gain foundational skills", "No", "Yes, currently working full-time",
        #     "Interested in data visualization and marketing analytics", "Breaks down problems into smaller tasks, uses Excel for analysis"
        # ],
        "John Santos": [
            "Master’s in Electrical Engineering", "Yes, Electrical Engineering", "Extensive coursework in calculus, and statistics", "Proficient in Python, MATLAB, and C++",
            "Intermediate; practical experience with machine learning", "Experienced with SQL, Excel, and Tableau", "Advanced",
            "Worked as a data engineer in a tech startup", "Developed a predictive maintenance model for an industrial company using Python", "Comfortable with both, but leans towards self-paced learning",
            "Can commit 20-25 hours per week", "Thrives in fast-paced, challenging environments", "Enjoys a mix of both hands-on projects and theoretical understanding",
            "Completed several MOOCs on machine learning", "Prefers hybrid approach, combining classroom and online", "Appreciates community support and networking opportunities",
            "Transition into a Data Scientist or Machine Learning Engineer role", "Looking to advance and specialize in data science", "Interested in applied roles with a focus on innovation",
            "Aims to gain advanced data science skills", "No", "Yes", "Strong interest in machine learning and predictive modeling",
            "Uses a systematic approach, leveraging programming and mathematical models"
        ],
        "Emily Tan": [
            "Bachelor’s in Psychology", "No", "Basic statistics", "Limited, basic knowledge of R",
            "Basic; self-study interest in applying to psychology research", "Basic knowledge of Excel", "Basic", "No, currently a research assistant in a psychology lab",
            "Assisted in data collection and analysis for psychological research studies", "Prefers structured learning with deadlines", "Can commit 15-20 hours per week",
            "Comfortable with moderate-paced learning", "Prefers hands-on learning, especially with real-world data", "Completed a course in research methods", "Prefers online learning",
            "Values community support for sharing ideas and insights", "Apply data science to psychological research or transition into a data analyst role in healthcare",
            "Interested in both advancing and potentially switching to a data-related career", "Interested in research-oriented roles with practical applications",
            "Looking to gain foundational data science skills", "Possibly, but unsure", "Yes, working part-time and assisting in research",
            "Interested in data visualization for psychological research", "Relies on research and collaboration with peers to find solutions"
        ],
        # "Raj Patel": [
        #     "Bachelor’s in Computer Science", "Yes, Computer Science", "Extensive coursework in mathematics and statistics", "Proficient in Python, Java, and SQL",
        #     "Advanced; coursework and practical projects", "Experienced with SQL, Python, and Power BI", "Advanced",
        #     "Worked as a software developer with a focus on data engineering", "Developed a recommendation system using collaborative filtering for an e-commerce site",
        #     "Comfortable with both, but prefers self-paced learning", "Can commit 20-25 hours per week", "Enjoys fast-paced environments with challenging problems",
        #     "Prefers a mix of hands-on and theoretical learning", "Completed several online courses in machine learning", "Prefers online learning with occasional classroom sessions",
        #     "Appreciates community support but works well independently", "Transition into a Data Scientist or Machine Learning Engineer role in a tech company",
        #     "Looking to advance within the data science field", "Interested in applied roles with a focus on cutting-edge technology",
        #     "Aims to gain advanced skills in data science", "Yes", "No, fully committed to learning", "Fascinated by machine learning and artificial intelligence",
        #     "Breaks down the problem into components, uses programming and algorithms to solve"
        # ],
        "Lisa Kim": [
            "Bachelor’s in Economics", "Yes, Economics", "Coursework in statistics and econometrics", "Basic knowledge of Python and R",
            "Basic; knowledge from courses in econometrics and data analysis", "Proficient in Excel, basic knowledge of R", "Intermediate",
            "Currently working as a financial analyst", "Analyzed financial data to create reports for investment strategies", "Prefers structured learning with clear deadlines",
            "Can commit 10-15 hours per week", "Comfortable with moderate-paced learning", "Prefers hands-on projects related to finance and economics",
            "Completed a course in financial modeling", "Prefers hybrid approach, especially for practical sessions", "Values community support for networking and collaboration",
            "Transition into a role that combines finance with data science, like a Quantitative Analyst", "Interested in advancing into a more technical role within finance",
            "Interested in applied roles within the finance industry", "Looking to gain foundational data science skills", "No", "Yes, currently working full-time",
            "Focused on financial analytics and econometrics", "Uses financial models and seeks insights from data analysis"
        ],
        "Jao Cordero": [
            "BS in Computer Engineering", "Yes, BS Computer Engineering", "Yes", "Yes - Java",
            "Basic", "Yes", "Intermediate", "Yes", "Yes, Reports Processing",
            "Structured learning with deadlines", "6 hours", "Yes", "Theoretical learning", "Yes",
            "classroom setting", "Both", "To gain knowledge in data visualization", "Advance in current role", 
            "Research-oriented", "Yes", "No", "Yes", "Yes, data visualization", 
            "Breaks down the problem, identify root cause"
        ]
    }

    # Ensure the session state is properly initialized
    if 'responses' not in st.session_state:
        st.session_state.responses = []

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if name in test_answers:
        # Clear existing session state
        st.session_state.responses = []
        st.session_state.chat_history = []

        # Load the answers and simulate the chat interaction
        for i, answer in enumerate(test_answers[name]):
            if i < len(questions):
                st.session_state.chat_history.append(("AI", questions[i]))  # Append the question first
            st.session_state.responses.append(answer)
            st.session_state.chat_history.append(("User", answer))  # Append the user's answer next

        st.session_state.question_index = len(test_answers[name])
        st.session_state.classification = True

        st.success(f"Test answers for {name} loaded successfully!")
    else:
        st.error(f"No test answers found for {name}!")

################################################## SIDE BAR ##################################################
with st.sidebar:

    if st.button("Start Over", disabled=st.session_state.BeginAssessment, type="primary", use_container_width = True, help = "Restart Assessment"):
        st.session_state.responses = []
        st.session_state.question_index = 0
        st.session_state.chat_history = []
        st.session_state.classification = False
        st.session_state.feedback_up = []
        st.session_state.feedback_down = []
        st.session_state.BeginAssessment = True
        st.rerun()       

with st.sidebar:
  # Call this function to load test answers at the beginning of your app (or when you need to test)
  name = st.selectbox("Choose a test user:", ["John Santos", "Emily Tan", "Raj Patel", "Lisa Kim", "Jao Cordero"])
  if st.button("Load Demo Answers", use_container_width = True, type = "primary"):
      load_test_answers_by_name(name)
      st.rerun()
        
with st.sidebar:
    if st.toggle("Discover!"):
        wf1, wf2 = st.columns([8,2])
        with wf1:
            with st.expander("Work Flow: How It Actually Works", expanded = True):
                st.image('data/DSLPC_WorkFlow.png')

################################################## SIDE BAR ##################################################


################################################ MAIN PROGRAM ################################################
# Main logic
if st.session_state.question_index < len(questions):
    display_question()
    
    user_response = st.chat_input("Your response:", disabled = (st.session_state.BeginAssessment or st.session_state.classification))
    if user_response:
        st.session_state.responses.append(user_response)
        st.session_state.chat_history.append(("User", user_response))
        st.session_state.question_index += 1
        if st.session_state.question_index < len(questions):
            next_question = questions[st.session_state.question_index]
            st.session_state.chat_history.append(("AI", next_question))
        else:
            if st.session_state.responses and st.session_state.question_index == len(questions):
                classification = get_classification()
                if classification:
                    st.session_state.chat_history.append(("AI", classification))
                    st.session_state.question_index += 1
                    st.session_state.classification = True

else:
    if st.session_state.responses and st.session_state.question_index == len(questions):
        classification = get_classification()
        if classification:
            st.session_state.chat_history.append(("AI", classification))
            st.session_state.question_index += 1
            st.session_state.classification = True
            st.rerun()
    
  
col_main1, col_main2, col_main3 = st.columns([1,4,1])
with col_main2:
  st.markdown("""<h1 style='text-align: center;'>Data Science Learning Path Classifier</h1>""", unsafe_allow_html=True)
  cc1, cc2, cc3 = st.columns([1,10,1])
  with cc2:
  

    st.markdown(f"<h6 style='text-align: center;'><i>Are you unsure about the best way to pursue your data science journey? Our intelligent classifier bot is here to help! By answering a few simple questions about your background, preferences, and goals, our bot will recommend the most suitable learning pathway for you.</i></h6>", unsafe_allow_html=True)
  
    if st.session_state.BeginAssessment == True: 
      st.markdown("""
      **HOW IT WORKS:**<br>
      1. Answer Questions: *Provide responses to a series of questions about your current experience, learning preferences, time commitment, and budget.*<br>
      2. Get Classified: *Based on your answers, our classifier bot will evaluate and determine the most appropriate learning pathway for you:* 
      :gray-background[**Data Science Fellowship**], :gray-background[**Data Analytics Bootcamp**], :gray-background[**Self-Learning**], :gray-background[**Master's Degree**]""", unsafe_allow_html=True)

if st.session_state.BeginAssessment == True:  
  st.markdown("<br>", unsafe_allow_html = True)       
  
  ba00, ba01, ba02, ba03, ba04 = st.columns([1,1,0.7,1,1])
  with ba02:
    st.markdown(
        f"""
        <style>
        .tooltip {{
          position: relative;
          display: inline-block;
          cursor: pointer;
        }}
    
        .tooltip .tooltiptext {{
          visibility: hidden;
          width: 250px;
          background-color: #fff;
          color: #333;
          text-align: left; /* Align text to the left */
          border-radius: 5px;
          padding: 10px;
          position: absolute;
          z-index: 1;
          left: 100%; /* Position next to the image */
          top: 50%;
          transform: translateX(20%) translateY(-50%); /* Center tooltip box */
          opacity: 0;
          transition: opacity 0.3s;
          white-space: normal; /* Allow text to wrap */
          display: flex;
          align-items: flex-end; /* Align content to the bottom */
          justify-content: flex-start; /* Align content to the left */
          box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.1);
          font-size: 12px;
        }}
    
        .tooltip:hover .tooltiptext {{
          visibility: visible;
          opacity: 1;
        }}
        </style>
        <div style='display: flex; align-items: center; justify-content: center; width: 100%;'>
            <div class='tooltip' style='flex-shrink: 0; width: 100%;'>
                <img src='{avatar_lpc}' style='width: 100%; height: auto; object-fit: contain;'>
                <span class="tooltiptext">I consistently provide reliable recommendations, with a 93% consistency rate in my suitability classifications.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

  s1, s2, s3 = st.columns([1,3,1])
  with s2:
      st.markdown("")
      st.markdown("")
      st.write(f"<h6 style='text-align: center;'><b>Start Your Journey</b></h6>", unsafe_allow_html=True)
      st.write("""<h6 style='text-align: center;color: #e76f51;'><b><i>Simply click "Begin Assessment" </b></i><i>
      and follow the prompts to receive your personalized learning pathway recommendation. Empower your data science career with the right guidance tailored to your needs!.</h6>""", unsafe_allow_html=True)
      cs1,cs2,cs3 = st.columns([1,1,1])
      with cs2:
          if st.button("Begin Assessment", type="primary", use_container_width = True):
              st.session_state.BeginAssessment = False
              st.rerun()
else: 
  suitability()      
  
