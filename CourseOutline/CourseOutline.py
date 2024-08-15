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

st.title("Course Outline")
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
