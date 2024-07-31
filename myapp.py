import streamlit as st


st.set_page_config(layout='wide')
# st.config.set_option('client.caching', False)


# col2.write("")

# # col2.write("MedInfoHub is a comprehensive healthcare app designed to provide accessible medical information to patients and healthcare providers. Leveraging the power of the MedQuAD dataset* and advanced AI, MedInfoHub offers reliable answers to medical questions, supports telemedicine consultations, and enhances public health literacy. Whether you’re a patient seeking to understand your health better or a healthcare provider in need of quick, reliable information, MedInfoHub is your go-to resource for trusted medical knowledge.")
# col2.write("*Do you agree that ")
# col2.write("Press the 'Activate MedInfoHub' Button to begin exploring MedInfoHub.")

if "role" not in st.session_state:
    st.session_state.role = None

if "vote" not in st.session_state:
    st.session_state.vote = None
ROLES = ["Patient/Caregiver", "Healthcare Provider"]





@st.experimental_dialog("❗Important Reminder",width="large")
def vote(role):
    st.markdown("""While our app provides information about illnesses and medications, it is not a substitute for professional medical advice. Self-medicating can be dangerous and may lead to serious health issues. 
    Always consult a healthcare professional before starting or changing any medication. <br><br>If you are experiencing symptoms, please seek medical advice from a qualified healthcare provider. 
    For your convenience, we have partnered with trusted clinics. <br><br>Find a Partner Clinic Here.""", unsafe_allow_html=True
               )
    col1, col2, col3 = st.columns(3)
    col1.link_button("Now Serving", "https://nowserving.ph", use_container_width = True)
    col2.link_button("Konsulta MD", "https://konsulta.md/", use_container_width = True)
    col3.link_button("SeriousMD", "https://seriousmd.com/healthcare-super-app-philippines", use_container_width = True)
    
    agree = st.checkbox("I acknowledge that I understand the importance of consulting a healthcare professional.")
   
    if st.button("Enter MedInfoHub+", type = "primary"):
        if agree:
            st.session_state.vote = {"role": role}
            st.rerun()
        else: 
            st.error("It is important to acknowledge the need for professional medical advice.")

        
def login():
    col1, col2, col3 = st.columns([1,3,1])
    
    col2.image('data/mihplus.png')

    col2.header("Welcome to MedInfoHub+!")
    # col1.image('data/art.png')
    # st.header("Log in")
    content = """
    Welcome to MedInfoHub+, your comprehensive source for accessible, reliable, and easy-to-understand medical information. 
    We aim to enhance public health literacy, advocate telemedicine consultations, and bridge the gap between drug knowledge and patient understanding. 
    Whether you’re a patient managing a chronic condition, a caregiver needing clear explanations, a healthcare provider requiring quick and reliable information, or a health enthusiast looking for health tips, MedInfoHub+ is your go-to resource.

    """
    col2.markdown(content, unsafe_allow_html=True)

    col2.subheader("Get Started")
    col2.markdown("To provide you with the best experience, please select your profile:")

    role = col2.radio("I am a ",ROLES, index = None, label_visibility = "collapsed",captions = ["Empowering you with reliable medical knowledge to manage health better and offer clear explanations to care for your loved ones.", "Providing quick access to accurate medical information and resources to support your practice."] )
    # role = col2.selectbox("Choose your role", ROLES)
    if st.session_state.vote == None: 
        
        if col2.button("Next"):
            if role:
                vote(role)
            else:
                col2.error("Please Select Your Profile in order to proceed.")
    else:
        st.session_state.role = st.session_state.vote['role']

    
    
    # col2.button("Enter MedInfoHub+"):
        
        # st.session_state.role = role
        st.rerun()

 
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
    # if st.session_state.role:
    #     # st.markdown("<h5 style='text-align: center;'>Hi, </h5>", unsafe_allow_html=True)
    #     st.markdown(f"""
    #     <div style="text-align: center; background-color: #C4E8F3;padding: 5px; border-radius: 5px; margin-right: 5px;">
    #         Hi, <b>{st.session_state.role}</b>
    #     </div>
    #     """, unsafe_allow_html=True)

    # if st.session_state.role:
    #     st.markdown(f"""
    #     <div style="text-align: center; background-color: #C4E8F3; padding: 5px; border-radius: 5px; margin-right: 5px;">
    #         Hi, <span style="font-weight: bold;">{st.session_state.role}</span>
    #     </div>
    #     """, unsafe_allow_html=True)

    
        
    st.markdown(f"<h1 style='text-align: center;'>Welcome to MedInfoHub+, {role} ✨</h1>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h4 style='text-align: center;color: #e76f51;'><b><i>MedInfoHub</b></i><i> is your ultimate resource for accessible, reliable, and easy-to-understand medical information. Our platform is designed to enhance public health literacy, advocate telemedicine consultations, and bridge the gap between drug knowledge and patient understanding. MedInfoHub+ features two powerful applications: HealthPlus and PharmaPal.</i></h4>", unsafe_allow_html=True)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕HealthPlus")
        st.markdown("***Empowering you with reliable medical knowledge***")
        st.markdown("HealthPlus leverages the power of the MedQuAD dataset and advanced AI to provide you with accurate and easy-to-understand medical information. Our goal is to make healthcare information accessible to everyone, enhancing public health literacy and advocating telemedicine consultations.")
        # st.image('data/healthplus.png')
        

    with col2:
        st.subheader("⚕️PharmaPal")
        st.markdown("***Bridging the gap between drug knowledge and patient understanding***")
        st.markdown("PharmaPal is an innovative Streamlit application designed to bridge the gap between drug knowledge and patient understanding. Leveraging the power of the FDA Dataset through the Retrieval-Augmented Generation (RAG), this app provides clear, reliable, and accessible information about the drug that is tailor-fit on the user profile, whether a healthcare provider or a patient.")
        # st.image('data/pharmapal.png')
        
    col3, col4 = st.columns(2)
    if col3.button('HealthPlus', type = "primary", use_container_width = True):
        st.switch_page("MedQuAd/medquad.py")
    if col4.button('PharmaPal', type = "primary", use_container_width = True):
        st.switch_page("FDA/fda_app.py")

    # st.subheader("WHAT WE OFFER")
    # st.image('data/use.png')
    # st.subheader("CONTACT US")
    # st.write('For any concerns or suggestions, you may reach out to us through the following:')
    # contactinfo = """
    # Facebook: facebook.com/medinfohub
    # Twitter: twitter.com/medinfohub
    # Instagram: instagram.com/medinfohub
    # """
    # # Display formatted text with st.markdown
    # st.markdown(contactinfo, unsafe_allow_html=True)
    
