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

api_key = st.secrets["api"]['api_key']e
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



collection = load_collection_DSFBAssistant()


# def return_best_eskdata(user_input, collection, n_results=1):
#     query_result = collection.query(query_texts=[user_input], n_results=n_results)
#     if not query_result['ids'] or not query_result['ids'][0]:
#         return None, None
#     top_result_id = query_result['ids'][0][0]
#     top_result_metadata = query_result['metadatas'][0][0]
#     top_result_document = query_result['documents'][0][0]
#     return top_result_metadata.get('eskdata', 'Unknown Data'), top_result_document

# def generate_conversational_response_DSFBAssistant(user_input, collection):
#     relevant_name, relevant_document = return_best_eskdata(user_input, collection)
#     if not relevant_name:
#         return "I couldn't find any relevant articles based on your input."
#     messages = [
#         {"role": "system", "content": "You are a bot that makes recommendations for each Sprint 1 to 4 for the Data Science bootcamp."},
#         {"role": "user", "content": user_input},
#         {"role": "assistant", "content": f"This is the recommended article: {relevant_name}. Here is a brief about the article: {relevant_document}"}
#     ]
#     response = openai.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=messages,
#         max_tokens=500
#     )
#     return response.choices[0].message.content


# Function to find the best matching data in the collection based on user input
def return_best_eskdata(user_input, collection, n_results=3):
    query_result = collection.query(query_texts=[user_input], n_results=n_results)
    if not query_result['ids'] or not query_result['ids'][0]:
        return []
    
    # Collect the top N results
    results = []
    for i in range(n_results):
        if i < len(query_result['ids'][0]):
            top_result_metadata = query_result['metadatas'][0][i]
            top_result_document = query_result['documents'][0][i]
            # Extract the link from the metadata or document
            link = top_result_document.split('Link: ')[1].split('\n')[0] if 'Link: ' in top_result_document else 'No Link Found'
            results.append({
                "title": top_result_metadata.get('eskdata', 'Unknown Data'),
                "document": top_result_document,
                "link": link
            })
    return results

# Function to generate a conversational response using OpenAI API with document-based initial response
def generate_conversational_response(user_input, collection):
    # Step 1: Query for the most relevant document
    related_articles = return_best_eskdata(user_input, collection, n_results=3)
    
    if not related_articles:
        return "I couldn't find any relevant articles based on your input."

    # Use the retrieved document to form the initial response
    primary_article = related_articles[0]  # Use the most relevant article
    document_content = primary_article['document'][:1000]  # Limit the document content to a reasonable length

    # Step 2: Generate a conversational response using the document content
    conversation_prompt = (
        f"Based on the following information, please provide a friendly and conversational explanation:\n\n"
        f"{document_content}\n\n"
        f"Please also recommend the reader to explore more using this link: {primary_article['link']}"
    )

    try:
        conversational_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly assistant who provides clear and engaging explanations."},
                {"role": "user", "content": conversation_prompt}
            ],
            max_tokens=1000,
        )
        final_response_content = conversational_response.choices[0].message.content

        # Step 3: Prepare related articles section
        if len(related_articles) > 1:
            related_content = "Here are some additional related articles you might find useful:\n"
            for article in related_articles[1:]:
                related_content += f"- **{article['title']}**: [Read more]({article['link']})\n"
        else:
            related_content = "No additional related articles were found."

        # Combine the final response with related articles
        final_response = f"{final_response_content}\n\n{related_content}"
        
        return final_response
    
    except Exception as e:
        st.error(f"An error occurred with OpenAI API: {e}")
        return "An error occurred while generating the response."


# Streamlit UI
st.title("Data Science Bootcamp Assistant")
st.write("Ask any question related to the bootcamp, and get recommendations and answers.")
# with st.container():
#   user_input = st.chat_input("Enter your question:")
#   if user_input:
#       response = generate_conversational_response_DSFBAssistant(user_input, collection)
#       st.write(f"You asked: {user_input}")  
#       st.write(response)

# Initialize session state for button clicks
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Function to handle button clicks and generate a response
def handle_button_click(question):
    st.session_state.button_clicked = True
    st.session_state.response = generate_conversational_response(question, collection)

# Add conversation starters if no button has been clicked yet
if not st.session_state.button_clicked:
    st.write("Choose a question to get started:")
    
    if st.button("What is RAG in LLM?"):
      handle_button_click("What is RAG in LLM?")
      
        
    
    if st.button("What is Bag of Words?"):
      handle_button_click("What is Bag of Words?")
        
    
    if st.button("What is Recall in Machine Learning?"):
      handle_button_click("What is Recall in Machine Learning?")
        

# Display the response if a button has been clicked
if st.session_state.button_clicked:
    st.write(st.session_state.response)

# Allow the user to enter their own question after clicking a starter question
user_input = st.text_input("Or enter your question:")
if user_input:
    response = generate_conversational_response(user_input, collection)
    st.write(response)
    feedback = st.text_input("Was this answer helpful? Leave your feedback:")
    if feedback:
        st.write("Thank you for your feedback!")
