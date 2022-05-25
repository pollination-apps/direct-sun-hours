"""A module to collect post-process functions."""

import streamlit as st
from pathlib import Path
from handlers import (
    web, 
    rhino,
    revit,
    sketchup,
    shared,
    api_cloud
)

def read(host: str, 
    target_folder: Path):

    api_cloud.set_client_for_results(target_folder)

    if st.session_state.output_path:
        if host == 'web':
            web.show_result()
        elif host == 'rhino':
            rhino.set_result()
            rhino.show_result()
        elif host == 'revit':
            revit.set_result()
            revit.show_result()
        elif host == 'sketchup':
            sketchup.set_result()
            sketchup.show_result()
        else:
            return