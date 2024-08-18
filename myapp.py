import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
import base64

########################################################
# PAGE CONFIG
########################################################
st.set_page_config(
    page_title = "Welcome to EskwelApps!",
    # initial_sidebar_state="expanded",
    layout='wide',
    menu_items={
    'About': "### Hi! Thanks for viewing our app!"
    }
)


########################################################
# LOAD STYLES CSS
########################################################
# Function to load local CSS file
def load_local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            # st.success("CSS loaded successfully!")  # Debug statement
    except FileNotFoundError:
        st.error(f"File {file_name} not found!")

#Load the local CSS file from the 'data' directory
load_local_css("data/styles.css")



########################################################
# CHANGE BACKGROUND USING LOCAL PNG
########################################################
@st.cache_data
def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

set_bg_hack('data/bg.png')


########################################################
# API KEYS and CREDENTIALS
########################################################
api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]

########################################################
# INITIALIZE role and vote (login)
########################################################
if "role" not in st.session_state:
    st.session_state.role = None

if "vote" not in st.session_state:
    st.session_state.vote = None
    
if "userinfo" not in st.session_state:
    st.session_state.userinfo = None

########################################################
# SET UP ROLES
########################################################
ROLES = [None,"Aspiring Student", "Fellow", "Mentor"]
role = st.session_state.role

########################################################
# SETUP CONNECTION TO GOOGLE SHEET
########################################################
def google_connection(client):
# Open the Google Sheet
    spreadsheet = client.open("LoginCredentials")
    
    return spreadsheet

########################################################
# ACCESS LoginCredentials GSHEET
########################################################
if "spreadsheet" not in st.session_state:
    # Google Sheets setup using st.secrets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    st.session_state.spreadsheet = google_connection(client)


########################################################
# LOGIN RULES
########################################################
def login():
        if st.session_state.vote == None: 
            vote(st.session_state.spreadsheet)
        else:
            st.session_state.role = st.session_state.vote['role']
           
            # st.markdown("Let us know who's visiting. Are you a/an ...")
            # col21, col22, col23 = st.columns([1,1,1])
        
        
        # def role_chosen():
        #     a = col21.button("Aspiring Student", type = "primary", use_container_width = True)
        #     b = col22.button("Fellow", type = "primary", use_container_width = True)
        #     c = col23.button("Mentor", type = "primary", use_container_width = True)
        #     if a:
        #         role = "Aspiring Student"
        #     elif b:
        #         role = "Fellow"
        #     elif c:
        #         role = "Mentor"
        #     else: 
        #         role = []
        #     return role
        # role = role_chosen()
       
        
        # if st.session_state.vote == None: 
            
            

        #     if role in ["Aspiring Student"]:
        #         st.session_state.vote = {"role": role}
        #         st.session_state.role = st.session_state.vote['role']
        #         st.rerun()
        #     elif role in ["Fellow", "Mentor"]:
        #         vote(role,st.session_state.spreadsheet)
        #     # elif role == []:
                
        # else:
        #     st.session_state.role = st.session_state.vote['role']

        st.markdown("""<br><br>
        
        """, unsafe_allow_html=True)

########################################################
# LOGIN POP UP AND CHECKING
########################################################
@st.dialog("Log In",width="large")
def vote(spreadsheet):
    sheet = spreadsheet.worksheet("Sheet1")
    users = pd.DataFrame(sheet.get_all_records())

    # st.radio
    # if role in ["Fellow"]:
    #     sheet = sheet_fellow
    #     user = users_fellow
    # elif role in ["Mentor"]:
    #     sheet = sheet_mentor
    #     user = users_mentor
    
    # Function to check login
    def check_login(userid, password):    
        users = pd.DataFrame(sheet.get_all_records())
        if userid in users['UserID'].values:
            st.session_state.username_exist = True
            if password == str(users[users['UserID'] == userid]['Password'].values[0]):
                return True
        return False
    
    userid = st.text_input("UserID")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        
        if check_login(userid, password):
            st.success("Login successful!")
            role = str(users[users['UserID']==userid]['Type'].values[0])
            st.session_state.vote = {"role": role}
            st.session_state.role = st.session_state.vote['role']
            df_user_info = users[users['UserID']==userid]
            st.session_state.userinfo = df_user_info
            st.session_state.name = str(users[users['UserID']==userid]['FirstName'].values[0])
            st.rerun()
        else:
            st.error("Invalid username or password")       

    if st.toggle("[For DEMO] Sample Login Credentials"):
        st.dataframe(users, use_container_width=True, hide_index=True)
