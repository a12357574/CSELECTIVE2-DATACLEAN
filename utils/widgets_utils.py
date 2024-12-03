import time
import streamlit as st

def progress_bar(progress_text):
    progress_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)

    progress_bar.empty()
