import streamlit as st
import openai
from openai import OpenAI
import pandas as pd


# Load CSV file containing the cohort's main topics and subtopics
def load_and_generate_course_outline(filepath):
    df = pd.read_csv(filepath)
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

# Function to retrieve and generates additional information about specific course topics
def generate_additional_content(query, collection):
    retrieved_docs = retrieve_documents(query, collection)
    context = ' '.join([doc['text'] for doc in retrieved_docs])
    
    prompt = f"Based on the following information:\n\n{context}\n\nAnswer the following question:\n{query}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that provides detailed educational content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content.strip()

# Function to enhance course outline 
def enhance_course_outline(course_outline, collection):
    enhanced_outline = {}
    for sprint, topics in course_outline.items():
        enhanced_outline[sprint] = {}
        for main_topic, subtopics in topics.items():
            enhanced_outline[sprint][main_topic] = {}
            for subtopic in subtopics:
                query = f"Provide detailed information and educational content about {subtopic} in the context of {main_topic}."
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant that provides detailed educational content."},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=350
                )
                additional_content = response.choices[0].message.content.strip()
                enhanced_outline[sprint][main_topic][subtopic] = additional_content
    return enhanced_outline


# Define file path to the CSV containing the cohort's curriculum
cohort_outline_filepath = 'data/Data Science Fellowship Cohort 13 Curriculum.csv'

# Load and generate the course outline from the CSV file
course_outline = load_and_generate_course_outline(cohort_outline_filepath)

# # Assuming `collection` is your ChromaDB collection with embeddings already set up
# enhanced_course_outline = enhance_course_outline(course_outline, None)


# st.title("Sprint Navigator")
# st.markdown("""The Sprint Navigator is a meticulously crafted course outline, designed to provide a clear and organized view of the 
# program's main topics and sub-topics, divided into four distinct Sprints. This Navigator acts as both a strategic planning tool and 
# a detailed guide for fellows, helping them steer through their learning journey with confidence. It ensures that all critical areas 
# of the program are covered in a cohesive and logical order, enabling fellows to grasp the curriculum's flow, stay aligned with their 
# learning objectives, and prepare effectively for the challenges ahead.""")
# # Print the enhanced course outline with detailed content
# for sprint, topics in enhanced_course_outline.items():
#     with st.expander(f"{sprint}",expanded=True):
#     # st.write(f"{sprint}:")
#         for main_topic, subtopics in topics.items():
#             st.write(f"  Main Topic: {main_topic}")
#             for subtopic, content in subtopics.items():
#                 st.write(f"    Subtopic: {subtopic}")
#                 st.write(f"      Content:\n{content}\n")


# Streamlit UI
st.title("Sprint Navigator")

st.markdown("""
The Sprint Navigator is a meticulously crafted course outline, designed to provide a clear and organized view of the program's main 
topics and sub-topics, divided into four distinct Sprints. This Navigator acts as both a strategic planning tool and a detailed 
guide for fellows, helping them steer through their learning journey with confidence.
""")


# # Dynamic checkbox generation with session state
# selected_sprints = {}

# for sprint in course_outline.keys():
#     if st.checkbox(sprint, key=f"checkbox_{sprint}"):
#         if f"outline_{sprint}" not in st.session_state:
#             # Enhance only if it hasn't been done before
#             st.session_state[f"outline_{sprint}"] = enhance_course_outline({sprint: course_outline[sprint]}, None)
#         selected_sprints[sprint] = st.session_state[f"outline_{sprint}"]

# # Display the enhanced course outline with detailed content
# if selected_sprints:
#     for sprint, topics in selected_sprints.items():
#         with st.expander(f"{sprint}", expanded=True):
#             for main_topic, subtopics in topics[sprint].items():
#                 st.write(f"Main Topic: {main_topic}")
#                 for subtopic, content in subtopics.items():
#                     st.write(f"  Subtopic: {subtopic}")
#                     st.write(f"    Content:\n{content}\n")

# Dynamic expander generation with session state
for sprint in course_outline.keys():
    expanded = st.expander(f"{sprint}", expanded=False)
    
    # Check if the expander is expanded and if the sprint outline hasn't been enhanced yet
    if expanded and f"outline_{sprint}" not in st.session_state:
        # Enhance the course outline for the sprint and store it in session state
        st.session_state[f"outline_{sprint}"] = enhance_course_outline({sprint: course_outline[sprint]}, None)
    
    # Retrieve and display the enhanced course outline from session state
    if f"outline_{sprint}" in st.session_state:
        enhanced_outline = st.session_state[f"outline_{sprint}"]
        for main_topic, subtopics in enhanced_outline[sprint].items():
            st.write(f"Main Topic: {main_topic}")
            for subtopic, content in subtopics.items():
                st.write(f"  Subtopic: {subtopic}")
                st.write(f"    Content:\n{content}\n")
