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
def home_main_content():
    home1, home2, home3 = st.columns([0.3, 3, 0.3])
    with home2:
        st.markdown(f"<h1 style='text-align: center;'>WELCOME TO ESKWELAPPS✨</h1>", unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("""<div style='text-align: center;'>
                            <span style='font-size: 16px;'<b><i>Welcome to EskwelApps.</b></i><i> Ready for the Future of Work? 
                            Learn data skills for digital jobs through our online cohort-based courses. Your Future is Bright! Eskwelabs is an online upskilling school 
                            that gives you access to affordable and high quality data skills education. Your Future Begins with Upskilling. Eskwelabs creates a warm 
                            online atmosphere for a community of students to learn. We mix live sessions, projects, and mentorship to help you achieve your goals.</span>
                    </div>        
                    """, unsafe_allow_html=True)
            
        st.divider()
        
    m0, m1, m2, m3, m4 = st.columns([0.3, 1,1,1,0.3])
    with m1:
        with st.container(border = True):
            m11, m12, m13 = st.columns([1,1,1])
            with m12:
                st.image('data/avatar_ai.png', use_column_width=True)
                
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
            if st.button("Launch", 1,use_container_width = True, type = "primary"):
                st.switch_page("suitability/DSLPC.py")

    
    with m2:
        with st.container(border = True):
            m21, m22, m23 = st.columns([0.5,1,0.5])
            with m22:
                st.image('data/avatar_ai_pi.png', use_column_width=True)
            st.markdown("""<h4 style= 'text-align: center;'>Program Information Bot<h/4>""", unsafe_allow_html=True)
            st.markdown("""<h5 style= 'text-align: center;'>Start Your Journney! An intelligent bot that classifies the most appropriate learning path for your Data Science Journey!</h5>""", unsafe_allow_html = True)
            if st.button("Launch", 2,use_container_width = True, type = "primary"):
                st.switch_page("Program_Information/pi_app.py")
    with m3:
        with st.container(border = True):
            m31, m32, m33 = st.columns([1,1,1])
            with m32:
                st.image('data/avatar_ai_lpc.png', use_column_width=True)
            st.markdown("""<h4 style= 'text-align: center;'>Pathfinder Assessment Report<h/4>""", unsafe_allow_html=True)
            st.markdown("""<h5 style= 'text-align: center;'>Pathfinder Assessment Report</h5>""", unsafe_allow_html = True)
            if st.button("Launch", 3, use_container_width = True, type = "primary"):
                st.switch_page("Pathfinder/feedback_summary.py")
def home():
    
        
        
        
        
        
        
        
        
        
        
        
    col1, col2, col3 = st.columns([1,8,1])
    
    # col2.image('data/mihplus.png') #                     !!!!ESKWELABS APP IMAGE!!!
    with col2:
        if st.session_state.userinfo is not None:
            
            
            st.title(f"Hi, {str(st.session_state.userinfo['FirstName'].values[0])}!")
            st.subheader("We added these specific apps for you!")
    home_main_content()
        

        # col1.image('data/art.png')
        # st.header("Log in")
       
    
    
    
    # st.markdown(f"<h1 style='text-align: center;'>WELCOME TO ESKWELABS APP✨</h1>", unsafe_allow_html=True)
    # st.divider()
    
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.subheader("➕HealthPlus")
    #     st.markdown("***Empowering you with reliable medical knowledge***")
    #     st.markdown("HealthPlus leverages the power of the MedQuAD dataset and advanced AI to provide you with accurate and easy-to-understand medical information. Our goal is to make healthcare information accessible to everyone, enhancing public health literacy and advocating telemedicine consultations.")
        

    # with col2:
    #     st.subheader("⚕️PharmaPal")
    #     st.markdown("***Bridging the gap between drug knowledge and patient understanding***")
    #     st.markdown("PharmaPal is an innovative Streamlit application designed to bridge the gap between drug knowledge and patient understanding. Leveraging the power of the FDA Dataset through the Retrieval-Augmented Generation (RAG), this app provides clear, reliable, and accessible information about the drug that is tailor-fit on the user profile, whether a healthcare provider or a patient.")
 
    # col3, col4 = st.columns(2)
    # if col3.button('HealthPlus', type = "primary", use_container_width = True):
    #     st.switch_page("MedQuAd/medquad.py")
    # if col4.button('PharmaPal', type = "primary", use_container_width = True):
    #     st.switch_page("FDA/fda_app.py")

  

            
 
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
    title="Start Your Journey",
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
    "data/Eskwelabs_logo.svg"#,
    # icon_image= "data/logo.png",
)

page_dict = {}
if st.session_state.role in [None,"Aspiring Student", "Fellow", "Mentor"]:
    page_dict["Main"] = main_apps
# if st.session_state.role in [None,"Aspiring Student", "Fellow", "Mentor"]:
#     page_dict["PathFinder"] = pf_apps
if st.session_state.role in [None,"Fellow"]:
    page_dict["Data Science Fellowship"] = dsf_apps
if st.session_state.role in [None,"Aspiring Student", "Fellow", "Mentor"]:
    page_dict["Ops"] = ops_apps

if st.session_state.role in ["Fellow", "Mentor", "Ops"]:
    account_apps = log_out
elif st.session_state.role in [None]:
    account_apps = log_in


if len(page_dict) > 0:
    pg = st.navigation(page_dict | {"Main": account_apps + main_apps}, position="sidebar")
else:
    pg = st.navigation([st.Page(login)], position="sidebar") #defaults to login page if no acceptable role is selected

pg.run()



        
