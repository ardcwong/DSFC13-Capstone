import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

st.set_page_config(layout='wide')
credentials = st.secrets["gcp_service_account"]

if "role" not in st.session_state:
    st.session_state.role = None

if "vote" not in st.session_state:
    st.session_state.vote = None

   
ROLES = ["Aspiring Student", "Fellow", "Mentor"]


        
def login():
    col1, col2, col3 = st.columns([1,3,1])
    
    # col2.image('data/mihplus.png') #                     !!!!ESKWELABS APP IMAGE!!!

    col2.header("ESKWELABS APP")
    # col1.image('data/art.png')
    # st.header("Log in")
    content = """
    Welcome to Eskwelabs App. Ready for the Future of Work? Learn data skills for digital jobs through our online cohort-based courses. Your Future is Bright! Eskwelabs is an online upskilling school that gives you access to affordable and high quality data skills education.
    Your Future Begins with Upskilling. Eskwelabs creates a warm online atmosphere for a community of students to learn. We mix live sessions, projects, and mentorship to help you achieve your goals.
    """
    col2.markdown(content, unsafe_allow_html=True)

    col2.subheader("Get Started")
    col2.markdown("Let us know who's visiting. Are you a/an ...")
    with col2:
        col21, col22, col23 = st.columns([1,1,1])
        def role_chosen():
            if col21.button("Aspiring Student", type = "primary", use_container_width = True):
                role = "Aspiring Student"
            elif col22.button("Fellow", type = "primary", use_container_width = True):
                role = "Fellow"
            elif col23.button("Mentor", type = "primary", use_container_width = True):
                role = "Mentor"
            else: 
                role = []
            return role
        role = role_chosen()
       
        
        if st.session_state.vote == None: 
            

            if role in ["Aspiring Student"]:
                st.session_state.vote = {"role": role}
                st.session_state.role = st.session_state.vote['role']
                st.rerun()
            elif role in ["Fellow", "Mentor"]:
                vote(role)
            # elif role == []:
                
        else:
            st.session_state.role = st.session_state.vote['role']
                
            
 
def logout():
    # st.session_state = None
    st.session_state.role = None
    st.session_state.vote = None
    st.rerun()

def contactus():
    st.title('MedInfoHub+')
    # st.subheader("WHAT WE OFFER")
    # st.image('data/use.png')
    st.subheader("CONTACT US")
    st.write('For any concerns or suggestions, you may reach out to us through the following:')
    contactinfo = """
    Email us:
    General Inquiries: info@medinfohub.com<br>
    Support: support@medinfohub.com<br>

    Follow us on Social Media Platforms:<br>
    Facebook: facebook.com/medinfohub<br>
    Twitter: twitter.com/medinfohub<br>
    Instagram: instagram.com/medinfohub
    """
    # Display formatted text with st.markdown
    st.markdown(contactinfo, unsafe_allow_html=True)
def medinfohubplus():
    st.markdown(f"<h1 style='text-align: center;'>Welcome to MedInfoHub+, {role} ✨</h1>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h4 style='text-align: center;color: #e76f51;'><b><i>MedInfoHub</b></i><i> is your ultimate resource for accessible, reliable, and easy-to-understand medical information. Our platform is designed to enhance public health literacy, advocate telemedicine consultations, and bridge the gap between drug knowledge and patient understanding. MedInfoHub+ features two powerful applications: HealthPlus and PharmaPal.</i></h4>", unsafe_allow_html=True)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕HealthPlus")
        st.markdown("***Empowering you with reliable medical knowledge***")
        st.markdown("HealthPlus leverages the power of the MedQuAD dataset and advanced AI to provide you with accurate and easy-to-understand medical information. Our goal is to make healthcare information accessible to everyone, enhancing public health literacy and advocating telemedicine consultations.")
        

    with col2:
        st.subheader("⚕️PharmaPal")
        st.markdown("***Bridging the gap between drug knowledge and patient understanding***")
        st.markdown("PharmaPal is an innovative Streamlit application designed to bridge the gap between drug knowledge and patient understanding. Leveraging the power of the FDA Dataset through the Retrieval-Augmented Generation (RAG), this app provides clear, reliable, and accessible information about the drug that is tailor-fit on the user profile, whether a healthcare provider or a patient.")
 
    col3, col4 = st.columns(2)
    if col3.button('HealthPlus', type = "primary", use_container_width = True):
        st.switch_page("MedQuAd/medquad.py")
    if col4.button('PharmaPal', type = "primary", use_container_width = True):
        st.switch_page("FDA/fda_app.py")

  
