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
from pollination_streamlit.interactors import Job
from helper import create_analytical_mesh, read_results_from_folder
from pollination_streamlit_io import (send_geometry, send_hbjson, 
    send_results, select_study, select_project)
from inputs import is_api_client_valid


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
    # TODO: clean this method
    with container:
        if st.session_state.is_cloud:
            if is_api_client_valid():
                api_client = st.session_state.api_client
                user = st.session_state.user

                pcol1, pcol2 = st.columns(2)
                if user and 'username' in user:
                    with pcol1:
                        project = select_project(
                            'out-select-project',
                            api_client,
                            project_owner=user['username']
                        )               
                    if project and 'name' in project:
                        with pcol2:
                            study = select_study(
                                'out-select-study',
                                api_client,
                                project_name=project['name'],
                                project_owner=user['username']
                            )
                        if study:
                            job = Job(owner=user['username'], project=project['name'], id=study['id'],
                                client=api_client)
                            # job = job_selector(api_client) # is a st.text_input
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
            else:
                st.warning('Please, check API data on the sidebar.')
                return
         
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
            results = create_analytical_mesh(st.session_state.result_path, 
                model)
            with container:
                col1, col2 = st.columns(2)
                with col1:
                    send_results(results=results,
                        key='po-results')
                with col2:
                    send_hbjson(
                        hbjson=model,
                        key='po-model')
        elif host == 'revit':
            # generate body message
            message = read_results_from_folder(st.session_state.result_path, 
                cfg_file, model)
            send_results(
                results=message,
                key='bake-grids')