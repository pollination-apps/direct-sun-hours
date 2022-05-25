"""A module to collect API info."""

from pathlib import Path
import streamlit as st
from .query import Query
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.selectors import job_selector
from .cloud_run import post_process_job


def set_client_for_simulation(host: str) -> ApiClient:
    api_key = st.text_input(
        'Enter Pollination APIKEY', type='password',
        help=':bulb: You only need an API Key to access private projects. '
        'If you do not have a key already go to the settings tab under your profile to '
        'generate one.'
        )

    # create a query
    query = Query(host)
    query.owner = st.text_input(
        'Project Owner', value=query.owner
    )

    query.project = st.text_input(
        'Project Name', value=query.project
    )
    api_client = ApiClient(api_token=api_key)

    # add to session state 
    st.session_state.sim_client = api_client
    st.session_state.query = query


def set_client_for_results(here: Path):
    api_client = ApiClient()
    job = job_selector(api_client)
    if job:
        viz_file, results_path, model_dict, output_path = post_process_job(job, 
            here=here)
        st.session_state.viz_file = viz_file
        st.session_state.results_path = results_path
        st.session_state.model_dict = model_dict
        st.session_state.output_path = output_path