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
        vector_store = Chroma(persist_directory=CHROMA_DATA_PATH,
                              embedding_function  = OpenAIEmbeddings(api_key=openai.api_key))
        return vector_store
    except Exception as e:
        st.error(f"Error loading vector store: {e}")
        return None


    
    # return collection
    
collection = load_collection()
st.write(collection)

if collection:
    query = st.text_input("type")
    if query:
        results = collection.similarity_search(query, k=3)
        st.write(results)










