"""A module to collect sketchup setup."""

import json
import pathlib
import streamlit as st
from honeybee.model import Model
from pollination_streamlit_io import get_hbjson, send_geometry, send_hbjson
from .read_results import create_analytical_mesh

def get_model(here: pathlib.Path):
    # save HBJSON in data folder
    data = get_hbjson(key='pollination-model')

    if data:
        model_data = data['hbjson']
        hb_model = Model.from_dict(model_data)
        hbjson_path = pathlib.Path(f'./{here}/data/{hb_model.identifier}.hbjson')
        hbjson_path.parent.mkdir(parents=True, exist_ok=True)
        hbjson_path.write_text(json.dumps(hb_model.to_dict()))

        st.success('Model linked')
        # add to session state
        st.session_state.hbjson_path = hbjson_path

def set_result():
    st.session_state.result_json = create_analytical_mesh(
                results_folder=st.session_state.results_path,
                model=st.session_state.model_dict)

def show_result():
    send_geometry(geometry=st.session_state.result_json,
        key='sketchup-grids')
    send_hbjson(
        hbjson=st.session_state.model_dict,
        key='sketchup-model')