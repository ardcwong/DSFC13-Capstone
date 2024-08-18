import streamlit as st
import openai
from openai import OpenAI
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from xhtml2pdf import pisa
from io import BytesIO

def convert_html_to_pdf_weasy(html_content):
    pdf = HTML(string=html_content).write_pdf()
    return pdf
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

########################################################
# ACCESS Data Science Fellowship Curriculum GSHEET
########################################################
if "spreadsheet_courseoutline_ops" not in st.session_state:
    st.session_state.spreadsheet_courseoutline_ops = google_connection_gsheet_courseoutline_ops(client)


# Load CSV file containing the cohort's main topics and subtopics
def load_and_generate_course_outline(spreadsheet):
    worksheet = spreadsheet.worksheet("Data Science Fellowship Cohort")
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
  
  # df = pd.read_csv(filepath)
    course_outline = {}
    
    for _, row in df.iterrows():
        sprint = row['Sprint Number']
        main_topic = row['Main Topic']
        subtopic = row['Sub-Topics']
        
        if sprint not in course_outline:
            course_outline[sprint] = {}
        if main_topic not in course_outline[sprint]:
            course_outline[sprint][main_topic] = []
        course_outline[sprint][main_topic].append(subtopic)
    
    return course_outline

# Function to recommend five datasets for a specific sprint
def recommend_datasets(subtopic):
    query = f"""Recommend 5 datasets with links that are relevant for the subtopic '{subtopic}' for building a concrete deliverable. Provide dataset names, descriptions, use cases, and URLs.
    Ensure recommendations are presented using this format:
    
    Here are the datasets you could explore!
    
    **Dataset Name**
        - **Description:** [Brief description of the dataset]
        - **Use Case:** [Relevant use cases for the dataset]
        - **URL:** [Dataset URL]
        
    """
    system_message = """You are a dataset recommendation assistant. """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ],
        max_tokens=700
    )
    datasets = response.choices[0].message.content.strip()
    return datasets

    # Start with These objectives will guide your learning and help you build valuable skills. Embrace each step and enjoy the process of growth and discovery!
    # 1. Learning Objectives 1 \n 
    # 2. Learning Objectives 2 \n 
    # 3. Learning Objectives 3 \n 
    # ...
    # \n N. Learning Objective N

    # Continue numbering the learning objectives until all relevant objectives have been listed.
