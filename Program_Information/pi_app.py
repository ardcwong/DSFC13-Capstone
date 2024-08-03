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


if "stop" not in st.session_state:
    st.session_state.stop = True
    nltk.download('stopwords')

x = "No"

api_key = st.secrets[api]['api_key']
openai.api_key = api_key
client = OpenAI(api_key=api_key)
# SKLLMConfig.set_openai_key(api_key)
