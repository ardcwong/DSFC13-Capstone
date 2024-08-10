import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
import json

########################################################
# API KEYS and CREDENTIALS
########################################################
api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
client = gspread.authorize(creds)


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

        prompt += "\nSummarize the feedback and actionable suggestions into a single paragraph.\nUse this format:\nSummary\nSuggestions(paragraph)"

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
if "reference_number" not in st.session_state:
    st.session_state.reference_number = []
if "feedback_generated" not in st.session_state:
    st.session_state.feedback_generated = []

if st.session_state.generate_pf_fs == False:
    # Input for reference number

    column11, column12, column13 = st.columns([2,6,2])  
    with column12:
        reference_number = st.text_input("Enter your Reference Number:")
        if st.button("My Pathfinder Exam Results Feedback Summary", use_container_width = True, type = "primary"):
            st.session_state.generate_pf_fs = True
            st.session_state.reference_number = reference_number
            st.rerun()
# Streamlit App Title
# st.title("Data Science Preparedness Feedback Generator")

else:
    # # Button to look up scores
# if st.button("Lookup Scores"):
#     if reference_number:
    user_data = scores_dataset[scores_dataset['Reference Number'] == st.session_state.reference_number]
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
            
            column1, column2, column3 = st.columns([1,8,1])        
            with column2:
                # st.write(pd.DataFrame(list(scores.items()), columns=["Category", "Score Category"]))  
                st.header("Feedback Summary")
                for main_category, feedback in zip(category_structure.keys(), st.session_state.feedback_generated):
                    with st.container(border = True):
                        st.markdown(f"""<h5 style='text-align: center;color: #e76f51;font-size: 35px;'><b><i>{main_category}</b></i><i></h5>""", unsafe_allow_html=True)
                        # st.divider()
                        # st.write(f"**{main_category.upper()}**")
                        st.write(feedback)
    else:
        st.error("Reference Number not found.")
# else:
#     st.error("Please enter a Reference Number.")