# Function to generate learning objectives for a specific sprint
def generate_learning_objectives(sprint, topics):
    query = f"""Generate a | separated list of learning objectives for {sprint} based on the following topics: {topics}.
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a learning objectives assistant."},
            {"role": "user", "content": query}
        ],
        max_tokens=300
    )
    objectives = response.choices[0].message.content.strip()
    return objectives

# Function to save the markdowns to the Google Sheet
def save_markdowns_to_gsheet(spreadsheet, sprint_markdowns, full_html_content):
    worksheet = spreadsheet.worksheet("Data Science Fellowship Cohort")
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # Ensure that there is an "Enhanced Course Outline" column
    if "Enhanced Course Outline" not in df.columns:
        worksheet.update_cell(1, len(df.columns) + 1, "Enhanced Course Outline")
        df["Enhanced Course Outline"] = ""
    
    # Update the "Enhanced Course Outline" column for each sprint
    for sprint, markdown in sprint_markdowns.items():
        # Find the rows corresponding to the sprint
        rows = df[df['Sprint Number'] == sprint].index.tolist()
        for row in rows:
            worksheet.update_cell(row + 2, df.columns.get_loc("Enhanced Course Outline") + 1, markdown)

    cell = worksheet.find("Sprint 1", in_column=1)  # Assumes "Reference Number" is in the first column
    if cell:
        worksheet.update_cell(cell.row, worksheet.find("Full HTML_CONTENT").col, full_html_content)

    return True


if 'enhanced_course_outline' not in st.session_state:
    st.session_state.enhanced_course_outline = []
# Streamlit UI
st.title("Sprint Navigator")

st.markdown("""
The Sprint Navigator provides a clear and organized view of the program's main 
topics, sub-topics, and learning objectives, divided into four distinct Sprints. It also offers tailored dataset recommendations for 
practical, hands-on learning. This Navigator acts as both a strategic planning tool and a detailed guide for fellows, ensuring they have 
all the resources they need to help them confidently steer through their learning journey.
""")
#

t1, t2 = st.columns([1,1])
if 'html_content_co' not in st.session_state:
    st.session_state.html_content_co = ""
if 'learning_objectives' not in st.session_state:
    st.session_state.learning_objectives = []

# st.write(type(st.session_state.learning_objectives))
# st.write(st.session_state.enhanced_course_outline.items())
# st.write("\n".join(
#     [f"{i+1}. {obj}" for i, obj in enumerate(st.session_state.learning_objectives["learning_objectives"])]
# ))


def generate_subtopics_html(main_topic, subtopics, sprint):
    # Collect all HTML parts related to subtopics and learning objectives
    subtopic_html_parts = []
    learning_objectives = generate_learning_objectives(sprint, list(subtopics))

    subtopic_html_parts.append(f"<h4>{main_topic}</h4>")
    subtopic_html_parts.append(f"<p><strong>Subtopics:</strong> {', '.join(subtopics)}</p>")
    subtopic_html_parts.append(f"<p><strong>Learning Objectives:</strong></p>")
    # subtopic_html_parts.append(f"<p>{learning_objectives}</p>")
    # Split the string into a list of objectives
    objectives_list = learning_objectives.split('\n')
    
    # Convert each objective to an HTML list item
    list_items = ''.join(f"{objective}<br>" for objective in objectives_list)
    
    # Wrap the list items in an ordered list
    ordered_list = f"<ol>{list_items}</ol>"
    
    # Append the ordered list to subtopic_html_parts
    subtopic_html_parts.append(f"<p>{ordered_list}</p>")

    # # Ensure the learning objectives are displayed as a list
    # subtopic_html_parts.append(f"<pre><ol>{learning_objectives}</ol></pre>")
    
    # Add spacing or a clear block before the Recommended Datasets section
    subtopic_html_parts.append('<br><p><strong>Recommended Datasets:</strong></p>')
    
    for subtopic in subtopics:
        recommended_datasets = recommend_datasets(subtopic)
        subtopic_html_parts.append(f"<p>{recommended_datasets}</p>")

    return "".join(subtopic_html_parts)

def generate_sprint_markdown(sprint, topics):
    # Collect all HTML parts related to the entire sprint
    sprint_html_parts = [
        '<div style="',
        'background-color: #FFFFFF;',
        'padding: 6px;',
        'border-radius: 10px;',
        'font-family: Arial, sans-serif;',
        'box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.2);',
        'margin-bottom: 10px;',
        'word-wrap: break-word;',  # Ensures long words wrap to the next line
        'word-break: break-word;',  # Breaks long words if necessary
        'overflow-wrap: break-word;',  # Handles long words or URLs
        '">',
        f'<h3 style="color: #54afa7; font-weight: bold;">{sprint}</h3>'
    ]

    for main_topic, subtopics in sorted(topics.items()):
        sprint_html_parts.append(generate_subtopics_html(main_topic, subtopics, sprint))

    sprint_html_parts.append("</div>")
    return "".join(sprint_html_parts)


with t2:
    with st.expander("Generate New Course Outline", expanded=True):
        # Initialize session state if it doesn't exist
        if 'markdowns' not in st.session_state:
            st.session_state['markdowns'] = {}
        if 'title' not in st.session_state:
            st.session_state.title = False
        AA, BB, CC = st.columns([2,1,1])
        with AA:
            if st.button("Generate New Course Outline", use_container_width = True):
                # Load and generate the course outline from the CSV file
                st.session_state.enhanced_course_outline = load_and_generate_course_outline(st.session_state.spreadsheet_courseoutline_ops)
                # st.session_state.enhanced_course_outline = enhance_course_outline(course_outline, None) #### TO UPDATE
                
            # Generate markdown for each sprint and save it in st.session_state
                for sprint, topics in st.session_state.enhanced_course_outline.items():
                    sprint_markdown = generate_sprint_markdown(sprint, topics)

                    
                    # # if sprint == 'Sprint 1': 
                    # sprint_markdown = (
                    #     f"""
                    #     <div style="
                    #         background-color: #FFFFFF;
                    #         padding: 6px;
                    #         border-radius: 10px;
                    #         font-family: Arial, sans-serif;
                    #         box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.2);
                    #         margin-bottom: 10px;
                    #         word-wrap: break-word; /* Ensures long words wrap to the next line */
                    #         word-break: break-word; /* Breaks long words if necessary */
                    #         overflow-wrap: break-word; /* Handles long words or URLs */
                    #     ">
                    #         <h3 style="color: #54afa7; font-weight: bold;">{sprint}</h3>
                    #         {"".join([
                    #             f"<h4>{main_topic}</h4>"
                    #             f"<p><strong>Subtopics:</strong> {', '.join(subtopics)}</p>"
                    #             f"<p><strong>Learning Objectives:</strong></p>"
                    #             f"<p>{generate_learning_objectives(sprint, list(topics.keys()))}<p>"
                    #             + "<br>".join([
                    #                 f"<p><strong>Recommended Datasets:</strong></p>"
                    #                 f"<p>{recommend_datasets(subtopic)}</p>"
                    #                 for subtopic in subtopics
                    #             ])
                    #             for main_topic, subtopics in sorted(topics.items())
                    #         ])}
                    #     </div>
                    #     """
                    # )        
                    st.session_state['markdowns'][sprint] = sprint_markdown
                st.session_state.title = True
                st.rerun()
                    

                # Loop through the sprints and topics to generate styled HTML markdown
        if st.session_state.title == True:
            st.markdown("""<h4 style='text-align: left;color: #e76f51;'><b>Course Outline</b></h4>""", unsafe_allow_html=True) 
        # # Example: Display the markdown for a specific sprint (Sprint 1)
        st.markdown(st.session_state['markdowns'].get('Sprint 1', ''), unsafe_allow_html=True)
        st.markdown(st.session_state['markdowns'].get('Sprint 2', ''), unsafe_allow_html=True)
        st.markdown(st.session_state['markdowns'].get('Sprint 3', ''), unsafe_allow_html=True)
        st.markdown(st.session_state['markdowns'].get('Sprint 4', ''), unsafe_allow_html=True)
        # st.write(st.session_state['markdowns'].get('Sprint 1', ''))
        # Collect all markdowns into a single HTML content block
        st.session_state.html_content_co = collect_all_markdowns(st.session_state['markdowns'])
        with BB:
            # Save markdowns to Google Sheet
            if st.session_state.html_content_co is not "":
                if st.button("Update", use_container_width = True):
                    saved_ = save_markdowns_to_gsheet(st.session_state.spreadsheet_courseoutline_ops, st.session_state['markdowns'],st.session_state.html_content_co)
                    if saved_:
                        st.success("HTML content saved successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to save HTML content.")
        

        
        with CC:
            if st.session_state.html_content_co is not "":
                pdf = convert_html_to_pdf(st.session_state.html_content_co)
                if pdf:
                    st.download_button(label=f"Download PDF", data=pdf, file_name="Course_Outline.pdf", mime="application/pdf", use_container_width = True)
                else:
                    st.error("Failed to convert HTML to PDF.")

