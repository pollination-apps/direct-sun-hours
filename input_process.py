"""A module to collect input functions."""
import pathlib
import streamlit as st

from handlers import (
    web,
    rhino,
    revit,
    sketchup,
    shared,
    cloud_run,
    local_run
)

import json
import pathlib
import streamlit as st
from honeybee.model import Model
from pollination_streamlit_io import get_hbjson
from pollination_streamlit_viewer import viewer
from honeybee_vtk.model import (HBModel,
                                Model as VTKModel,
                                SensorGridOptions,
                                DisplayMode)


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

def vtk_model_preview(hbjson_path: pathlib.Path,
    hb_model: Model) -> str:
    vtk_path = VTKModel.from_hbjson(hbjson_path.as_posix(), 
        SensorGridOptions.Sensors).to_vtkjs(
        folder=hbjson_path.parent, name=hb_model.identifier)
    viewer(content=pathlib.Path(vtk_path).read_bytes(), key='vtk_preview_model')


def get_model(target_folder: pathlib.Path):
    # save HBJSON in data folder
    data = get_hbjson(key='pollination-model')

    if data:
        model_data = data['hbjson']
        hb_model = Model.from_dict(model_data)
        hbjson_path = pathlib.Path(f'./{target_folder}/data/{hb_model.identifier}.hbjson')
        hbjson_path.parent.mkdir(parents=True, exist_ok=True)
        hbjson_path.write_text(json.dumps(hb_model.to_dict()))

        st.success('Model linked')
        # add to session state
        st.session_state.hbjson_path = hbjson_path

        check_model = st.checkbox('Check model')
        if check_model:
            vtk_model_preview(hbjson_path=hbjson_path,
            hb_model=hb_model)



def run_cloud_simulation():
    query = st.session_state.query
    client = st.session_state.sim_client
    hbjson_path = st.session_state.hbjson_path
    wea_path = st.session_state.wea_path

    # no login or last step wea
    if not hbjson_path and not wea_path:
        return

    if st.button('Run Simulation'):
        cloud_run.run_cloud_simulation(query, client,
                                       hbjson_path, wea_path)

def run_local_simulation(target_folder: str):
    hbjson_path = st.session_state.hbjson_path
    wea_path = st.session_state.wea_path

    # no last step wea
    if not wea_path:
        return

    if st.button('Run Simulation'):
        local_run.run_simulation(here=target_folder, 
            hbjson_path=hbjson_path, 
            wea_path=wea_path)
