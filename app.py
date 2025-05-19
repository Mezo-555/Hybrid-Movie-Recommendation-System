import Movies_Recommender
import streamlit as st
import random

# 🎯 **Streamlit Page Configuration**
favicon = ["🎶", "🎸", "🎹", "📯", "📻", "🎧", "🍿", "🎥", "🎞", "🎬", "📺", "📽"]
st.set_page_config(page_title="Movies Recommender", 
                   page_icon=random.choice(favicon), 
                   layout="wide")

# 🎯 **Hiding Streamlit's Default Menu**
hide_menu_style = """
    <style>
        .st-ae { caret-color: transparent; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# 🎯 **Launch the Recommender App**
Movies_Recommender.app()