with t1:
    if 'get_current_markdown_co' not in st.session_state:
        st.session_state.get_current_markdown_co = ""
    
    def load_course_outline_dataset(spreadsheet):
        worksheet = spreadsheet.worksheet("Data Science Fellowship Cohort")
        data_score = worksheet.get_all_values()
        df_co = pd.DataFrame(data_score[1:], columns=data_score[0])
        return df_co

    df_co = load_course_outline_dataset(st.session_state.spreadsheet_courseoutline_ops)
    get_current_markdown = ""
    with st.expander("Current Course Outline", expanded=True):
        
        for i in range(4):
            get_current_markdown +=  df_co[df_co['Sprint Number'] == f"Sprint {i+1}"]['Enhanced Course Outline'].values[0]
            # st.session_state.get_current_markdown += get_current_markdown
        st.session_state.get_current_markdown_co = df_co[df_co['Sprint Number'] == f"Sprint 1"]['Full HTML_CONTENT'].values[0]    
            
        # st.markdown(st.session_state.get_current_markdown, unsafe_allow_html=True)     
        pdf_current = convert_html_to_pdf(st.session_state.get_current_markdown_co)
        if pdf_current:
            st.download_button(label=f"Download PDF (Current CO)", data=pdf_current, file_name="Course_Outline.pdf", mime="application/pdf", use_container_width = True)
        else:
            st.error("Failed to convert HTML to PDF.")

        st.markdown("""<h4 style='text-align: left;color: #e76f51;'><b>Course Outline</b></h4>""", unsafe_allow_html=True) 
        
        for i in range(4):
            st.markdown(df_co[df_co['Sprint Number'] == f"Sprint {i+1}"]['Enhanced Course Outline'].values[0], unsafe_allow_html=True)




            # if st.button("Generate New Course Outline", use_container_width = True):
            #     # Load and generate the course outline from the CSV file
            #     st.session_state.enhanced_course_outline = load_and_generate_course_outline(st.session_state.spreadsheet_courseoutline_ops)
            #     # st.session_state.enhanced_course_outline = enhance_course_outline(course_outline, None) #### TO UPDATE
            #     # datasets = recommend_datasets(subtopic)
            #     # learning_objectives = generate_learning_objectives(sprint, topics.keys())
            # # Generate markdown for each sprint and save it in st.session_state
            #     for sprint, topics in st.session_state.enhanced_course_outline.items():
            #         sprint_markdown = ""
            #         for main_topic, subtopics in sorted(topics.items()):
            #             # Add sprint and main topic to styled HTML markdown
            #             sprint_markdown = f"""
            #             <div style="border: 1px solid #1E73BE; border-radius: 5px; overflow: hidden; margin-bottom: 20px;">
            #                 <div style="background-color: #1E73BE; padding: 10px;">
            #                     <h4 style="color: white; margin: 0;">{sprint}: {main_topic}</h4>
            #                 </div>
            #                 <div style="background-color: #F8F9FA; padding: 15px;">
            #             """
                        
            #             # Add subtopics to the styled HTML markdown
            #             subtopics_list = ', '.join(subtopics)
            #             sprint_markdown += f"<p style='color: #333333;'><strong>Subtopics:</strong> {subtopics_list}<br></p>"
                
            #             # Generate learning objectives and add to markdown
            #             learning_objectives = generate_learning_objectives(sprint, list(topics.keys()))
            #             st.session_state.learning_objectives = learning_objectives
            #             if learning_objectives:
            #                 if isinstance(learning_objectives, str):
            #                     learning_objectives = json.loads(learning_objectives)
            #                 if learning_objectives:
            #                     numbered_list_learning_objectives = "<br>".join(
            #                         [f"{i+1}. {obj}" for i, obj in enumerate(learning_objectives["learning_objectives"])]
            #                     )
    
                            
            #                     sprint_markdown += f"<p style='color: #333333;'><strong>Learning Objectives:</strong><br>{numbered_list_learning_objectives}<br></p>"
            #             # st.markdown(learning_objectives)
            #             # Add recommended datasets for each subtopic to the styled HTML markdown
            #             for subtopic in subtopics:
            #                 datasets = recommend_datasets(subtopic)
            #                 sprint_markdown += f"<p style='color: #333333;'><strong>Recommended Datasets:</strong> {datasets}<br></p>"
                
            #             # Close the outer div
            #             sprint_markdown += """
            #                 </div>
            #             </div>
            #             """
            #         # Save the generated markdown in st.session_state
            #         st.session_state['markdowns'][sprint] = sprint_markdown
            #     st.session_state.title = True
            #     st.rerun()
            
            
