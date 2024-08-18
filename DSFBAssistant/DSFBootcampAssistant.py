import streamlit as st
import sqlite3
__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import openai
import streamlit as st
# import os
from openai import OpenAI
# from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import base64
api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]
client = OpenAI(api_key=api_key)

# Load environment variables from .env file
# load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=api_key)

@st.cache_resource
def load_collection_DSFBAssistant():
    CHROMA_DATA_PATH_2 = "eskwe"
    COLLECTION_NAME_2 = "eskwe_embeddings"
    client_chromadb_2 = chromadb.PersistentClient(path=CHROMA_DATA_PATH_2)
    openai_ef_2 = embedding_functions.OpenAIEmbeddingFunction(api_key=openai.api_key, model_name="text-embedding-ada-002")
    collection = client_chromadb_2.get_or_create_collection(
        name=COLLECTION_NAME_2,
        embedding_function=openai_ef_2,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

if 'collection' not in st.session_state:
    st.session_state.collection = load_collection_DSFBAssistant()

######################################

#### USER AVATAR AND RESPONSE
@st.cache_data
def user_avatar():
    # Load the image and convert it to base64
    with open('data/avatar_user.png', 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    # Base64 encoded image string from the previous step
    avatar_base64 = encoded_string
    
    # Construct the base64 image string for use in HTML
    avatar_url = f'data:image/png;base64,{avatar_base64}'
    return avatar_url

avatar_user = user_avatar()

def show_user_question(message_text, avatar_url):
    st.markdown(f"""
    <div style='display: flex; align-items: flex-start; padding: 10px; justify-content: flex-end;'>
        <div style='background-color: #F7F9FA; padding: 10px 15px; border-radius: 10px; margin-right: 10px; display: inline-block; text-align: right; max-width: 60%;box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
            <span style='font-size: 16px;'>{message_text}</span>
        </div>
        <div style='flex-shrink: 0;'>
            <img src='{avatar_url}' alt='avatar' style='width: 40px; height: 40px; border-radius: 50%; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
        </div>
    </div>
    """, unsafe_allow_html=True)

#### AI AVATAR AND RESPONSE WITH FEEDBACK
@st.cache_data
def ai_avatar():
    # Load the image and convert it to base64
    with open('data/avatar_ai.png', 'rb') as image_file_ai:
        encoded_string_ai = base64.b64encode(image_file_ai.read()).decode()
    
    avatar_ai = f'data:image/png;base64,{encoded_string_ai}'
    return avatar_ai

avatar_ai = ai_avatar()

# Initialize session state for storing feedback and ratings
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}

if 'thumbs_up' not in st.session_state:
    st.session_state.thumbs_up = {}

if 'thumbs_down' not in st.session_state:
    st.session_state.thumbs_down = {}

import time

def show_ai_response(message_text, avatar_ai, response_id):
    st.markdown(f"""
    <div style='display: flex; align-items: flex-start; padding: 10px; justify-content: flex;'>
        <div style='flex-shrink: 0;'>
            <img src='{avatar_ai}' alt='avatar' style='width: 40px; height: 40px; border-radius: 50%; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
        </div>
        <div style='background-color: #FCFCFC; padding: 10px 15px; border-radius: 10px; margin-left: 10px; display: inline-block; text-align: left; max-width: 85%; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
            <span style='font-size: 16px;'>{message_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feedback link and thumbs up/thumbs down in the same row
    col1, col2, col3 = st.columns([1.5, 2, 2])
    with col2:
        if st.button("👍", key=f"thumbs_up_{response_id}"):
            st.session_state.thumbs_up[response_id] = st.session_state.thumbs_up.get(response_id, 0) + 1
            st.session_state.feedback_mode = f"feedback_up_{response_id}"

    with col3:
        if st.button("👎", key=f"thumbs_down_{response_id}"):
            st.session_state.thumbs_down[response_id] = st.session_state.thumbs_down.get(response_id, 0) + 1
            st.session_state.feedback_mode = f"feedback_down_{response_id}"

    # Only show feedback area if a thumbs button was clicked
    if st.session_state.get('feedback_mode') == f"feedback_up_{response_id}" or st.session_state.get('feedback_mode') == f"feedback_down_{response_id}":
        feedback = st.text_area("Tell us more about your experience:", key=f"feedback_{response_id}")
        if st.button("Submit Feedback", key=f"submit_feedback_{response_id}"):
            st.session_state.feedback[response_id] = feedback
            st.session_state.feedback_mode = None  # Reset feedback mode after submission
            
            # Display the thank you message temporarily
            thanks_placeholder = st.empty()
            thanks_placeholder.success("Thank you for your feedback!")
            
            # Wait for 1 seconds
            time.sleep(1)
            
            # Clear the thank you message
            thanks_placeholder.empty()
            
            # Optionally, rerun the page to return to the user response view
            st.rerun()
##########################

def return_best_eskdata(user_input, collection, n_results=3):
    query_result = collection.query(query_texts=[user_input], n_results=n_results)
    if not query_result['ids'] or not query_result['ids'][0]:
        return []
    
    results = []
    for i in range(n_results):
        if i < len(query_result['ids'][0]):
            distance = query_result['distances'][0][i]
            if distance >= 0.25:
                continue  # Skip results with distance >= 0.25
            
            top_result_metadata = query_result['metadatas'][0][i]
            top_result_document = query_result['documents'][0][i]
            link = top_result_document.split('Link: ')[1].split('\n')[0] if 'Link: ' in top_result_document else 'No Link Found'
            results.append({
                "title": top_result_metadata.get('eskdata', 'Unknown Data'),
                "document": top_result_document,
                "link": link
            })

    return results

def generate_conversational_response(user_input, collection):
    related_articles = return_best_eskdata(user_input, collection, n_results=3)
    
    if not related_articles:
        return "I couldn't find any relevant articles based on your input."

    primary_article = related_articles[0]
    document_content = primary_article['document'][:2000]

    conversation_prompt = (
        f"You are an expert in Data Science. Based on the following information, please provide a friendly and conversational explanation. No need to mention the article. Provide code as much as possible.:\n\n"
        f"{document_content}\n\n"
        f"Please also recommend the reader to explore more using this link: {primary_article['link']}"
    )

    try:
        conversational_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in Data Science and a friendly assistant who provides clear and engaging explanations. No need to mention the article. Provide code as much as possible."},
                {"role": "user", "content": conversation_prompt}
            ],
            max_tokens=1000,
        )
        final_response_content = conversational_response.choices[0].message.content

        if len(related_articles) > 1:
            related_content = "Here are some additional related articles you might find useful:\n"
            for article in related_articles[1:]:
                related_content += f"- **{article['title']}**: [Read more]({article['link']})\n"
        else:
            related_content = "No additional related articles were found."

        final_response = f"{final_response_content}\n\n{related_content}"
        
        return final_response
    
    except Exception as e:
        st.error(f"An error occurred with OpenAI API: {e}")
        return "An error occurred while generating the response."

###### Streamlit UI ###########
# Initialize session state for conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Initialize session state for button clicks
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Initialize session state for question
if 'question' not in st.session_state:
    st.session_state.question = ""

# Streamlit UI
########################################## MAIN PROGRAM ##########################################
# Allow the user to enter their own question
user_input = st.chat_input("Enter your question:")
if user_input:
    st.session_state.button_clicked = True
    st.session_state.question = user_input
    st.rerun()
    
with st.sidebar:
    if st.button("Start Over", type = "primary", use_container_width = True, help = "Restart Chat Session"):
        st.session_state.button_clicked = False
        st.session_state.question = "" 
        st.session_state.conversation = []
        st.session_state.feedback = {}
        st.session_state.thumbs_up = {}
        st.session_state.thumbs_down = {}
        st.rerun()
#################################################################################################

ba1, ba2, ba3 = st.columns([1, 4, 1])

with ba2:
    st.markdown(f"<h1 style='text-align: center;'>Data Science Bootcamp Assistant</h1>", unsafe_allow_html=True)
    st.markdown(f"<h6 style='text-align: center;'><i>Ask any question related to the bootcamp, and get recommendations and answers.</i></h6>", unsafe_allow_html=True)

    # Display the conversation history
    for idx, message in enumerate(st.session_state.conversation):
        show_user_question(message['user'], avatar_user)
        show_ai_response(message['response'], avatar_ai, idx)

    # If no button has been clicked yet, show the conversation starter buttons
    if not st.session_state.button_clicked:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        
        assistant_stats = "Arden. Line 252.<br>Sample: I consistently provide reliable recommendations, with a 93% consistency rate in my suitability classifications."
        b00, b01, b02, b03, b04 = st.columns([1, 1, 1, 1, 1])
        with b02:
            st.image('data/avatar_ai.png', use_column_width=True)
            # st.markdown(
            # f"""
            # <style>
            # .tooltip {{
            #   position: relative;
            #   display: inline-block;
            #   cursor: pointer;
            # }}
        
            # .tooltip .tooltiptext {{
            #   visibility: hidden;
            #   width: 250px;
            #   background-color: #fff;
            #   color: #333;
            #   text-align: left; /* Align text to the left */
            #   border-radius: 5px;
            #   padding: 10px;
            #   position: absolute;
            #   z-index: 1;
            #   left: 100%; /* Position next to the image */
            #   top: 50%;
            #   transform: translateX(20%) translateY(-50%); /* Center tooltip box */
            #   opacity: 0;
            #   transition: opacity 0.3s;
            #   white-space: normal; /* Allow text to wrap */
            #   display: flex;
            #   align-items: flex-end; /* Align content to the bottom */
            #   justify-content: flex-start; /* Align content to the left */
            #   box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.1);
            #   font-size: 12px;
            # }}
        
            # .tooltip:hover .tooltiptext {{
            #   visibility: visible;
            #   opacity: 1;
            # }}
            # </style>
            # <div style='display: flex; align-items: center; justify-content: center; width: 100%;'>
            #     <div class='tooltip' style='flex-shrink: 0; width: 100%;'>
            #         <img src='{avatar_ai}' style='width: 100%; height: auto; object-fit: contain;'>
            #         <span class="tooltiptext">{assistant_stats}</span>
            #     </div>
            # </div>
            # """,
            # unsafe_allow_html=True
            # )           
        
        st.markdown(f"<h6 style='text-align: center;'><br><br><br>Choose a question to get started:</h6>", unsafe_allow_html=True)
        b0, b1, b2, b3, b4 = st.columns([1, 1, 1, 1, 1])
        with b1:
            if st.button("What is RAG in LLM?", use_container_width=True):
                st.session_state.question = "What is RAG in LLM?"
                st.session_state.button_clicked = True
                st.rerun()

        with b3:
            if st.button("What is Bag of Words?", use_container_width=True):
                st.session_state.question = "What is Bag of Words?"
                st.session_state.button_clicked = True
                st.rerun()

        with b2:
            if st.button("What is Recall in Machine Learning?", use_container_width=True):
                st.session_state.question = "What is Recall in Machine Learning?"
                st.session_state.button_clicked = True
                st.rerun()
    
    # After a question is asked, append it to the conversation history and display the response
    if st.session_state.question:
        response = generate_conversational_response(st.session_state.question, st.session_state.collection)
        st.session_state.conversation.append({'user': st.session_state.question, 'response': response})
        st.session_state.question = ""  # Clear the question after it's processed
        st.rerun()

