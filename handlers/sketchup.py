"""A module to collect sketchup setup."""

import json
import pathlib
import streamlit as st
from honeybee.model import Model
from pollination_streamlit_io import button
from .shared import generate_vtk_model, show_vtk_viewer, run_res_viewer
from .utils import create_grid_from_faces
from .read_results import create_analytical_mesh


def get_model(here: pathlib.Path):
    # save HBJSON in data folder
    st.warning('Sketchup does not support sync for now...')
    data = button.get(is_pollination_model=True,
                      key='pollination-model',
                      platform='sketchup')

    if data:
        # create grids
        with st.container():
            grid_size = st.number_input(
                label='Grid size(m)',
                min_value=0.1,
                max_value=5.0,
                value=0.6096)
            grid_height = st.number_input(
                label='Workplane height(m)',
                min_value=0.1,
                max_value=5.0,
                value=0.762)

        # honeybee openstudio does not expose grids :(
        st.write('Select a skp group to generate sensor grids.')
        faces = button.get(
            key='faces-for-sensors',
            button_text='Create SensorGrid',
            platform='sketchup')
        if faces:
            grids, error_msg = create_grid_from_faces(faces,
                                                      grid_size=grid_size, offset=grid_height)
            model_data = data
            hb_model = Model.from_dict(model_data)

            hb_model = hb_model.duplicate()
            if grids:
                hb_model.properties.radiance.add_sensor_grids([grids])
            else:
                st.warning('Unable to create sensor grids... '
                           'use a skp group made by planar faces.'
                           ' {}'.format('ERROR: ' + str(error_msg)))

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
    button.send(action='DrawGeometry',
                data=st.session_state.result_json,
                unique_id='bake-grids-skp',
                key='sketchup-grids',
                platform='sketchup')
    button.send(
        action='BakePollinationModel',
        data=st.session_state.model_dict,
        unique_id='bake-model',
        key='sketchup-bake-model',
        platform='sketchup'
    )
