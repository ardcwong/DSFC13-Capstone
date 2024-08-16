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


########################################################
##### Function to convert HTML content to PDF
########################################################
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


########################################################
##### Google Sheets connection function
########################################################
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



########################################################
# Function to load category structure data from Google Sheet
########################################################
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


########################################################
# Function to load the scores dataset from Google Sheet
########################################################
def load_scores_dataset(spreadsheet):
    worksheet = spreadsheet.worksheet("Sheet1")
    data_score = worksheet.get_all_values()
    df_score = pd.DataFrame(data_score[1:], columns=data_score[0])
    return df_score

#################
# Load the data
#################
category_structure = load_category_structure(st.session_state.spreadsheet_DerivedCompetencyFramework)
scores_dataset = load_scores_dataset(st.session_state.spreadsheet_PathfinderExamResults)



if "generate_pf_fs" not in st.session_state:
    st.session_state.generate_pf_fs = False
if "reference_number" not in st.session_state:
    st.session_state.reference_number = []
if "feedback_generated" not in st.session_state:
    st.session_state.feedback_generated = []

pf_rn_y = scores_dataset["Reference Number"][scores_dataset["PARGenTag"] == "Y"].tolist()



if st.session_state.generate_pf_fs == False:
    # st.title("Pathfinder Assessment Report")
    # st.image('data/PAR.svg', use_column_width = True)
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
            <h1 style="font-size: 60px; margin-bottom: 10px; font-weight: bold; letter-spacing: 2px; color: white; text-transform: capitalize;">
                Pathfinder Assessment Report
            </h1>
        </div>
        """,
        unsafe_allow_html=True)
    st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)

    
    col_main1, col_main2 = st.columns([1,2.5])
    with col_main1:
        with st.expander("# **About**", expanded=True):
            st.write("The 'Pathfinder Assessment Report' feature of our app provides a comprehensive performance overview after completing the Pathfinder Exam. This report helps you identify your strengths and weaknesses across different topic areas, allowing you to pinpoint knowledge gaps that need improvement. Along with the performance summary, the app offers personalized suggestions to help you bridge those gaps, guiding you on the next steps in your learning journey.")
        with st.expander("**View Report**", expanded =True):
                
            reference_number = st.chat_input("Enter your Reference Number:")
            if reference_number:
                st.session_state.reference_number = reference_number

                if st.session_state.reference_number in pf_rn_y:
                    st.session_state.generate_pf_fs = True
                    st.rerun()
                    
                else:
                    st.error(f"Reference Number {st.session_state.reference_number} not found. Either it doesn't exist or your Pathfinder Assessment Report (PAR) is not yet generated.")
                    st.session_state.generate_pf_fs = False
                    st.session_state.reference_number = []
                    reference = []
                    # st.rerun()
    with col_main2:
        with st.expander("# **Instructions**", expanded=True):
            st.markdown("""
            1. **Complete the Pathfinder Exam:**  
               Before accessing the Pathfinder Assessment Report, you must first complete the Pathfinder Exam.
            
            2. **Receive Your Reference Number:**  
               After completing the exam, a reference number will be sent to you by the Eskwelabs team.  
               Keep this reference number handy, as you will need it to access your report.
            
            3. **View Your Performance Summary:**  
               Once you have received your reference number, navigate to this section in the app.  
               Enter the reference number to access a detailed breakdown of your scores across various topic areas, highlighting both your strengths and areas that need further attention.
            
            4. **Review Suggestions for Improvement:**  
               Along with your performance summary, the app will provide tailored suggestions aimed at helping you improve in the areas where you scored lower.  
               Follow these suggestions to enhance your understanding and close any knowledge gaps.
            
            5. **Save Your Report:**  
               If desired, you can save your performance summary and suggestions for future reference. This allows you to track your progress over time and revisit the feedback as needed.
            
            6. **Plan Your Next Steps:**  
               Use the feedback and suggestions to plan your next steps in your learning journey. Focus on the areas identified as needing improvement and take advantage of the resources provided by the app.
            """, unsafe_allow_html=True)

else:
    # column11, column22, column33 = st.columns([1,2,1])

    # with column22:
    # st.info(f"Viewing Reference Number {st.session_state.reference_number}")
        # st.markdown(f"""<h6 style='text-align: center; font-weight: bold;'><br>Viewing Reference Number {st.session_state.reference_number}</h6>""", unsafe_allow_html = True)

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
        <h1 style="font-size: 60px; margin-bottom: 10px; font-weight: bold; letter-spacing: 2px; color: white; text-transform: capitalize;">
            Pathfinder Assessment Report<br>for Reference Number {st.session_state.reference_number}
        </h1>
    </div>
    """,
    unsafe_allow_html=True)
    st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)
    with st.sidebar:
        if st.button("Go Back", type = "primary", use_container_width = True, help = "Go Back to PAR main menu."):
            st.session_state.generate_pf_fs = False
            st.session_state.reference_number = []
            st.session_state.feedback_generated = []
            st.rerun()
        pf_rn_y = scores_dataset["Reference Number"][scores_dataset["PARGenTag"] == "Y"].tolist()
        if scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]['HTML_CONTENT'].values[0] != "":
            download_disabled = False
        else:
            download_disabled = True
            
        pdf = convert_html_to_pdf(scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]['HTML_CONTENT'].values[0])
        if pdf:
            st.download_button(label=f"Download PDF (**{st.session_state.reference_number}**)", data=pdf, file_name="PAR.pdf", mime="application/pdf", use_container_width = True, disabled = download_disabled, help = f"Download {st.session_state.reference_number} PAR", type = "primary")
        else:
            st.error("Failed to convert HTML to PDF.")
    
    with st.container(border=True):
        column_1, column_2, column_3 = st.columns([1,8,1])     
        with column_2:
            st.markdown(scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]['REPORT_INTRO'].values[0], unsafe_allow_html=True)
            st.markdown(scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]['SCORE_CATEGORY_TABLE'].values[0], unsafe_allow_html=True)
            for i in range(9):
                st.markdown(scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number][f"FEEDBACK_SECTION_{i+1}"].values[0], unsafe_allow_html=True)