role = st.session_state.role
# def role_print_none():
#     if st.session_state.role:
#         st.sidebar.markdown(f"Hi, {st.session_state.role}")
        
#     return []

# role_print_none()


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

# 👩🏻‍⚕️
# respond_1 = st.Page(
#     "respond/respond_1.py",
#     title="Respond 1",
#     icon=":material/healing:",
#     default=(role == "Responder"),
# )
# respond_2 = st.Page(
#     "respond/respond_2.py", title="Respond 2", icon=":material/handyman:"
# )


# admin_1 = st.Page(
#     "admin/admin_1.py",
#     title="Admin 1",
#     icon=":material/person_add:",
#     default=(role == "Admin"),
# )
# admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")
about_us_pages = [medinfohubplus_info,about_us]
account_pages = [logout_page]
data_apps = [medquad, fda_app]
# user_info = []


# respond_pages = [respond_1, respond_2]
# admin_pages = [admin_1, admin_2]

# st.sidebar.title('MedInfoHub')
# with st.sidebar:
#     # st.subheader("WHAT WE OFFER")
#     # st.image('data/use.png')
#     st.subheader("CONTACT US")
#     st.write('For any concerns or suggestions, you may reach out to us through the following:')
#     contactinfo = """
#     Facebook: facebook.com/medinfohub
#     Twitter: twitter.com/medinfohub
#     Instagram: instagram.com/medinfohub
#     """
#     # Display formatted text with st.markdown
#     st.markdown(contactinfo, unsafe_allow_html=True)
# st.title("Request manager")
# st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")
st.logo(
    "data/mihplus.png",
    icon_image= "data/logo.png",
)

page_dict = {}
# if st.session_state.role in ["Patient/Caregiver", "Healthcare Provider", "Neither"]:
#     page_dict["Hi",role] = user_info
if st.session_state.role in ["Patient/Caregiver", "Healthcare Provider", "Neither"]:
    page_dict["Application"] = data_apps
if st.session_state.role in ["Patient/Caregiver", "Healthcare Provider", "Neither"]:
    page_dict["MedInfoHub+"] = about_us_pages

# if st.session_state.role in ["Responder", "Admin"]:
#     page_dict["Respond"] = respond_pages
# if st.session_state.role == "Admin":
#     page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation(page_dict | {"Session": account_pages})
else:
    pg = st.navigation([st.Page(login)]) #defaults to login page if no acceptable role is selected

pg.run()
