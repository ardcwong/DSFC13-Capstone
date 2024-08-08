import streamlit as st
import requests
import io

st.image('data\anaconda.png')
# st.markdown(f"<h1 style='text-align: center;'> Installation Guide </h1>", unsafe_allow_html=True)
st.markdown(
    "<h1 style='text-align: center; color: #48a937; font-size: 70px;'>Installation Guide</h1>",
    unsafe_allow_html=True
)
st.divider()
st.markdown(
    """
    <p style='text-align: center; color: #333333; font-size: 20px;'>
        Welcome to the installation guide where you'll find all the necessary steps 
        to set up your environment and get started with the installation process of Anaconda.
    </p>
    """,
    unsafe_allow_html=True
)
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<h2 style='text-align: center;'>MAC OS</h2>", unsafe_allow_html=True)
    st.markdown("***Install on your MAC OS***")
    st.image(r'C:\Users\Nicole Barrion\anaconda3\envs\capstone_env\data\1.png')

with col2:
    st.markdown("<h2 style='text-align: center;'>WINDOWS</h2>", unsafe_allow_html=True)
    st.markdown("***Install on your Windows***")
    st.image(r'C:\Users\Nicole Barrion\anaconda3\envs\capstone_env\data\2.png')

with col3:
    st.markdown("<h2 style='text-align: center;'>RUN PYTHON</h2>", unsafe_allow_html=True)
    st.markdown("***Run Python in Anaconda***")
    st.image(r'C:\Users\Nicole Barrion\anaconda3\envs\capstone_env\data\3.png')

def fetch_pdf_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None

pdf_url_mac = 'https://drive.google.com/uc?export=download&id=1kBWygtPP5nkzCv9uR3AX2Y-PGjCFpeFr'
youtube_url_mac = 'https://www.youtube.com/watch?v=2xh5sjpAI6k'

pdf_url_windows = 'https://drive.google.com/uc?export=download&id=1bNYZP591fY5-rwjKbSYHAUuNjmYsqV9N'
youtube_url_windows = 'https://www.youtube.com/watch?v=UTqOXwAi1pE'

pdf_url_run = 'https://drive.google.com/uc?export=download&id=18DltGgOgzL3gbqlFCGxqG581g8fkFkHu'
youtube_url_run = 'https://www.youtube.com/watch?v=DPi6CAkUUPY'

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(
            """
            <a href="https://www.youtube.com/watch?v=2xh5sjpAI6k" target="_blank">
                <button style="background-color:#FF4B4B;color:white;padding:10px 20px;border:none;border-radius:5px;">
                    Youtube Video Installation Guide
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    #May isa pang button to proceed with download
    if st.button('PDF Guide for MAC OS', type="primary", use_container_width=True):
        pdf_content = fetch_pdf_content(pdf_url_mac)
        if pdf_content:
            st.download_button(
                label="Download PDF",
                data=pdf_content,
                file_name='MAC OS_Installation Guide.pdf',
                mime='application/pdf'
            )
            
    # # # Direct download once clicked
    # # with col4:
    # if st.button('Download Installation Guide for MAC OS', type="primary", use_container_width=True):
    #     pdf_content_mac = fetch_pdf_content(pdf_url_mac)
        
    # if pdf_content_mac:
    #     st.download_button(
    #         label='Download Installation Guide for MAC OS',
    #         data=pdf_content_mac,
    #         file_name='MAC_OS_Installation_Guide.pdf',
    #         mime='application/pdf'
    #     )

with col5:
    st.markdown(
            """
            <a href="https://www.youtube.com/watch?v=UTqOXwAi1pE" target="_blank">
                <button style="background-color:#FF4B4B;color:white;padding:10px 20px;border:none;border-radius:5px;">
                    Youtube Video Installation Guide 
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

    if st.button('PDF Guide for Windows', type="primary", use_container_width=True):
        pdf_content = fetch_pdf_content(pdf_url_windows)
        if pdf_content:
            st.download_button(
                label="Download PDF",
                data=pdf_content,
                file_name='Windows_Installation Guide.pdf',
                mime='application/pdf'
            )

with col6:

    st.markdown(
            """
            <a href="https://www.youtube.com/watch?v=DPi6CAkUUPY" target="_blank">
                <button style="background-color:#FF4B4B;color:white;padding:10px 20px;border:none;border-radius:5px;">
                    Youtube Video Installation Guide
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    if st.button('PDF Guide to Run Python', type="primary", use_container_width=True):
        pdf_content = fetch_pdf_content(pdf_url_run)
        if pdf_content:
            st.download_button(
                label="Download PDF",
                data=pdf_content,
                file_name='Run Python_Installation Guide.pdf',
                mime='application/pdf'
            )
