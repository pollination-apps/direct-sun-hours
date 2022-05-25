"""A module to collect rhino setup."""

import json
import pathlib
import streamlit as st
from honeybee.model import Model
from pollination_streamlit_io import special, button, inputs
from .shared import generate_vtk_model, show_vtk_viewer, run_res_viewer
from .read_results import create_analytical_mesh

def get_model(here: pathlib.Path):
    # save HBJSON in data folder
    token = special.sync(key='pollination-sync',
        delay=50)
    data = button.get(is_pollination_model=True,
        sync_token=token, 
        key='pollination-model')
    if data:
        model_data = data
        hb_model = Model.from_dict(model_data)
        hbjson_path = pathlib.Path(f'./{here}/data/{hb_model.identifier}.hbjson')
        hbjson_path.parent.mkdir(parents=True, exist_ok=True)
        hbjson_path.write_text(json.dumps(hb_model.to_dict()))

        # show the model
        vtk_path = generate_vtk_model(hbjson_path=hbjson_path,
            hb_model=hb_model)
        show_vtk_viewer(vtk_path)

        # add to session state
        st.session_state.hbjson_path = hbjson_path

def set_result():
    st.session_state.result_json = create_analytical_mesh(
                results_folder=st.session_state.results_path,
                model=st.session_state.model_dict)

def show_result():
    # display grids
    inputs.send(
        data=st.session_state.result_json,
        default_checked=True,
        label='Show Grids!',
        unique_id='unique-id-02',
        options={'layer': 'daylight_factor_results'}, 
        delay=1000,
        key='rhino-preview'
    )
    button.send(
        action='BakeGeometry',
        data=st.session_state.result_json,
        unique_id='bake-grids',
        key='rhino-bake-grids',
        platform='rhino'
    )
    button.send(
        action='BakePollinationModel',
        data=st.session_state.model_dict,
        unique_id='bake-model',
        key='rhino-bake-model',
        platform='rhino'
    )
    run_res_viewer()