# st.write(st.session_state.userinfo)
########################################################
# LOG OUT
########################################################
def logout():
    # st.session_state = None
    
    
    @st.dialog("Are you sure?")
    def LO_confirmation():
        # st.session_state.LO_confirmation = True
        LO1, LO2 = st.columns([1,1])
        with LO1:
            if st.button("Yes", use_container_width = True):
                
        
                
                st.session_state.role = None
                st.session_state.vote = None
                st.session_state.userinfo = None
                st.switch_page(home_page)
                st.rerun()
        with LO2:
            if st.button("No", use_container_width = True):
                st.switch_page(home_page)
                st.rerun()
    
    LO_confirmation()



########################################################
# HOME PAGE
########################################################
if role == None:
    role_welcome = "!"
elif role == []:
    role_welcome = "!"
else:
    role_welcome = f", {role}!"

# def home_main_content():

    # EA0, EA1, EA2, EA3 = st.columns([0.3, 1.5, 1.5,0.3])
    # with EA1:

def home():
    st.markdown(f"""<h1 style='text-align: center;'>Welcome to EskwelApps{role_welcome}</h1>""", unsafe_allow_html=True)
        # st.image('data/EskwelApps.png', use_column_width=True)

    home1, home2, home3 = st.columns([0.3, 3, 0.3])
    with home2:
        # st.markdown(f"<h1 style='text-align: center;'>Welcome to EskwelApps</h1>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="
                background: linear-gradient(90deg, #009688, #3F51B5);
                padding: 40px;
                border-radius: 10px;
                text-align: center;
                font-family: Arial, sans-serif;
                color: white;
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
            ">
                <h1 style="font-size: 28px; margin-bottom: 10px; font-weight: bold; letter-spacing: 2px; color: white; text-transform: capitalize;">
                    Ready To Navigate Your Data Science Journey?
                </h1>
                <p style="font-size: 18px; line-height: 1.5; letter-spacing: 1.5px; color: white;">
                    <strong>Learn and Be Guided with Confidence!</strong> EskwelApps is here to guide you every step of the way. Whether you're exploring the perfect learning path, seeking detailed program insights, or looking for a personalized assessment, we’ve got everything you need to thrive. <strong><br><br>Unlock Tools and Resources!</strong> Once enrolled, dive into our comprehensive course outline, get your questions answered with our bootcamp assistant, and easily set up your environment with our installation guide. Let EskwelApps support you throughout your entire data science journey.
                </p>
            </div>
            """,
            unsafe_allow_html=True)
        

        if st.session_state.role in ["Fellow","Ops","Fellow (Developer)"]:
            st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)
            st.markdown(
            f"""
            <div style="
                background: linear-gradient(90deg, #3D2B6A, #6A5FAE, #3D2B6A);
                padding: 6px;
                border-radius: 10px;
                text-align: center;
                font-family: Arial, sans-serif;
                color: white;
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
            ">
                <h1 style="font-size: 20px; margin-bottom: 10px; font-weight: bold; letter-spacing: 2px; color: white; text-align: center;">
                    Hi, <span style="color: #FFD700;">{st.session_state.userinfo['FirstName'].values[0]}</span>!<br>We've added these tools and resources for you!
                </h1>
            </div>
            """,
            unsafe_allow_html=True
            )

    if st.session_state.role in ["Ops"]:
        om0, om1, om2, om3 = st.columns([0.3, 1.5, 1.5,0.3])
        with om1:
            with st.container(border = True, height=300):
                st.markdown("""<br>""", unsafe_allow_html=True)
                # om11, om12, om13 = st.columns([0.7,1,0.7])
                # with om12:
                #     st.image('data/avatar_course_outline.png', use_column_width=True)
                om111, om122, om133 = st.columns([0.1,1,0.1])
                with om122:
                    ############# Data Science Learning Path Classifier ##############
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-weight:bold; font-size: 16px;'>Pathfinder Assessment Report Generator</span>
                                </div>
                                """,
                                unsafe_allow_html=True)
                    ############# DESCRIPTION
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-size: 14px;'><br>Leverage this tool to efficiently generate personalized reports 
                                    for Pathfinder Exam takers. The generator uses aggregated scores across various exam categories to produce 
                                    detailed insights into each candidate's strengths and areas for improvement.</span>
                                </div>
                                """, unsafe_allow_html=True)
                    st.markdown("""<br>""", unsafe_allow_html=True)
                
                if st.button("Launch", 7,use_container_width = True, type = "primary"):
                    st.switch_page("Ops/PARGenerator.py")
        with om2:
            with st.container(border = True, height=300):
                st.markdown("""<br>""", unsafe_allow_html=True)
                # om11, om12, om13 = st.columns([0.7,1,0.7])
                # with om12:
                #     st.image('data/avatar_course_outline.png', use_column_width=True)
                om211, om222, om233 = st.columns([0.1,1,0.1])
                with om222:
                    ############# Data Science Learning Path Classifier ##############
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-weight:bold; font-size: 16px;'>Course Outline Generator</span>
                                </div>
                                """,
                                unsafe_allow_html=True)
                    ############# DESCRIPTION
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-size: 14px;'><br>Leverage this tool to access a meticulously crafted course 
                                    outline that provides a clear and comprehensive overview of the program’s core topics and sub-topics, 
                                    along with specific learning objectives, divided into four distinct Sprints.</span>
                                </div>
                                """, unsafe_allow_html=True)
                    st.markdown("""<br>""", unsafe_allow_html=True)
                
                if st.button("Launch", 8,use_container_width = True, type = "primary"):
                    st.switch_page("Ops/COGenerator.py")
    
    if st.session_state.role in ["Fellow","Ops","Fellow (Developer)"]:
        em0, em1, em2, em3, em4 = st.columns([0.3, 1,1,1,0.3])
        with em1:
            with st.container(border = True, height=550):
                st.markdown("""<br>""", unsafe_allow_html=True)
                em11, em12, em13 = st.columns([0.7,1,0.7])
                with em12:
                    st.image('data/avatar_course_outline.png', use_column_width=True)
                em111, em122, em133 = st.columns([0.1,1,0.1])
                with em122:
                    ############# Data Science Learning Path Classifier ##############
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-weight:bold; font-size: 16px;'>Course Outline</span>
                                </div>
                                """,
                                unsafe_allow_html=True)
                    ############# DESCRIPTION
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-size: 14px;'><br>This page is designed to provide you with a comprehensive overview of our bootcamp to 
                                    guide you through each phase of your learning journey.</span>
                                </div>
                                """, unsafe_allow_html=True)
                    st.markdown("""<br>""", unsafe_allow_html=True)
                
                if st.button("Launch", 4,use_container_width = True, type = "primary"):
                    st.switch_page("CourseOutline/CourseOutline.py")
    
        
        with em2:
            with st.container(border = True, height=550):
                st.markdown("""<br>""", unsafe_allow_html=True)
                em21, em22, em23 = st.columns([0.7,1,0.7])
                with em22:
                    st.image('data/avatar_ai.png', use_column_width=True)
                em211, em222, em233 = st.columns([0.1,1,0.1])
                with em222:
                    ############# Program Information Bot ##############
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-weight:bold; font-size: 16px;'>Data Science Bootcamp Assistant</span>
                                </div>
                                """,
                                unsafe_allow_html=True)
                    ############# DESCRIPTION
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-size: 14px;'><br>Ask any question related to the bootcamp, and get recommendations and answers.</span>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.markdown("""<br>""", unsafe_allow_html=True)
                    
                if st.button("Launch", 5,use_container_width = True, type = "primary"):
                    st.switch_page("DSFBAssistant/DSFBootcampAssistant.py")
        with em3:
            with st.container(border = True, height=550):
                st.markdown("""<br>""", unsafe_allow_html=True)
                em31, em32, em33 = st.columns([0.7,1,0.7])
                with em32:
                    st.image('data/installation_guide.png', use_column_width=True)
                em311, em322, em333 = st.columns([0.1,1,0.1])
                with em322:
                    ############# Program Information Bot ##############
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-weight:bold; font-size: 16px;'>Installation Guide</span>
                                </div>
                                """,
                                unsafe_allow_html=True)
                    ############# DESCRIPTION
                    st.markdown("""
                                <div style='text-align: center;'>
                                    <span style='font-size: 14px;'><br>An installation guide page where you'll find all the necessary steps to set up your environment and get started with the installation process of Anaconda.</span>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.markdown("""<br>""", unsafe_allow_html=True)
                    
                if st.button("Launch", 6, use_container_width = True, type = "primary"):
                    st.switch_page("InstallationGuidePage/InstallationGuide.py")



        
    shome1, shome2, shome3 = st.columns([0.3, 3, 0.3])
    with shome2:
        st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)    
        st.markdown(
            """
            <div style="
                background-color: #D3D3D3;;
                padding: 6px;
                border-radius: 10px;
                text-align: center;
                font-family: Arial, sans-serif;
                box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.2);
            ">
                <h1 style="font-size: 20px; margin-bottom: 10px; font-weight: bold; letter-spacing: 3px; text-transform: capitalize;">
                    Starter Apps
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        
    m0, m1, m2, m3, m4 = st.columns([0.3, 1,1,1,0.3])
    with m1:
        with st.container(border = True, height=550):
            st.markdown("""<br>""", unsafe_allow_html=True)
            m11, m12, m13 = st.columns([0.7,1,0.7])
            with m12:
                st.image('data/avatar_ai_lpc.png', use_column_width=True)
            m111, m122, m133 = st.columns([0.1,1,0.1])
            with m122:
                ############# Data Science Learning Path Classifier ##############
                st.markdown("""
                            <div style='text-align: center;'>
                                <span style='font-weight:bold; font-size: 16px;'>Data Science Learning Path Classifier</span>
                            </div>
                            """,
                            unsafe_allow_html=True)
                ############# DESCRIPTION
                st.markdown("""
                            <div style='text-align: center;'>
                                <span style='font-size: 14px;'><br>Find your ideal data science path! Our tool analyzes your background and preferences to recommend whether the 
                            Eskwelabs Data Science Fellowship, Data Analytics Bootcamp, or another learning option is right for you. Get guidance tailored to your goals.</span>
                            </div>
                            """, unsafe_allow_html=True)
                st.markdown("""<br>""", unsafe_allow_html=True)
            
            if st.button("Launch", 1,use_container_width = True, type = "primary"):
                st.switch_page("suitability/DSLPC.py")

    
    with m2:
        with st.container(border = True, height=550):
            st.markdown("""<br>""", unsafe_allow_html=True)
            m21, m22, m23 = st.columns([0.7,1,0.7])
            with m22:
                st.image('data/avatar_ai_pi.png', use_column_width=True)
            m211, m222, m233 = st.columns([0.1,1,0.1])
            with m222:
                ############# Program Information Bot ##############
                st.markdown("""
                            <div style='text-align: center;'>
                                <span style='font-weight:bold; font-size: 16px;'>Program Information Bot</span>
                            </div>
                            """,
                            unsafe_allow_html=True)
                ############# DESCRIPTION
                st.markdown("""
                            <div style='text-align: center;'>
                                <span style='font-size: 14px;'><br>This AI-powered assistant chatbot is designed to help you with ideas, advice, and questions that 
                                you may have to understand all aspects of the Eskwelabs DSF program.</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("""<br>""", unsafe_allow_html=True)
                
            if st.button("Launch", 2,use_container_width = True, type = "primary"):
                st.switch_page("Program_Information/pi_app.py")
    with m3:
        with st.container(border = True, height=550):
            st.markdown("""<br>""", unsafe_allow_html=True)
            m31, m32, m33 = st.columns([0.7,1,0.7])
            with m32:
                st.image('data/pathfinder.png', use_column_width=True)
            m311, m322, m333 = st.columns([0.1,1,0.1])
            with m322:
                ############# Program Information Bot ##############
                st.markdown("""
                            <div style='text-align: center;'>
                                <span style='font-weight:bold; font-size: 16px;'>Pathfinder Assessment Report</span>
                            </div>
                            """,
                            unsafe_allow_html=True)
                ############# DESCRIPTION
                st.markdown("""
                            <div style='text-align: center;'>
                                <span style='font-size: 14px;'><br>Get a personalized analysis of your data science skills with 
                                actionable insights. The report highlights your strengths, areas to improve, and guides your learning journey based on your Pathfinder Assessment Exam results.</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("""<br>""", unsafe_allow_html=True)
                
            if st.button("Launch", 3, use_container_width = True, type = "primary"):
                st.switch_page("Pathfinder/feedback_summary.py")  
        
  
        


  

            
 
########################################################################
#    MAIN PROGRAM
########################################################################
#    PAGE DICTIONARY
#    #
########################################################################
role = st.session_state.role

home_page = st.Page(home, title="Home", icon="🏠", default=(role == role))
login_page = st.Page(login, title = "Log In",icon=":material/login:")
logout_page = st.Page(logout, title="Log Out", icon=":material/logout:")
IGP = st.Page("InstallationGuidePage/InstallationGuide.py", title = "Installation Guide", icon = "📦") # 📑
pathfinder_rfs = st.Page("Pathfinder/feedback_summary.py", title="Pathfinder Assessment Report", icon="📝") # 📓
# DSF = st.Page("DSF/app.py", title = "DSF Program Information", icon = "📗")
DSFBA = st.Page("DSFBAssistant/DSFBootcampAssistant.py", title = "Your Bootcamp Assistant", icon = "🤖") # 📗
CO = st.Page("CourseOutline/CourseOutline.py", title = "Course Outline", icon = "📍")
pathfinder_rfs_ops = st.Page("Ops/PARGenerator.py", title="PAR Generator", icon="📊")
CO_ops = st.Page("Ops/COGenerator.py", title="CCO Generator", icon="🗂️") # 📖 

suitability = st.Page(
    "suitability/DSLPC.py",
    title="Start Your Data Journey",
    icon="🚀", # ➕
)
ProgramInformation = st.Page(
    "Program_Information/pi_app.py", title="Program Information", icon="📚" # ⚕️
)



main_apps = [home_page, suitability, ProgramInformation, pathfinder_rfs]
log_in = [login_page]
log_out = [logout_page]
data_apps = []
dsf_apps = [CO,DSFBA,IGP]
pf_apps = []
ops_apps = [pathfinder_rfs_ops, CO_ops]
st.logo(
    "data/EskwelApps.png"#,
    # icon_image= "data/logo.png",
)

page_dict = {}
if st.session_state.role in [None, "Fellow", "Mentor","Ops","Fellow (Developer)"]:
    page_dict["Main"] = main_apps
# if st.session_state.role in [None,"Aspiring Student", "Fellow", "Mentor"]:
#     page_dict["PathFinder"] = pf_apps
if st.session_state.role in [None,"Fellow","Mentor","Ops","Fellow (Developer)"]:
    page_dict["Data Science Fellowship"] = dsf_apps
if st.session_state.role in [None,"Fellow", "Mentor","Ops","Fellow (Developer)"]:
    page_dict["Ops"] = ops_apps

if st.session_state.role in ["Fellow", "Mentor", "Ops","Fellow (Developer)"]:
    account_apps = log_out
elif st.session_state.role in [None]:
    account_apps = log_in


if len(page_dict) > 0:
    pg = st.navigation(page_dict | {"Main": account_apps + main_apps}, position="sidebar")
else:
    pg = st.navigation([st.Page(login)], position="sidebar") #defaults to login page if no acceptable role is selected

pg.run()


        # st.markdown(
        #     """
        #     <div style="
        #         background: linear-gradient(90deg, #009688, #3F51B5);
        #         padding: 40px;
        #         border-radius: 10px;
        #         text-align: center;
        #         font-family: Arial, sans-serif;
        #         color: white;
        #     ">
        #         <h1 style="font-size: 28px; margin-bottom: 10px; font-weight: bold; letter-spacing: 2px; color: white;">
        #             Ready For The Future Of Work?
        #         </h1>
        #         <p style="font-size: 18px; line-height: 1.5; letter-spacing: 1.5px; color: white;">
        #             Learn data skills for digital jobs through our online cohort-based courses. 
        #             <strong>Your Future is Bright!</strong> Eskwelabs is an online upskilling school that gives you access to affordable 
        #             and high-quality data skills education. <strong>Your Future Begins with Upskilling.</strong> Eskwelabs creates a warm online atmosphere for 
        #             a community of students to learn. We mix live sessions, projects, and mentorship to help you achieve your goals.
        #         </p>
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )
        
