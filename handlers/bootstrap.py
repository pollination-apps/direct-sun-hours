"""Init all session state variables"""

import streamlit as st

def initialize():
    # sim session
    if 'query' not in st.session_state:
        st.session_state.query = None
    if 'sim_client' not in st.session_state:
        st.session_state.sim_client = None
    if 'hbjson_path' not in st.session_state:
        st.session_state.hbjson_path = None
    if 'wea_path' not in st.session_state:
        st.session_state.wea_path = None
    # results session
    if 'viz_file' not in st.session_state:
        st.session_state.viz_file = None
    if 'results_path' not in st.session_state: 
        st.session_state.results_path = None
    if 'model_dict' not in st.session_state: 
        st.session_state.model_dict = None
    if 'output_path' not in st.session_state:
        st.session_state.output_path = None
    if 'result_json' not in st.session_state:
        st.session_state.result_json = None