@st.dialog("❗Important Reminder",width="large")
def vote(role):
    # Google Sheets setup using st.secrets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    
    # Open the Google Sheet
    sheet = client.open("LoginCredentials").sheet1
    users = pd.DataFrame(sheet.get_all_records())
    st.write(users['Username'])
    
    st.write(pd.DataFrame(sheet.get_all_records()))
    # Function to check login
    def check_login(username, password):
        users = pd.DataFrame(sheet.get_all_records())
        if username in users['Username'].values:
            st.session_state.username_exist = True
            if password == str(users[users['Username'] == username]['Password'].values[0]):
                st.write("Correct")
                return True
        return False
    
    # Streamlit app
    st.title("Login Page")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if check_login(username, password):
            st.success("Login successful!")
            st.session_state.vote = {"role": role}
            st.session_state.role = st.session_state.vote['role']
            st.rerun()
        else:
            st.error("Invalid username or password")
            
    # agree = st.checkbox("I acknowledge that I understand the importance of consulting a healthcare professional.")
   
    # if st.button("Enter MedInfoHub+", type = "primary"):
    #     if agree:
    #         st.session_state.vote = {"role": role}
    #         st.session_state.role = st.session_state.vote['role']
    #         st.rerun()
    #     else: 
    #         st.error("It is important to acknowledge the need for professional medical advice.")











    
    # st.markdown("""While our app provides information about illnesses and medications, it is not a substitute for professional medical advice. Self-medicating can be dangerous and may lead to serious health issues. 
    # Always consult a healthcare professional before starting or changing any medication. <br><br>If you are experiencing symptoms, please seek medical advice from a qualified healthcare provider. 
    # For your convenience, we have partnered with trusted clinics. <br><br>Find a Partner Clinic Here.""", unsafe_allow_html=True
    #            )
    # col1, col2, col3 = st.columns(3)
    # col1.link_button("Now Serving", "https://nowserving.ph", use_container_width = True)
    # col2.link_button("Konsulta MD", "https://konsulta.md/", use_container_width = True)
    # col3.link_button("SeriousMD", "https://seriousmd.com/healthcare-super-app-philippines", use_container_width = True)
    








#----------------------------------------------------------------------------------------------------------------------------

role = st.session_state.role



logout_page = st.Page(logout, title="End Session", icon=":material/logout:")
about_us = st.Page(contactus, title="Contact Us", icon="✉️")
medinfohubplus_info = st.Page(medinfohubplus, title="About Our Data App", icon="📱", default=(role == role))
# role_print = st.Page(role_print_none,title=role)

# settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
medquad = st.Page(
    "MedQuAd/medquad.py",
    title="HealthPlus",
    icon="➕",
)
fda_app = st.Page(
    "FDA/fda_app.py", title="PharmaPal", icon="⚕️"
)

about_us_pages = [medinfohubplus_info,about_us]
account_pages = [logout_page]
data_apps = [medquad, fda_app]

st.logo(
    "data/mihplus.png",
    icon_image= "data/logo.png",
)

page_dict = {}

if st.session_state.role in ["Aspiring Student", "Fellow", "Mentor"]:
    page_dict["Application"] = data_apps
if st.session_state.role in ["Aspiring Student", "Fellow", "Mentor"]:
    page_dict["MedInfoHub+"] = about_us_pages


if len(page_dict) > 0:
    pg = st.navigation(page_dict | {"Session": account_pages})
else:
    pg = st.navigation([st.Page(login)]) #defaults to login page if no acceptable role is selected

pg.run()
