import streamlit as st


def get_api_key():
    return st.secrets["ALCHEMY_API_KEY"]
