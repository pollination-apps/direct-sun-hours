
""" A module for inputs. """

import pathlib
import streamlit as st
from query import Query
from pollination_streamlit.api.client import ApiClient


def initialize():
    """Initialize any of the session state variables if they don't already exist."""
    if 'target_folder' not in st.session_state:
        st.session_state.target_folder = pathlib.Path('/home/ladybugbot/app').resolve()
    if 'valid_report' not in st.session_state:
        st.session_state.valid_report = None
    # sim session
    if 'query' not in st.session_state:
        st.session_state.query = None
    if 'sim_client' not in st.session_state:
        st.session_state.sim_client = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
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
    if 'result_json' not in st.session_state:
        st.session_state.result_json = None


def set_api_client(host: str,
    api_key: str,
    owner: str,
    project: str) -> ApiClient:
    # TODO: replace components with auth pollination-streamlit-io

    # create a query
    query = Query(host)
    query.owner = owner
    query.project = project

    api_client = ApiClient(api_token=api_key)

    # add to session state
    st.session_state.sim_client = api_client
    st.session_state.query = query
    st.session_state.api_key = api_key
    st.session_state.owner = query.owner
    st.session_state.project = query.project

  
def get_api_inputs(host: str, container):
    with container:
        api_key = st.sidebar.text_input(
            'Enter Pollination APIKEY', type='password',
            help=':bulb: You only need an API Key to access private projects. '
            'If you do not have a key already go to the settings tab under your profile to '
            'generate one.'
        )
        owner_name = st.sidebar.text_input('Project Owner')
        project_name = st.sidebar.text_input('Project Name')

        set_api_client(host=host, 
            api_key=api_key,
            owner=owner_name,
            project=project_name)




