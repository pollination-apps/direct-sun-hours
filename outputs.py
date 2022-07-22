""" A module for outpus. """

import json
import zipfile
import pathlib
import streamlit as st
from honeybee.model import Model
from honeybee_vtk.model import Model as VTKModel
from honeybee_vtk.vtkjs.schema import SensorGridOptions
from honeybee_vtk.model import (HBModel,
                                Model as VTKModel,
                                SensorGridOptions,
                                DisplayMode)
from pollination_streamlit_viewer import viewer
from pollination_streamlit.selectors import job_selector
from helper import create_analytical_mesh, read_results_from_folder
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit_io import send_geometry, send_hbjson, send_results

def get_vtk_config(res_folder: pathlib.Path) -> str:
    """Write Direct Sun Hours config to a folder."""

    cfg = {
        "data": [
            {
                "identifier": "Direct Sun Hours",
                "object_type": "grid",
                "unit": "Hour",
                "path": res_folder.as_posix(),
                "hide": False,
                "legend_parameters": {
                    "hide_legend": False,
                    "color_set": "nuanced",
                    "label_parameters": {
                        "color": [34, 247, 10],
                        "size": 0,
                        "bold": True
                    }
                }
            }
        ]
    }

    config_file = res_folder.parent.joinpath('config.json')
    config_file.write_text(json.dumps(cfg))

    return config_file.as_posix()


def get_vtk_model_result(model_dict: dict, 
    simulation_folder: pathlib.Path,
    cfg_file,
    container):
    """ Get the viewer """
    if not st.session_state.vtk_result_path:
        # load the configuration file
        hb_model = HBModel.from_dict(model_dict)
        hbjson_path = hb_model.to_hbjson(
            hb_model.identifier,
            simulation_folder)
    
        vtk_model = VTKModel.from_hbjson(hbjson_path, SensorGridOptions.Mesh)
        vtk_result_path = vtk_model.to_vtkjs(folder=simulation_folder.resolve(),
            config=cfg_file,
            model_display_mode=DisplayMode.Wireframe,
            name=hb_model.identifier)
        st.session_state.vtk_result_path = vtk_result_path
    vtk_result_path = st.session_state.vtk_result_path

    with container:
        viewer(content=pathlib.Path(vtk_result_path).read_bytes(), 
            key='vtk_res_model')


def get_output(host: str, container):
    api_client = ApiClient(api_token=st.session_state.api_key)
    with container:
        if st.session_state.is_cloud:
            job = job_selector(api_client) # is a st.text_input
            if job and job.id != st.session_state.job_id:
                st.session_state.vtk_result_path = None
                st.session_state.job_id = job.id

                run = job.runs[0]
                input_model_path = job.runs_dataframe.dataframe['model'][0]

                simulation_folder = pathlib.Path(st.session_state.target_folder, 
                    run.id)
                res_folder = simulation_folder.joinpath('cloud_results')
                res_folder.mkdir(parents=True, exist_ok=True)

                # download results
                res_zip = run.download_zipped_output('cumulative-sun-hours')
                with zipfile.ZipFile(res_zip) as zip_folder:
                    zip_folder.extractall(res_folder.as_posix())

                model_dict = json.load(job.download_artifact(input_model_path))
                st.session_state.hb_model_dict = model_dict
                st.session_state.result_path = res_folder
         
        viz_result(host, 
            st.session_state.hb_model_dict, 
            container)


def viz_result(host:str, model:dict, container):
    if st.session_state.result_path:
        cfg_file = get_vtk_config(
            res_folder=st.session_state.result_path.resolve())
        if host == 'web':
            get_vtk_model_result(model, 
                st.session_state.result_path, 
                cfg_file, 
                container)
        elif host == 'sketchup' or host == 'rhino':
            # generate grids
            analysis_grid = create_analytical_mesh(st.session_state.result_path, 
                model)
            with container:
                send_geometry(geometry=analysis_grid,
                    key='po-grids')
                send_hbjson(
                    hbjson=model,
                    key='po-model')
        elif host == 'revit':
            # generate body message
            message = read_results_from_folder(st.session_state.result_path, 
                cfg_file, model)
            send_results(
                geometry=message,
                key='bake-grids')