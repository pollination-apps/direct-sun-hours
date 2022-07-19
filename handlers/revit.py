"""A module to collect revit setup."""

import json
import pathlib
import streamlit as st
from honeybee.model import Model
from pollination_streamlit_io import get_hbjson, send_results
from .read_results import read_daylight_factor_results_from_folder


# ADN: @Konrad can you check this? :)
def get_model(here: pathlib.Path):
    data = get_hbjson(key='my-revit-json')
    if data:
        model_data = json.loads(data['hbjson'])
        hb_model = Model.from_dict(model_data)
        hbjson_path = pathlib.Path(f'./{here}/data/{hb_model.identifier}.hbjson')
        hbjson_path.parent.mkdir(parents=True, exist_ok=True)
        hbjson_path.write_text(data)

        st.success('Model linked')
        # add to session state
        st.session_state.hbjson_path = hbjson_path


def set_result():
    st.session_state.result_json = read_daylight_factor_results_from_folder(
        results_folder=st.session_state.results_path,
        output_folder=st.session_state.output_path,
        model=st.session_state.model_dict)


def show_result():
    send_results(
        geometry=st.session_state.result_json,
        key='bake-grids')
