import streamlit as st
import openai
from openai import OpenAI
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from xhtml2pdf import pisa
from io import BytesIO
########################################################
# API KEYS and CREDENTIALS
########################################################
api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
client = gspread.authorize(creds)

with st.sidebar:
  # Call this function to load test answers at the beginning of your app (or when you need to test)
  st.image('data/John.png', use_column_width=True)
  st.markdown(
      """
      <div style="font-family: 'Arial', sans-serif; padding: 10px; background-color: #f9f9f9; border-radius: 10px; border: 1px solid #ddd;">
          <p style="font-size: 11px; color: #333;">
              John is now officially enrolled in the Data Science Fellowship, and EskwelApps continues to support him. One of the first things he accesses is the Course Outline.
              The Course Outline is more than just a list of topics—it’s a roadmap. It’s divided into structured sprints, each with specific subtopics and <strong>learning objectives</strong>. John sees that the 
              first sprint will dive deep into machine learning, exactly what he’s been looking forward to. The outline also recommends <strong>datasets</strong> he can use for hands-on practice, ensuring he’s 
              not just learning but also applying his knowledge.
          </p>
      </div>
      """,
      unsafe_allow_html=True
  )


# Function to collect all markdowns into a single HTML content block
def collect_all_markdowns(markdowns):
    html_content = ""
    for sprint, sprint_markdown in markdowns.items():
        html_content += sprint_markdown
    return html_content
    
# Function to convert HTML content to PDF
def convert_html_to_pdf(html_content):
    # Embed CSS for margins
    # Embed CSS for scaling and margins
    html_with_styles = f"""
    <html>
    <head>
        <style>
            @page {{
                margin: 0.3in; /* Set margins */
            }}
            body {{
                transform: scale(0.5); /* Scale content */
                transform-origin: top left; /* Scale from top-left corner */
                width: 200%; /* Increase body width to handle scaling */
                overflow-wrap: break-word; /* Ensure long words break to fit */
                word-wrap: break-word; /* Compatibility for older browsers */
            }}
            p {{
                margin: 0; /* Remove default margins */
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    result = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(html_with_styles.encode("utf-8")), dest=result)
    if pisa_status.err:
        return None
    return result.getvalue()

# Google Sheets connection function
def google_connection_gsheet_courseoutline_ops(client):
    # Open the Google Sheet
    spreadsheet = client.open("Data Science Fellowship Curriculum")
    return spreadsheet


def load_course_outline_dataset(spreadsheet):
    worksheet = spreadsheet.worksheet("Data Science Fellowship Cohort")
    data_score = worksheet.get_all_values()
    df_co = pd.DataFrame(data_score[1:], columns=data_score[0])
    return df_co
########################################################
# ACCESS Data Science Fellowship Curriculum GSHEET
########################################################
if "spreadsheet_courseoutline_ops" not in st.session_state:
    st.session_state.spreadsheet_courseoutline_ops = google_connection_gsheet_courseoutline_ops(client)

df_co = load_course_outline_dataset(st.session_state.spreadsheet_courseoutline_ops)

########################################################
# MAIN PROGRAM
########################################################
# st.image('data/Course_Outline.svg', use_column_width = True)
if st.session_state.role == None:
    role_co = "!"
elif st.session_state.role == []:
    role_co = "!"
else:
    role_co = f", {st.session_state.role}!"

st.markdown(
    f"""
    <div style="
        background: linear-gradient(90deg, #009688, #3F51B5);
        padding: 40px;
        border-radius: 10px;
        text-align: center;
        font-family: Arial, sans-serif;
        color: white;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
    ">
        <h1 style="font-size: 48px; margin-bottom: 10px; font-weight: bold; letter-spacing: 2px; color: white;">
            Welcome to the Course Outline Page{role_co}🤓
        </h1>
    </div>
    """,
    unsafe_allow_html=True)
st.markdown(
    """
    <div style="
        background-color: #FFFFFF;
        padding: 6px;
        border-radius: 10px;
        text-align: center;
        font-family: Arial, sans-serif;
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.2);
    ">
        This page is designed to <span style='color:#54afa7; font-weight:bold;'>provide you with a comprehensive overview of our bootcamp</span> to guide you through each phase of your learning journey. 
        Whether you're a beginner or looking to advance your skills, our structured outline will help you <span style='color:#54afa7; font-weight:bold;'>navigate the curriculum, track your progress, and make the most out of your bootcamp experience.</span>
        <br><br>Ready for more challenges? Embrace the learning process with our <span style='text-decoration:underline; color:#54afa7;'>dataset recommendations</span> for each sprint, designed to offer practical, hands-on experiences. Remember, <span style='font-weight:bold; color:#54afa7;'> 
        the best lessons come from the mistakes you make along the way—each one is a step closer to mastery.</span>
        <br>Dive in to see what’s in store and get ready to embark on a transformative learning adventure, <span style='color:#54afa7; font-weight:bold;'>Best of luck!<br></span>
    </div>
    """,
    unsafe_allow_html=True
)
        # <span style='font-weight:bold; font-size: 20px'>
        #     Welcome to the Course Outline Page, Fellow! 🤓 
        # </span>
# st.title("Course Outline")
# st.markdown("""
# <span style='font-weight:bold; font-size: 20px'>Welcome to the Course Outline Page, Fellow! 🤓 </span>
# <br>This page is designed to <span style='color:#54afa7; font-weight:bold;'>provide you with a comprehensive overview of our bootcamp</span> to guide you through each phase of your learning journey. Whether you're a beginner or looking to advance your skills, our structured outline will help you <span style='color:#54afa7; font-weight:bold;'>navigate the curriculum, track your progress, and make the most out of your bootcamp experience.</span>
# <br>Dive in to see what’s in store and get ready to embark on a transformative learning adventure, <span style='color:#54afa7; font-weight:bold;'>Best of luck!<br></span>
# """, unsafe_allow_html=True) 
st.markdown("""<br>""", unsafe_allow_html=True) 

# st.markdown("""
# <div style='text-align:center;'>
#     <span style='font-weight:bold; font-size: 35px;'>Data Science Fellowship Course Outline</span>
# </div>
# """, unsafe_allow_html=True)

with st.sidebar:
    st.session_state.get_current_markdown_co = df_co[df_co['Sprint Number'] == f"Sprint 1"]['Full HTML_CONTENT'].values[0]    
        
    # st.markdown(st.session_state.get_current_markdown, unsafe_allow_html=True)     
    pdf_current = convert_html_to_pdf(st.session_state.get_current_markdown_co)
    if pdf_current:
        st.download_button(label=f"Download PDF (Current CO)", data=pdf_current, file_name="Course_Outline.pdf", mime="application/pdf", use_container_width = True)
    else:
        st.error("Failed to convert HTML to PDF.")


for i in range(4):
    st.markdown(df_co[df_co['Sprint Number'] == f"Sprint {i+1}"]['Enhanced Course Outline'].values[0], unsafe_allow_html=True)
