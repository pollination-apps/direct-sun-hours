"""A module to collect revit setup."""

import json
import pathlib
import streamlit as st
from honeybee.model import Model
from pollination_streamlit_io import special, button
from .shared import generate_vtk_model, show_vtk_viewer, run_res_viewer
from .read_results import read_daylight_factor_results_from_folder


# ADN: @Konrad can you check this? :)
def get_model(here: pathlib.Path):
    data = special.get_hbjson(key='my-revit-json')
    if data:
        model_data = json.loads(data)
        hb_model = Model.from_dict(model_data)
        hbjson_path = pathlib.Path(f'./{here}/data/{hb_model.identifier}.hbjson')
        hbjson_path.parent.mkdir(parents=True, exist_ok=True)
        hbjson_path.write_text(data)

        # show the model
        vtk_path = generate_vtk_model(hbjson_path=hbjson_path,
            hb_model=hb_model)
        show_vtk_viewer(vtk_path)

        # add to session state
        st.session_state.hbjson_path = hbjson_path

def set_result():
    st.session_state.result_json = read_daylight_factor_results_from_folder(
        results_folder=st.session_state.results_path,
        output_folder=st.session_state.output_path,
        model=st.session_state.model_dict)

def show_result():
    button.send(
        action='AddResults',
        data=st.session_state.result_json,
        unique_id='bake-grids',
        key='bake-grids',
        platform='revit')
    button.send(
        action='ClearResults',
        data=st.session_state.result_json,
        unique_id='clear-grids',
        key='clear-grids',
        platform='revit')
    run_res_viewer()