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


with st.sidebar:
  # Call this function to load test answers at the beginning of your app (or when you need to test)
  st.image('data/John.png', use_column_width=True)
  st.markdown(
      """
      <div style="font-family: 'Arial', sans-serif; padding: 10px; background-color: #f9f9f9; border-radius: 10px; border: 1px solid #ddd;">
          <p style="font-size: 11px; color: #333;">
              After applying, John eagerly awaits his Pathfinder Exam results. Once the results are in, he <strong>heads to the Pathfinder Assessment Report page and enters his Reference Number</strong>. 
              He discovers he scored 75% in Pre-Data Science, showing a solid foundation. The report suggests areas for improvement, like advanced Python syntax and data manipulation, 
              giving John clear steps to focus on before the fellowship.
          </p>
      </div>
      """,
      unsafe_allow_html=True
  )






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
    pargen_stats = "Our Pathfinder Assessment Report Generator has a validity rate of 97.78%, ensuring that the insights it provides are closely aligned with the key topics and sub-categories outlined in the 2023 Competency Framework."
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
          width: 500px;
          background-color: #fff;
          color: #333;
          text-align: left; /* Align text to the left */
          border-radius: 5px;
          padding: 10px;
          position: absolute;
          z-index: 1;
          left: 80%; /* Center tooltip horizontally */
          top: -90%; /* Position above the element */
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
        <div style="
            background: linear-gradient(90deg, #009688, #3F51B5);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            font-family: Arial, sans-serif;
            color: white;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
        ">
            <div class='tooltip' style='flex-shrink: 0; width: 100%;'>
                <h1 style="font-size: 60px; margin-bottom: 10px; font-weight: bold; letter-spacing: 2px; color: white; text-transform: capitalize;">
                Pathfinder Assessment Report
                </h1>
                <span class="tooltiptext">{pargen_stats}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    
    # st.markdown(
    #     """
    #     <div style="
    #         background: linear-gradient(90deg, #009688, #3F51B5);
    #         padding: 40px;
    #         border-radius: 10px;
    #         text-align: center;
    #         font-family: Arial, sans-serif;
    #         color: white;
    #         box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
    #     ">
    #         <h1 style="font-size: 60px; margin-bottom: 10px; font-weight: bold; letter-spacing: 2px; color: white; text-transform: capitalize;">
    #             Pathfinder Assessment Report
    #         </h1>
    #     </div>
    #     """,
    #     unsafe_allow_html=True)
    # st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)

    
    col_main1, col_main2 = st.columns([1,2.5])
    with col_main1:
        with st.expander("# **About**", expanded=True):
            st.write("""The Pathfinder Assessment Report provides a detailed overview of your performance in the Pathfinder Exam, 
            helping you identify strengths and areas for improvement. By entering your reference number, you can access personalized 
            feedback and tailored suggestions to bridge knowledge gaps and guide your learning journey. The report leverages Eskwelabs' 
            2023 Competencies Framework to offer actionable insights, with an option to save your report for tracking progress over time.""")
            
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
               Enter the reference number to access your Pathfinder Assessment Report.
            
            4. **Review Suggestions for Improvement:**  
               Along with your performance summary, the app will provide tailored suggestions aimed at helping you improve in the areas where you scored lower.  
               Follow these suggestions to enhance your understanding and close any knowledge gaps.
            
            5. **Save Your Report:**  
               If desired, you can save your performance summary and suggestions for future reference. This allows you to track your progress over time and revisit the feedback as needed.
            
            6. **Plan Your Next Steps:**  
               Use the feedback and suggestions to plan your next steps in your learning journey. Focus on the areas identified as needing improvement and take advantage of the resources provided by the app.
            """, unsafe_allow_html=True)

else:
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


