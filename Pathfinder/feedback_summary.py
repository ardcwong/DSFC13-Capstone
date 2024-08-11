import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
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
def google_connection_gsheet_DerivedCompetencyFramework(client):
    # Open the Google Sheet
    spreadsheet = client.open("Derived Competency Framework")
    return spreadsheet

def google_connection_gsheet_PathfinderExamResults(client):
    # Open the Google Sheet
    spreadsheet = client.open("Pathfinder Exam Results")
    return spreadsheet

########################################################
# ACCESS DERIVED COMPETENCY FRAMEWORK GSHEET
########################################################
if "spreadsheet_DerivedCompetencyFramework" not in st.session_state:
    st.session_state.spreadsheet_DerivedCompetencyFramework = google_connection_gsheet_DerivedCompetencyFramework(client)
########################################################
# ACCESS PATHFINDER EXAM RESULTS GSHEET
########################################################
if "spreadsheet_PathfinderExamResults" not in st.session_state:
    st.session_state.spreadsheet_PathfinderExamResults = google_connection_gsheet_PathfinderExamResults(client)


# Function to load category structure data from Google Sheet
def load_category_structure(spreadsheet):
    worksheet = spreadsheet.worksheet("Sheet1")
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    df['Main Category'] = df['Main Category'].fillna(method='ffill')
    df['Main Category'] = df['Main Category'].str.strip()
    df['Sub-Category'] = df['Sub-Category'].str.strip()
    df['Key Topics'] = df['Key Topics'].str.strip()
    category_structure = {}
    for _, row in df.iterrows():
        main_category = row['Main Category']
        sub_category = row['Sub-Category']
        key_topics = row['Key Topics']
        if main_category not in category_structure:
            category_structure[main_category] = {}
        category_structure[main_category][sub_category] = key_topics.split(',')
    return category_structure

# Function to load the scores dataset from Google Sheet

def load_scores_dataset(spreadsheet):
    worksheet = spreadsheet.worksheet("Sheet1")
    data_score = worksheet.get_all_values()
    df_score = pd.DataFrame(data_score[1:], columns=data_score[0])
    return df_score

# Load the data
category_structure = load_category_structure(st.session_state.spreadsheet_DerivedCompetencyFramework)
scores_dataset = load_scores_dataset(st.session_state.spreadsheet_PathfinderExamResults)
# st.write(category_structure)
# st.write(scores_dataset.head())


if "generate_pf_fs" not in st.session_state:
    st.session_state.generate_pf_fs = False
if "reference_number" not in st.session_state:
    st.session_state.reference_number = []
if "feedback_generated" not in st.session_state:
    st.session_state.feedback_generated = []

pf_rn_y = scores_dataset["Reference Number"][scores_dataset["PARGenTag"] == "Y"].tolist()

if st.session_state.generate_pf_fs == False:
    # Input for reference number

    column11, column12, column13 = st.columns([2,6,2])  
    with column12:
        st.markdown("")
        st.markdown("")
        with st.container():
            reference_number = st.chat_input("Enter your Reference Number:")
            st.session_state.reference_number = reference_number
            # st.write(st.session_state.reference_number)
            # st.write(pf_rn_y.tolist())
            if st.session_state.reference_number is not []:
        # if st.button("My Pathfinder Assessment Exam Report", use_container_width = True, type = "primary"):
                
                if st.session_state.reference_number in pf_rn_y:
                    st.session_state.generate_pf_fs = True
                    st.rerun()
                else:
                    st.error("Reference Number not found.")
                    st.session_state.generate_pf_fs = False
                    st.session_state.reference_number = []
                    # st.rerun()

else:

    if st.button("Go Back", type = "primary"):
        st.session_state.generate_pf_fs = False
        st.session_state.reference_number = []
        st.session_state.feedback_generated = []
        st.rerun()
    
    
    
    column__1, column__2 = st.columns([2,8])
    with column__2:

        pf_rn_y = scores_dataset["Reference Number"][scores_dataset["PARGenTag"] == "Y"].tolist()

    with column__1:
        
        if scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]['HTML_CONTENT'].values[0] is not "":
            download_disabled = False
        else:
            download_disabled = True

        pdf = convert_html_to_pdf(scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]['HTML_CONTENT'].values[0])
        if pdf:
            st.download_button(label=f"Download PDF (**{reference_number_ops_view}**)", data=pdf, file_name="PAR.pdf", mime="application/pdf", use_container_width = True, disabled = download_disabled, help = "Download PAR")
        else:
            st.error("Failed to convert HTML to PDF.")
    
    with st.container(border=True):
        column_1, column_2, column_3 = st.columns([1,8,1])     
        with column_2:
            st.markdown(scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]['REPORT_INTRO'].values[0], unsafe_allow_html=True)
            st.markdown(scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]['SCORE_CATEGORY_TABLE'].values[0], unsafe_allow_html=True)
            for i in range(9):
                st.markdown(scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number][f"FEEDBACK_SECTION_{i+1}"].values[0], unsafe_allow_html=True)


