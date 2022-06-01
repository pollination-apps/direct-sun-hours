"""A module to collect input functions."""
import streamlit as st

from handlers import (
    web,
    rhino,
    revit,
    sketchup,
    shared,
    cloud_run
)


def get_inputs(host: str,
               target_folder: str):
    if host.lower() == 'web':
        web.get_model(target_folder)
    elif host.lower() == 'rhino':
        rhino.get_model(target_folder)
    elif host.lower() == 'revit':
        revit.get_model(target_folder)
    elif host.lower() == 'sketchup':
        sketchup.get_model(target_folder)
    else:
        return

    wea, epw_path = shared.get_weather_file(target_folder)
    if epw_path:
        shared.set_wea_input(wea, epw_path)


def run_simulation():
    query = st.session_state.query
    client = st.session_state.sim_client
    hbjson_path = st.session_state.hbjson_path
    wea_path = st.session_state.wea_path

    # no login or last step wea
    if not query and not wea_path:
        return

    if st.button('Run Simulation'):
        cloud_run.run_cloud_simulation(query, client,
                                       hbjson_path, wea_path)
