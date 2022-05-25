"""A module to collect web setup."""

import json
import pathlib
import streamlit as st
from honeybee.model import Model
from .shared import generate_vtk_model, show_vtk_viewer, run_res_viewer

def get_model(here: pathlib.Path):
    hbjson_file = st.file_uploader(
        'Upload a hbjson file', 
        type=['hbjson', 'json'])
    if hbjson_file:
        # save HBJSON in data folder
        hbjson_path = pathlib.Path(f'./{here}/data/{hbjson_file.name}')
        hbjson_path.parent.mkdir(parents=True, exist_ok=True)
        data = hbjson_file.read()
        hbjson_path.write_bytes(data)
        model_data = json.loads(data)
        hb_model = Model.from_dict(model_data)

        vtk_path = generate_vtk_model(hbjson_path=hbjson_path,
            hb_model=hb_model)
        show_vtk_viewer(vtk_path)

        # add to session state
        st.session_state.hbjson_path = hbjson_path

def show_result():
    run_res_viewer()