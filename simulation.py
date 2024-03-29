""" A module to run local calculation. """

import pathlib
import streamlit as st
from typing import Optional, Tuple
from lbt_recipes.recipe import Recipe
from honeybee.model import Model
from ladybug.wea import Wea
from query import Query
from honeybee_radiance.config import folders as rad_folders
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import Recipe as ItRecipe
from pollination_streamlit.interactors import NewJob, Job


def run_local_study(
        here: str,
        hb_model: Model,
        wea_path: pathlib.Path,
        timestep: Optional[int]=1, 
        north: Optional[int]=0, 
        cpu_count: Optional[int]=4, 
        min_sensor_count: Optional[int]=100, 
        grid_filter: Optional[str]='*') -> Tuple[bool, Exception]:
    """ Run local study """
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
        wea_path: pathlib.Path) -> Tuple[str, Exception]:
    """ Run cloud study """
    try:
        query.job_id = None
        # remember to add direct-sun-hours to your cloud project
        recipe = ItRecipe('ladybug-tools', 'direct-sun-hours',
            'latest', api_client)

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
  