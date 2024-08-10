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
client1 = gspread.authorize(creds)
client2 = gspread.authorize(creds)

# Google Sheets connection function
def google_connection_gsheet_DerivedCompetencyFramework(client):
    # Open the Google Sheet
    spreadsheet1 = client.open("Derived Competency Framework")
    return spreadsheet1

def google_connection_gsheet_PathfinderExamResults(client):
    # Open the Google Sheet
    spreadsheet2 = client.open("Pathfinder Exam Results")
    return spreadsheet2

########################################################
# ACCESS DERIVED COMPETENCY FRAMEWORK GSHEET
########################################################
if "spreadsheet_DerivedCompetencyFramework" not in st.session_state:
    st.session_state.spreadsheet_DerivedCompetencyFramework = google_connection_gsheet_DerivedCompetencyFramework(client1)
########################################################
# ACCESS PATHFINDER EXAM RESULTS GSHEET
########################################################
if "spreadsheet_PathfinderExamResults" not in st.session_state:
    st.session_state.spreadsheet_PathfinderExamResults = google_connection_gsheet_PathfinderExamResults(client2)

st.write(st.session_state.spreadsheet_DerivedCompetencyFramework)
st.write(st.session_state.spreadsheet_PathfinderExamResults)
# Function to load category structure data from Google Sheet
@st.cache_data
def load_category_structure(_spreadsheet):
    worksheet = _spreadsheet.worksheet("Sheet1")
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
@st.cache_data
def load_scores_dataset(_spreadsheet2):
    worksheet2 = _spreadsheet2.worksheet("Sheet1")
    data_score = worksheet2.get_all_values()
    df_score = pd.DataFrame(data_score[1:], columns=data_score[0])
    st.write(df_score)
    return df_score

# Load the data
category_structure = load_category_structure(st.session_state.spreadsheet_DerivedCompetencyFramework)
scores_dataset = load_scores_dataset(st.session_state.spreadsheet_DerivedCompetencyFramework)
st.write(category_structure)
st.write(scores_dataset.head())
# Streamlit App Title
st.title("Data Science Preparedness Feedback Generator")

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

# Function to generate feedback using GPT based on categorized scores
def generate_feedback_with_subcategories_via_gpt(scores):
    feedback = []
    for category, score in scores.items():
        feedback.append(f"Your performance in {category} is categorized as {score}. Here are some suggestions:")
        
        # Custom feedback messages based on the score category
        if score == "Needs Improvement":
            feedback.append(f"Consider revisiting the basics in {category}. Focus on understanding the fundamentals.")
        elif score == "Fair":
            feedback.append(f"You're on the right track in {category}, but there's room for improvement. Keep practicing.")
        elif score == "Good":
            feedback.append(f"You're doing well in {category}. Keep honing your skills and move to advanced topics.")
        else:  # Excellent
            feedback.append(f"Great job in {category}! Consider taking on more challenging tasks to further excel.")
        
        for subcat, topics in category_structure.get(category, {}).items():
            topic_list = ', '.join(topics)
            prompt = (f"Based on a performance categorized as '{score}' in {category}, provide specific, actionable suggestions "
                      f"for improving in the subcategory '{subcat}', considering the key topics: {topic_list}.")
            suggestion = ask_openai(prompt)
            feedback.append(f"- {subcat}: {suggestion}")
    return feedback

# Function to interact with OpenAI's GPT
def ask_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant who provides specific and actionable feedback."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Input for reference number
reference_number = st.text_input("Enter your Reference Number:")

# Button to look up scores
if st.button("Lookup Scores"):
    if reference_number:
        user_data = scores_dataset[scores_dataset['Reference Number'] == reference_number]
        if not user_data.empty:
            scores = {}
            for main_category in category_structure.keys():
                score = float(user_data[main_category].values[0])
                score_category = categorize_score(score)
                scores[main_category] = score_category
            with st.spinner("Generating feedback..."):
                feedback_list = generate_feedback_with_subcategories_via_gpt(scores)
                feedback_output = "\n".join(feedback_list)
                st.header("Feedback Summary")
                st.text(feedback_output)
        else:
            st.error("Reference Number not found.")
    else:
        st.error("Please enter a Reference Number.")

# Optional: Display raw data for transparency
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.write(scores_dataset)
