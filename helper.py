"""A module to collect helper functions."""

import streamlit as st

def local_css(file_name):
    """Load local css file."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)