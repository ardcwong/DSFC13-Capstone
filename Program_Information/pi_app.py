import streamlit as st
import sqlite3
__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from skllm.config import SKLLMConfig
from skllm.models.gpt.text2text.summarization import GPTSummarizer
# from sentence_transformers import SentenceTransformer, util
import openai
from openai import OpenAI
from wordcloud import WordCloud
import subprocess
import time
import numpy as np
import ast #built in
import chromadb
from chromadb.utils import embedding_functions
from annotated_text import annotated_text
# from langchain.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# if "stop" not in st.session_state:
#     st.session_state.stop = True
#     nltk.download('stopwords')

x = "No"

api_key = st.secrets["api"]['api_key']
openai.api_key = api_key
credentials = st.secrets["gcp_service_account"]
client = OpenAI(api_key=api_key)
# SKLLMConfig.set_openai_key(api_key)

class ChatHistory:
    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []

    def show_history(self):
        for msg in self.history:
            role = msg['role']
            content = msg['content']
            st.write(f"{role.capitalize()}: {content}")

    def show_history_streamlit(self):
        for msg in self.history:
            role = msg['role']
            content = msg['content']
            st.chat_message(role).write(content)
               
    def get_latest_messages(self, count=4):
        return self.history[-count:]



@st.cache_resource
def load_collection():

    CHROMA_DATA_PATH = "persistent_directory_4"
    try:
        vector_store = Chroma(persist_directory=CHROMA_DATA_PATH, embedding_function  = OpenAIEmbeddings(api_key=openai.api_key))
        return vector_store
    except Exception as e:
        st.error(f"Error loading vector store: {e}")
        return None

    

vector_store = load_collection()
# st.write(vector_store)
def retrieve_documents(query, collection):
    # Perform similarity search
    results = collection.similarity_search(query, k=3)
    
    docs = [result.page_content for result in results]
    metadatas = [result.metadata for result in results] 

    return [{'text': doc, 'metadata': meta} for doc, meta in zip(docs, metadatas)]

#####
# add rules when chat memory is blank then dont include it in the prompt
####
def generate_chatbot_response(context, query, metadata, chat_memory):
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_memory])
    metadata_info = "\n".join([f"File: {meta['description']}" for meta in metadata])
    prompt = f"Based on the following conversation history:\n\n{history_text}\n\nAnd the following information:\n\n{context}\n\nAdditional Information:\n{metadata_info}\n\nAnswer the following question:\n{query}"
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that helps students answer questions about Eskwelabs' Data Science Fellowship program."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()
def chatbot_response(user_query, collection, chat_history, chat_memory):
    chat_history.add_message("user", user_query)
    
    retrieved_docs = retrieve_documents(user_query, collection)
    context = ' '.join([doc['text'] for doc in retrieved_docs])
    response = generate_chatbot_response(context, user_query, [doc['metadata'] for doc in retrieved_docs], chat_memory)
    
    chat_history.add_message("assistant", response)
    return response


# Initialize chat history in session state
if 'pi_chat_history' not in st.session_state:
    st.session_state.pi_chat_history = ChatHistory()

# Initialize chat history in session state
if 'pi_chat_memory' not in st.session_state:
    st.session_state.pi_chat_memory = []

def update_chat_memory():
    st.session_state.pi_chat_memory = st.session_state.pi_chat_history.get_latest_messages()

def show_pi_chat_memory():
    for msg in st.session_state.pi_chat_memory:
        role = msg['role']
        content = msg['content']
        st.chat_message(role).write(content)

# Inject CSS to create a fixed container
st.markdown("""
    <style>
    .fixed-container {
        position: fixed;
        top: 0;
        width: 100%;
        background-color: white;
        z-index: 1000;
        padding: 10px;
    }
    </style>
    
    <div class="fixed-container">
        <h1><br>Eskwelabs Data Science Fellowship Information Bot</h1>
    </div>
""", unsafe_allow_html=True)


# st.markdown(f"<h1 style='text-align: center;'>Eskwelabs Data Science Fellowship Information Bot</h1>", unsafe_allow_html=True)
st.divider()
st.markdown("""<h5 style='text-align: center;color: #e76f51;'><b><i>Welcome to the Eskwelabs Data Science Fellowship Information Bot!" </b></i><i>
            <br><br>
            This intelligent bot is designed to help you understand all aspects of the Eskwelabs Data Science Fellowship (DSF) program.
            Whether you're considering applying or just curious about what the program offers, this bot provides detailed information to guide you.</h5>""", unsafe_allow_html=True)
st.divider()                        

user_query = st.chat_input("Ask")
if user_query:
    response = chatbot_response(user_query, vector_store, st.session_state.pi_chat_history, st.session_state.pi_chat_memory)
    update_chat_memory()  # Update chat memory with the latest messages

if st.button("Clear history"):
    st.session_state.pi_chat_history.clear_history()
    st.session_state.pi_chat_memory = []  # Clear chat memory as well
with st.container():
    st.session_state.pi_chat_history.show_history_streamlit()





