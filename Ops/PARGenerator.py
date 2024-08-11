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

# Function to update the HTML_CONTENT and PARGeneratedTag columns in the Google Sheet
def save_html_content_and_update_tag(spreadsheet, reference_number, html_content):
    worksheet = spreadsheet.worksheet("Sheet1")
    cell = worksheet.find(reference_number, in_column=1)  # Assumes "Reference Number" is in the first column
    if cell:
        # worksheet.update_cell(cell.row, worksheet.find("HTML_CONTENT").col, st.session_state.html_content)
        worksheet.update_cell(cell.row, worksheet.find("REPORT_INTRO").col, st.session_state.report_intro)
        worksheet.update_cell(cell.row, worksheet.find("SCORE_CATEGORY_TABLE").col, st.session_state.styled_table_html)
        worksheet.update_cell(cell.row, worksheet.find("FEEDBACK_SECTION").col, st.session_state.feedback_section)
        # Update PARGeneratedTag to "Y"
        worksheet.update_cell(cell.row, worksheet.find("PARGenTag").col, "Y")
        return True
    else:
        return False
        
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


# Custom function to categorize scores
def categorize_score(score):
    if score < 40:
        return "Needs Improvement"
    elif 40 <= score < 60:
        return "Fair"
    elif 60 <= score < 80:
        return "Good"
    else:
        return "Excellent"


# Function to generate a single summarized feedback paragraph using GPT
def generate_summarized_feedback(scores):
    feedback = []

    # Iterate through each main category and generate feedback
    for category, score in scores.items():
        score_category = score
        subcategories = category_structure[category]

        # Constructing the prompt
        prompt = (
            f"Based on the following information, please provide a summarized of feedback and actionable suggestions "
            f"to help me improve in the category '{category}'.\n"
            f"The student's performance in this category is '{score_category}'.\n"
            f"Here are the subcategories and key topics covered in this category:\n\n"
        )

        for subcategory, topics in subcategories.items():
            topic_list = ', '.join(topics)
            prompt += f"- {subcategory}: {topic_list}\n"

        prompt += "\nSummarize the feedback and actionable suggestions into a single paragraph."

        # Get the suggestion from GPT
        suggestion = ask_openai(prompt)
        
        # # Store the feedback in the dictionary
        # feedback[category] = {
        #     "Score Category": score_category,
        #     "Feedback": suggestion
        # }
        # Append the feedback
        feedback.append(f"**{category}** ({score_category}):\n{suggestion}\n")
        
    return feedback 

    # return "\n".join(feedback)
# Function to interact with OpenAI's GPT
def ask_openai(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant who generates feedback for Eskwelabs pathfinder exam results in a generalized and contructive manner."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250
    )
    return response.choices[0].message.content.strip()

if "generate_pf_fs" not in st.session_state:
    st.session_state.generate_pf_fs = False
if "reference_number_ops" not in st.session_state:
    st.session_state.reference_number_ops = []
if "feedback_generated" not in st.session_state:
    st.session_state.feedback_generated = []
if "html_content" not in st.session_state:
    st.session_state.html_content = ""

def score_table_show(scores):
    # Convert the scores dictionary to an HTML table directly
    table_html = f"""
    <table class="styled-table" style="width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; margin-top: 6px; border-radius: 5px; border: 1px solid #21AF8D; overflow: hidden;">
        <tr style="background-color: #28a745;">
            {"".join([f"<th style='padding: 8px; text-align: center; color: white;'>{category}</th>" for category in scores.keys()])}
        </tr>
        <tr>
            {"".join([f"<td style='padding: 8px; text-align: center;'>{performance}</td>" for performance in scores.values()])}
        </tr>
    </table>
    <div style="font-size:16px;">
        <strong><br><br></strong>
    </div>
    """
    
    # Apply CSS styling
    styled_table_html = f"""
    <style>
    .styled-table {{
        border-radius: 5px;  /* Rounded corners for the table */
        overflow: hidden; /* Ensures rounded corners are applied */
        border: 1px solid #21AF8D;  /* Dark green border for the whole table */
    }}
    .styled-table th, .styled-table td {{
        border: 1px solid #21AF8D;  /* Dark green border for cells */
    }}
    .styled-table th {{
        background-color: #21AF8D;  /* Dark green header */
        color: white;  /* White text in header */
    }}
    .styled-table tr:nth-child(even) {{
        background-color: #e9f7ef;  /* Light green for even rows */
    }}
    .styled-table tr:nth-child(odd) {{
        background-color: #f7fcf9;  /* Slightly lighter green for odd rows */
    }}
    </style>
    {table_html}
    """
    
    return styled_table_html
####################################################################
################            MAIN PROGRAM            ################
####################################################################

st.dataframe(scores_dataset)
is_blank = scores_dataset["PARGenTag"] == "N"
pf_rn = scores_dataset["Reference Number"][is_blank].tolist()
reference_number_ops = st.selectbox("Choose a Pathfinder Result Reference Number",pf_rn)

if "report_intro" not in st.session_state:
    st.session_state.report_intro = ""

if "styled_table_html" not in st.session_state:
    st.session_state.styled_table_html = ""

if "feedback_section" not in st.session_state:
    st.session_state.feedback_section = []

COL1, COL2 = st.columns([3,7])
with COL2:
    with st.expander(f"{st.session_state.reference_number_ops} PAR",expanded=True):
        if st.session_state.html_content is not "":
            st.markdown(st.session_state.report_intro, unsafe_allow_html=True)
            st.markdown(st.session_state.styled_table_html, unsafe_allow_html=True)
            for feedback_section in st.session_state.feedback_section:
                st.markdown(feedback_section, unsafe_allow_html=True)
            

