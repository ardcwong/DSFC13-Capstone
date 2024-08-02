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
    page_title = "Welcome to Eskwelabs App!",
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
@st.cache(allow_output_mutation=True)
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
    
if "spreadsheet" not in st.session_state:
    # Google Sheets setup using st.secrets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    st.session_state.spreadsheet = google_connection(client)



def login():
    
        

        st.subheader("Get Started")
        st.markdown("Let us know who's visiting. Are you a/an ...")
        col21, col22, col23 = st.columns([1,1,1])
        
        
        def role_chosen():
            a = col21.button("Aspiring Student", type = "primary", use_container_width = True)
            b = col22.button("Fellow", type = "primary", use_container_width = True)
            c = col23.button("Mentor", type = "primary", use_container_width = True)
            if a:
                role = "Aspiring Student"
            elif b:
                role = "Fellow"
            elif c:
                role = "Mentor"
            else: 
                role = []
            return role
        role = role_chosen()
       
        
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
            
 
def logout():
    # st.session_state = None
    st.session_state.role = None
    st.session_state.vote = None
    st.rerun()


def medinfohubplus():
    col1, col2, col3 = st.columns([1,8,1])
    
    # col2.image('data/mihplus.png') #                     !!!!ESKWELABS APP IMAGE!!!
    with col2:
        
        st.markdown(f"<h1 style='text-align: center;'>WELCOME TO ESKWELABS APP✨</h1>", unsafe_allow_html=True)
        st.divider()
        st.markdown("""<h4 style='text-align: center;color: #e76f51;'><b><i>Welcome to Eskwelabs App.</b></i><i> Ready for the Future of Work? 
        Learn data skills for digital jobs through our online cohort-based courses. Your Future is Bright! Eskwelabs is an online upskilling school 
        that gives you access to affordable and high quality data skills education. Your Future Begins with Upskilling. Eskwelabs creates a warm 
        online atmosphere for a community of students to learn. We mix live sessions, projects, and mentorship to help you achieve your goals.""", unsafe_allow_html=True)
        
        st.divider()
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

  
@st.dialog("Log In",width="large")
def vote(role, spreadsheet):
    sheet_fellow = spreadsheet.worksheet("Sheet1")
    sheet_mentor = spreadsheet.worksheet("Sheet2")
    users_fellow = pd.DataFrame(sheet_fellow.get_all_records())
    users_mentor = pd.DataFrame(sheet_mentor.get_all_records())

    if role in ["Fellow"]:
        sheet = sheet_fellow
        user = users_fellow
    elif role in ["Mentor"]:
        sheet = sheet_mentor
        user = users_mentor

        
    
    # Function to check login
    def check_login(username, password, sheet, user):    
        users = pd.DataFrame(sheet.get_all_records())
        if username in users['Username'].values:
            st.session_state.username_exist = True
            if password == str(users[users['Username'] == username]['Password'].values[0]):
                return True
        return False
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        
        if check_login(username, password, sheet, user):
            st.success("Login successful!")
            st.session_state.vote = {"role": role}
            st.session_state.role = st.session_state.vote['role']
            st.rerun()
        else:
            st.error("Invalid username or password")
            
 
########################################################################
#    MAIN PROGRAM
########################################################################
#    PAGE DICTIONARY
#    #
########################################################################
role = st.session_state.role


login_page = st.Page(login, title = "Welcome",icon=":material/login:")
logout_page = st.Page(logout, title="End Session", icon=":material/logout:")
medinfohubplus_info = st.Page(medinfohubplus, title="About Our Data App", icon="📱", default=(role == role))
# role_print = st.Page(role_print_none,title=role)

# settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
suitability = st.Page(
    "suitability/DSLPC.py",
    title="Data Science Learning Path Classifier",
    icon="➕",
)
fda_app = st.Page(
    "FDA/fda_app.py", title="PharmaPal", icon="⚕️"
)

about_us_pages = [login_page, medinfohubplus_info]
account_pages = [logout_page]
data_apps = [suitability, fda_app]

st.logo(
    "data/mihplus.png"#,
    # icon_image= "data/logo.png",
)

page_dict = {}

if st.session_state.role in [None,"Aspiring Student", "Fellow", "Mentor"]:
    page_dict["Application"] = data_apps
if st.session_state.role in [None,"Aspiring Student", "Fellow", "Mentor"]:
    page_dict["MedInfoHub+"] = about_us_pages


if len(page_dict) > 0:
    pg = st.navigation(page_dict | {"Session": account_pages})
else:
    pg = st.navigation([st.Page(login)]) #defaults to login page if no acceptable role is selected

pg.run()



        
