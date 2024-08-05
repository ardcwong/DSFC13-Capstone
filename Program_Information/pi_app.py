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
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

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



@st.cache_resource
def load_collection():
    # CHROMA_DATA_PATH = 'FDA/fda_drugs_v6'
    # COLLECTION_NAME = "fda_drugs_embeddings_v6"
    # client_chromadb = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    # openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=openai.api_key, model_name="text-embedding-ada-002")
    # collection = client_chromadb.get_or_create_collection(
    # name=COLLECTION_NAME,
    # embedding_function=openai_ef,
    # metadata={"hnsw:space": "cosine"}
    # )
    CHROMA_DATA_PATH = "persistent_directory_4"
    try:
        vector_store = Chroma(persist_directory=CHROMA_DATA_PATH, embedding_function = OpenAIEmbeddings(api_key))
        return vector_store
    except Exception as e:
        st.error(f"Error loading vector store: {e}")
        return None


    
    # return collection
    

collection = load_collection()

def retrieve_documents(query, collection):
    # Perform similarity search
    results = collection.similarity_search(query, k=3)
    
    docs = [result.page_content for result in results]
    metadatas = [result.metadata for result in results] 

    return [{'text': doc, 'metadata': meta} for doc, meta in zip(docs, metadatas)]


def generate_chatbot_response(context, query, metadata, chat_history):
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    metadata_info = "\n".join([f"File: {meta['description']}" for meta in metadata])
    prompt = f"Based on the following conversation history:\n\n{history_text}\n\nAnd the following information:\n\n{context}\n\nAdditional Information:\n{metadata_info}\n\nAnswer the following question:\n{query}"
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that helps students answer questions about Eskwelabs' Data Science Fellowship program."},
            {"role": "user", "content": prompt}
        ],
        temperature = 0.7
    )
    
    return response.choices[0].message.content.strip()
def chatbot_response(user_query, collection, chat_history):
    chat_history.add_message("user", user_query)
    
    retrieved_docs = retrieve_documents(user_query, collection)
    context = ' '.join([doc['text'] for doc in retrieved_docs])
    response = generate_chatbot_response(context, user_query, [doc['metadata'] for doc in retrieved_docs], chat_history.get_history())
    
    chat_history.add_message("assistant", response)
    return response

# # Initialize chat history
chat_history = ChatHistory()

user_query = st.text_input("Ask")
if user_query:
    response = chatbot_response(user_query, collection, chat_history)
    st.write(response)

if st.button("Clear history"):
    chat_history.clear_history()

chat_history.show_history()





