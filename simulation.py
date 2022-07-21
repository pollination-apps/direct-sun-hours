""" A module to run local calculation. """

from pollination_streamlit.selectors import job_selector
import json
import pathlib
import streamlit as st
from typing import Optional
from lbt_recipes.recipe import Recipe
from honeybee.model import Model
from ladybug.wea import Wea
from helper import create_analytical_mesh
from outputs import get_vtk_model_result
from query import Query
from honeybee_radiance.config import folders as rad_folders
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import Recipe as ItRecipe
from pollination_streamlit.interactors import NewJob, Job
import zipfile
from pollination_streamlit_io import send_geometry, send_hbjson

def run_local_study(
        here: str,
        hb_model: Model,
        wea_path: pathlib.Path,
        timestep: Optional[int]=1, 
        north: Optional[int]=0, 
        cpu_count: Optional[int]=4, 
        min_sensor_count: Optional[int]=100, 
        grid_filter: Optional[str]='*'):

    try:
        # reload wea
        wea = Wea.from_file(wea_path)

        recipe = Recipe('direct-sun-hours')
        recipe.input_value_by_name('model', hb_model)
        recipe.input_value_by_name('timestep', timestep)
        recipe.input_value_by_name('north', north)
        recipe.input_value_by_name('cpu-count', cpu_count)
        recipe.input_value_by_name('min-sensor-count', min_sensor_count)
        recipe.input_value_by_name('wea', wea)
        recipe.input_value_by_name('grid-filter', grid_filter)

        simulation_path = pathlib.Path(f'{here}/local_simulation')
        simulation_path.mkdir(parents=True, exist_ok=True)

        # set rad folder
        rad_folders.radiance_path = '/home/ladybugbot/'
    
        project_folder = recipe.run(f'--workers 16 --folder {simulation_path.as_posix()}',
            radiance_check=True)
        st.session_state.result_path = pathlib.Path(f'{project_folder}/direct_sun_hours/results/cumulative')
        st.session_state.hb_model_dict = hb_model.to_dict()
        return True, None
        
    except Exception as e:
        st.session_state.result_path = None
        st.session_state.hb_model_dict = None
        return False, e


def run_cloud_study(query: Query,
        api_client: ApiClient,
        model_path: pathlib.Path,
        wea_path: pathlib.Path):
    try:
        query.job_id = None
        # remember to add direct-sun-hours to your cloud project
        recipe = ItRecipe('ladybug-tools', 'direct-sun-hours',
            '0.5.5-viz', api_client)

        new_job = NewJob(query.owner,
            query.project,
            recipe,
            client=api_client)

        model_project_path = new_job.upload_artifact(model_path)

        wea_project_path = new_job.upload_artifact(wea_path)

        q = {
            'model': model_project_path,
            'wea': wea_project_path,
            'min-sensor-count': 100
        }

        new_job.arguments = [q]
        job = new_job.create() # run
        query.job_id = job.id

        return job.id, None

    except Exception as e:
        st.session_state.results_path = None
        return None, e


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
        if host == 'web':
            get_vtk_model_result(model, 
                st.session_state.result_path, container)
        else:
            # generate grids
            analysis_grid = create_analytical_mesh(st.session_state.result_path, 
                model)
            with container:
                send_geometry(geometry=analysis_grid,
                    key='po-grids')
                send_hbjson(
                    hbjson=model,
                    key='po-model')
    
    # TODO: Add revit
    # send_results(
    # geometry=st.session_state.result_json,
    # key='bake-grids')

        