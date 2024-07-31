import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from skllm.config import SKLLMConfig
from skllm.models.gpt.text2text.summarization import GPTSummarizer
from sentence_transformers import SentenceTransformer, util
import openai
from openai import OpenAI
from wordcloud import WordCloud
import subprocess
import time
import numpy as np
import ast #built in
from annotated_text import annotated_text
# Custom function to download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

###
api_key = st.secrets['api_key']
client = OpenAI(api_key=api_key)
SKLLMConfig.set_openai_key(api_key)

# st.set_page_config(layout='wide')

st.markdown('<p style="font-size: 14px; color: red; text-align: center;"><strong>⚠️ This app is not intended for self-diagnosis or self-treatment. Always consult a qualified healthcare professional for medical advice and diagnosis. ⚠️</strong></p>', unsafe_allow_html=True)

# disable?
x = "No"

# DATA SET
df = pd.read_csv('data/medquad-cleaned.csv')
df = df.drop_duplicates(subset=['question'])
df['lemmatized_answer_tokens'] = [' '.join(ast.literal_eval(x)) for x in  df['lemmatized_answer_tokens']]
# df['lemmatized_answer_tokens'] = [ast.literal_eval(x) for x in  df['lemmatized_answer_tokens']]
# df = df.iloc[:3000]


# Define your focus areas
focus_areas = df['focus_area'].str.lower().unique().tolist()
def disable_openai(x):
    if x == "Yes":
        disable = 1
    else:
        disable = 0
    return disable

def generate_response(focus_area, prompt):
    disable = disable_openai(x)
    if disable == 1:
        return []
    else:
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system',
                     'content':
                     f"Perform the specified tasks based on this focus area:\n\n{focus_area}"},
                    {'role': 'user', 'content': prompt}
                ]
            )

            return response.choices[0].message.content
        except:
            return []

def summarize_answer(focus_area):
    prompt = f'Summarize the answer in easy to understand terms and words'
    summary = generate_response(focus_area, prompt)
    return summary

def generate_response(summary, prompt):
    disable = disable_openai(x)
    if disable == 1:
        return []
    else:
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system',
                     'content':
                     f"Perform the specified tasks based on this summary:\n\n{summary}"},
                    {'role': 'user', 'content': prompt}
                ]
            )
            return response.choices[0].message.content
        except:
            return []


def specialty_doctor_recommendation(summary):
    if summary:
        prompt = f'Which specialty doctor should I consult?:\n\n{summary}'
        doctor_recommendation = generate_response(summary, prompt)
        return doctor_recommendation
    else:
        return []
    

def initializing():
        msg = st.toast('Getting Ready...')
        time.sleep(1)
        msg.toast('Initializing...')
        time.sleep(1)
        msg.toast('Ready!', icon = "🥞")
        status = 1

# FOR SEMANTIC SIMILARITIES MATCHING
def get_synsets(text):
        tokens = word_tokenize(text)
        synsets = [wn.synsets(token) for token in tokens]
        synsets = [item for sublist in synsets for item in sublist]  # Flatten list
        return synsets
# Compute similarity
def compute_similarity(synsets1, synsets2):
    max_similarity = 0
    for synset1 in synsets1:
        for synset2 in synsets2:
            similarity = synset1.path_similarity(synset2)
            if similarity and similarity > max_similarity:
                max_similarity = similarity
    return max_similarity

def search_keyword(keyword, text_list):
    focus_area_embeddings = np.load('data/focus_area_embeddings.npy') # load

    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    keyword_embedding = model.encode(keyword)
    similarities = util.pytorch_cos_sim(keyword_embedding, focus_area_embeddings)

    best_match_index = similarities.argmax()

    best_match_focus_area = text_list[int(best_match_index)]

    return best_match_focus_area