with COL1:
    with st.expander("TOOLS", expanded = True):
        if st.button("Generate", use_container_width = True, type = "primary"):
            st.session_state.generate_pf_fs = True
            st.session_state.reference_number_ops = reference_number_ops
            st.session_state.html_content = ""
            st.session_state.report_intro = ""
            st.session_state.styled_table_html = ""
            st.session_state.feedback_section = []
            st.session_state.feedback_generated = []
        if st.session_state.html_content is not "":
            # Add the "Save" button
            if st.button(f"Save Report to Google Sheet (**{st.session_state.reference_number_ops}**)", use_container_width = True):
                saved = save_html_content_and_update_tag(st.session_state.spreadsheet_PathfinderExamResults, st.session_state.reference_number_ops, st.session_state.html_content)
                if saved:
                    st.success("HTML content saved successfully and PARGeneratedTag updated.")
                    st.rerun()
                else:
                    st.error("Failed to save HTML content or update PARGeneratedTag.")
            pdf = convert_html_to_pdf(st.session_state.html_content)
            if pdf:
                st.download_button(label=f"Download PDF (**{st.session_state.reference_number_ops}**)", data=pdf, file_name="PAR.pdf", mime="application/pdf", use_container_width = True)
            else:
                st.error("Failed to convert HTML to PDF.")


        if st.session_state.generate_pf_fs == True:
            user_data = scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number_ops]
            if not user_data.empty:
                scores = {}
                for main_category in category_structure.keys():
                    score_str = user_data[main_category].values[0]
                    
                    # Remove the '%' sign and convert to float
                    if isinstance(score_str, str) and '%' in score_str:
                        score = float(score_str.replace('%', '').strip())
                    else:
                        score = float(score_str)
                        
                    scores[main_category] = score
                    score_category = categorize_score(score)
                    
                    scores[main_category] = score_category
                    
                with st.spinner("Generating feedback..."):
                    if st.session_state.feedback_generated == []:
                        st.session_state.feedback_generated = generate_summarized_feedback(scores)
        
        
                            
                    
                    # html_content = ""
                    
                    with st.container(border=True):
                        column1, column2, column3 = st.columns([1,8,1])        
                        with column2:
                            report_intro = f"""<h1 style='text-align: center;font-size: 40px; font-weight: bold;'><br>Your Pathfinder Assessment Report</h1>
                            <hr style="border:2px solid #ccc;" />
                            <h5 style='text-align: left;color: #e76f51;font-size: 35px;'><strong><b>Introduction</b></strong></h5>
                            <div style="font-size:16px;">
                                <strong>Thank you for completing the Pathfinder Assessment Exam.<br></strong>
                            </div>
                            <div style="font-size:14px;">
                                <br>The results of your assessment have been analyzed, and a summary of your performance is provided below. The content of this report is confidential and intended solely for you.<br>
                            </div>
                            <div style="font-size:16px;">
                                <strong><br>We strongly believe in the value of feedback, and this report is based on your responses to the Pathfinder Assessment Exam.<br></strong>
                            </div>
                            <div style="font-size:14px;">
                                <strong><br>Performance Summary:</strong>
                                <ul>
                                    <li><strong>Needs Improvement:</strong> Areas where further development is recommended.</li>
                                    <li><strong>Fair:</strong> Areas where your performance meets basic expectations.</li>
                                    <li><strong>Good:</strong> Areas where you have demonstrated a solid understanding and capability.</li>
                                    <li><strong>Excellent:</strong> Areas where you have excelled and shown strong proficiency.</li>
                                </ul>
                            </div>
                            <div style="font-size:14px;">
                                <strong>Actionable Suggestions:</strong><br>
                                Along with your performance summary, we have included actionable suggestions to help you improve where needed, build on your strengths, and continue your journey toward mastering key skills.
                            </div>
                            <div style="font-size:14px;">
                                <br>We hope you find this information helpful.
                            </div>
                            <hr style="border:2px solid #ccc;" />
                            <h5 style='text-align: left;color: #e76f51;font-size: 35px;'><strong><b>Feedback Summary</b></strong></h5>
                            """
                            # st.markdown(report_intro, unsafe_allow_html=True)
                            st.session_state.report_intro = report_intro
                            st.session_state.html_content += report_intro
        
                            
                            with st.container(border=False):
                                styled_table_html = score_table_show(scores)
                                # Display the HTML table in Streamlit
                                st.session_state.styled_table_html = styled_table_html
                                # st.markdown(styled_table_html, unsafe_allow_html=True)
                                st.session_state.html_content += styled_table_html
        
        
                            for main_category, feedback in zip(category_structure.keys(), st.session_state.feedback_generated):
                                with st.container(border=False):
        
                                    
                                    feedback_section = f"""
                                    <div style="border: 2px solid #1f77b4; border-radius: 5px; background-color: #1f77b4; color: white; padding: 10px; font-size: 18px;">
                                        <strong>{main_category}</strong>
                                    </div>
                                    <div style="border: 2px solid #1f77b4; border-radius: 5px; background-color: #f0f0f0; padding: 15px; font-size: 14px; color: black;">
                                        <p>{feedback}</p>
                                    </div>
                                    <div style="font-size:18px;">
                                    <strong><br></strong>
                                    </div>
                                    """
                                    st.session_state.feedback_section.append(feedback_section)
                                    # st.markdown(feedback_section, unsafe_allow_html=True)
                                    st.session_state.html_content += feedback_section
                    
        
        
                            st.session_state.generate_pf_fs = False
                            st.rerun()
                        
                    

    # else:
    #     st.error("Reference Number not found.")
    #     st.session_state.generate_pf_fs = False
    #     st.session_state.reference_number = []

# else:
#     st.error("Please enter a Reference Number.")

