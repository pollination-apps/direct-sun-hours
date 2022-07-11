"""A module to collect rhino setup."""

import json
import pathlib
import streamlit as st
from honeybee.model import Model
from pollination_streamlit_io import get_hbjson, send_geometry, send_hbjson
from .shared import generate_vtk_model, show_vtk_viewer, run_res_viewer
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

        # add to session state
        st.session_state.hbjson_path = hbjson_path


def set_result():
    st.session_state.result_json = create_analytical_mesh(
        results_folder=st.session_state.results_path,
        model=st.session_state.model_dict)


def show_result():
    # display grids
    send_geometry(
        geometry=st.session_state.result_json,
        key='rhino-preview'
    )
    send_hbjson(
        hbjson=st.session_state.model_dict,
        key='rhino-model'
    )