def process_keyword(keyword, df, best_match_focus_area):
    column1, column2 = st.columns([1,1])

    # keyword_synsets = get_synsets(keyword)
    # focus_area_synsets = {area: get_synsets(area) for area in focus_areas}

    # # Calculate similarities
    # similarities = {}
    # for area, synsets in focus_area_synsets.items():
    #     similarity = compute_similarity(keyword_synsets, synsets)
    #     similarities[area] = similarity


    # # Find the focus area with the highest similarity
    # best_match_focus_area = max(similarities, key=similarities.get)

    column2.caption("FOCUS AREA")
    highlighted_fa = ""
    highlighted_fa += f"<span style='background-color:#FAA8A8;padding: 5px; border-radius: 5px; margin-right: 5px;'>{best_match_focus_area.upper()}</span>"
    column2.markdown(highlighted_fa, unsafe_allow_html=True)
    # column2.caption(best_match_focus_area.upper())
    focus_area = best_match_focus_area

    if focus_area:

        # Filter answers by the selected focus area
        filtered_df = df[df['focus_area'].str.lower().str.contains(focus_area, case=False, na=False)]

        if not filtered_df.empty:
            # Concatenate all answers into a single text
            all_answers_text = " ".join(filtered_df['answer'].dropna().tolist())
            lemmatized_answer = " ".join(filtered_df['lemmatized_answer_tokens'].dropna().tolist())
            summary = summarize_answer(all_answers_text)

            top_keywords = extract_keywords(all_answers_text)
            column1.caption('TOP KEYWORDS')
            if top_keywords:
                highlighted_keywords = ""
                for i, keyword in enumerate(top_keywords):
                    highlighted_keywords += f"<span style='background-color:#FFD3D3;padding: 5px; border-radius: 5px; margin-right: 5px;'>{keyword}</span>"

                column1.markdown(highlighted_keywords, unsafe_allow_html=True)

            else:
                highlighted_tkw = ""
                highlighted_tkw += f"<span style='background-color:#96BAC5;padding: 5px; border-radius: 5px; margin-right: 5px;'>{'Top Keywords is unavailable.'}</span>"
                column1.markdown(highlighted_tkw, unsafe_allow_html=True)


            if summary:
                column1.markdown(summary)
                column1.caption("SOURCE")
                source = filtered_df['source'].iloc[0]
                # column1.subheader("Source")
                column1.markdown(source)
            else:
                highlighted_summ = ""
                highlighted_summ += f"<span style='background-color:#96BAC5;padding: 5px; border-radius: 5px; margin-right: 5px;'>{'Summarizer is unavailable. Showing all info.'}</span>"
                column1.markdown(highlighted_summ, unsafe_allow_html=True)
                column1.markdown(all_answers_text)
                column1.caption("SOURCE")
                source = filtered_df['source'].iloc[0]
                column1.markdown(source)
            # Generate word cloud of content of summary of answers
            # column2.dataframe(filtered_df['lemmatized_answer_tokens'])
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(lemmatized_answer)
            st.session_state['wordcloud'] = wordcloud

            # Display the word cloud
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            column2.pyplot(plt)
            doctor_recommendation = specialty_doctor_recommendation(summary)
            column2.subheader("Recommended Doctor for Consultation")
            if doctor_recommendation:
                column2.markdown(doctor_recommendation)
            else:
                highlighted_dr = ""
                highlighted_dr += f"<span style='background-color:#96BAC5;padding: 5px; border-radius: 5px; margin-right: 5px;'>{'Doctor Recommender is unavailable.'}</span>"
                column2.markdown(highlighted_dr, unsafe_allow_html=True)

        else:
            st.session_state['summary'] = "No matching focus areas found."
            st.session_state['wordcloud'] = None

    return focus_area, summary, filtered_df

def select_questions(filtered_df):
    st.subheader("You may also want to know")
    selected_question = st.selectbox("Choose Question",filtered_df['question'].tolist())
    if selected_question:
        # Display the selected question and its answer
        # st.write("Selected Question:", selected_question)

        selected_answer = filtered_df[filtered_df['question'] == selected_question]['answer'].values[0]
        container = st.container(border=True)
        container.subheader("ANSWER:")
        top_keywords_ans = extract_keywords(selected_answer)
        container.caption('TOP KEYWORDS')
        if top_keywords_ans:
            highlighted_keywords_ans = ""
            for i, keyword in enumerate(top_keywords_ans):
                highlighted_keywords_ans += f"<span style='background-color:#FFD3D3;padding: 5px; border-radius: 5px; margin-right: 5px;'>{keyword}</span>"

            container.markdown(highlighted_keywords_ans, unsafe_allow_html=True)

        else:
            highlighted_tkw_ans = ""
            highlighted_tkw_ans += f"<span style='background-color:#96BAC5;padding: 5px; border-radius: 5px; margin-right: 5px;'>{'Top Keywords is unavailable.'}</span>"
            container.markdown(highlighted_tkw_ans, unsafe_allow_html=True)

        container.write(selected_answer)
        container.caption("SOURCE")
        source = filtered_df['source'].iloc[0]
        container.markdown(source)




def extract_keywords(text):
        system_prompt = 'You are a health professional assistant tasked to extract keywords from medical question answering dataset.'

        main_prompt = """
        ###TASK###

    Extract the five most crucial keywords from the medical question answering dataset.
    Extracted keywords must be listed in a comma-separated list.
    Example: Glaucoma, optic nerve, vision loss, eye, treatment

        ###HEALTH###
        """
        disable = disable_openai(x)
        if disable == 1:
            return []
        else:
            try:
                response = client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{main_prompt}\n{text}"}
                    ]
                )
                top_keywords = response.choices[0].message.content
                return [kw.strip() for kw in top_keywords.split(',')]

            except:
                return []

