"""A module to collect post-process functions."""

import streamlit as st
from pathlib import Path
from handlers import (
    web,
    rhino,
    revit,
    sketchup,
    shared,
    api_cloud,
    local_run
)


def read_from_cloud(host: str,
         target_folder: Path):
    api_cloud.set_client_for_results(target_folder)
    if st.session_state.results_path:
        show_result(host)

def read_from_local(host: str,
         target_folder: Path):
    if st.session_state.results_path:
        local_run.set_output()
        show_result(host)

def show_result(host):
    if st.session_state.results_path:
        if host.lower() == 'web':
            web.show_result()
        elif host.lower() == 'rhino':
            rhino.set_result()
            rhino.show_result()
        elif host.lower() == 'revit':
            revit.set_result()
            revit.show_result()
        elif host.lower() == 'sketchup':
            sketchup.set_result()
            sketchup.show_result()
        else:
            return