def telemedicine():
    st.subheader('Telemedicine and Specialty Doctors')

    # Original text with website titles and URLs
    text = """
    For telemedicine consultations or to find the nearest specialty doctor near you, you may visit:

    <b>NowServing</b>: https://nowserving.ph/<br><b>Konsulta MD</b>: https://konsulta.md/<br><b>SeriousMD</b>: https://seriousmd.com/healthcare-super-app-philippines
    """
    # st.link_button("Now Serving", "https://nowserving.ph")
    # st.link_button("Konsulta MD", "https://konsulta.md/")
    # st.link_button("SeriousMD", "https://seriousmd.com/healthcare-super-app-philippines")
    # Display formatted text with st.markdown
    st.markdown(text, unsafe_allow_html=True)

#---------------------MAIN PROGRAM----------------------#


# ENTER KEYWORD FOR SEMANTIC SIMILARITIES MATCHING WITH FOCUS AREA
st.subheader("Welcome to ➕HealthPlus!")

tab1, tab2 = st.tabs(["About the App    ", "How to Use    "])
with tab1:
    col1, col2 = st.columns([1,1])
    col1.image('data/art.png')
    col2.write("")
    col2.write("")
    col2.write("")
    content = """
<b style='color:#0C3974;'>HealthPlus</b> empowers you with reliable medical knowledge, making healthcare information accessible to all through the <b style='color:#0C3974;'>provision of accessible and easy-to-understand medical information</b>. Leveraging the power of the MedQuAD dataset and advanced AI, it <b style='color:#0C3974;'>enhances public health literacy and supports telemedicine consultations.</b> Whether you’re a patient managing a chronic condition, a caregiver needing clear explanations, a healthcare provider requiring quick and reliable information, or a health enthusiast looking for health tips, MedInfoHub is your go-to resource for trusted medical knowledge.
"""
    col2.markdown(content, unsafe_allow_html=True)
    col2.write("*The MedQuAD dataset aggregates content from reputable sources like the National Institutes of Health (NIH), National Library of Medicine (NLM), and other authoritative medical organizations.")
with tab2:
    col1, col2 = st.columns([1,1])
    col1.image('data/art.png')
    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.title("Instructions:")
        content_inst = """
        (1) Enter a Keyword to Search<br>(2) Choose Keyword Search Method<br>(3) Choose Focus Area (Applicable for Exact Word search method)<br>(4) Retrieve Information about Focus Area<br><br>
        """
        st.markdown(content_inst, unsafe_allow_html=True)
        annotated_text(("Focus Area", ""),": A category or specific subject within a broader topic that helps refine and target the search results more effectively.",)
st.divider()    
# inst1, inst2 = st.columns([1,10])
# inst1.caption("Instructions:")
# inst2.caption("""(1) Enter a Keyword to Search, (2) Choose Keyword Search Method, (3) Choose Focus Area (Applicable for Exact Word Search Method, (4) Retrieve Information about Focus Area""")
# st.write("Instructions:", help = "(1) Enter a Keyword to Search, (2) Choose Keyword Search Method, (3) Choose Focus Area (Applicable for Exact Word Search Method, (4) Retrieve Information about Focus Area")


st.markdown("<h1 style='text-align: center;'>➕HealthPlus</h1>", unsafe_allow_html=True)    
a, b, c = st.columns([1,1,1])

keyword = a.text_input("Enter a keyword to search:", help = "Type the keyword you want to search for. (e.g. diabetes, cancer, Stomach pain, psoriasis, ...)")
st.title(keyword)
if keyword:

    choose_method = b.selectbox(
            "Choose Keyword Search Method",
            ("Exact Word","Best Match"), help = 'Exact Word: Returns every focus area that contains the word in "Enter a keyword to search:" | Best Match utilizes Sentence Transformers for words matching.')
    st.session_state.choosemethod = choose_method
    if st.session_state.choosemethod == 'Exact Word':
        filtered_df = df[df['focus_area'].str.lower().str.contains(keyword, case=False, na=False)]
        focus_area_choose = c.selectbox(
                "Choose (1) from matched Focus Area/s",
                filtered_df["focus_area"].sort_values(ascending = True).str.lower().unique().tolist(), index=None, help = "Select one of the focus areas that match your search keyword.")
        st.session_state.fac = focus_area_choose
        # if a.button("View Information", type = "primary", use_container_width = True):
        
        if focus_area_choose:
            focus_area, summary, filtered_df = process_keyword(keyword, df, st.session_state.fac)
            select_questions(filtered_df)
            # doctor_recommendation = specialty_doctor_recommendation(summary)
            # column2.markdown(doctor_recommendation)
            telemedicine()
  
    elif st.session_state.choosemethod == 'Best Match':
        # if a.button("View Information", type = "primary", use_container_width = True):
        # # Filter questions containing the keyword
        # filtered_df = df[df['question'].str.contains(keyword, case=False, na=False)]
        best_match_focus_area = search_keyword(keyword, df['focus_area'])
        focus_area, summary, filtered_df = process_keyword(keyword, df, best_match_focus_area)
        select_questions(filtered_df)
        telemedicine()
        # else:
        #     if st.session_state.fac == None:
        #         st.error("Please choose a focus area first.")
# else:
#     st.info("Please enter a keyword to search.")
        
