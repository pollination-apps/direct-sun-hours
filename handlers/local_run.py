""" A module to run local calculation. """

import json
import pathlib
import streamlit as st
from typing import Optional
from lbt_recipes.recipe import Recipe
from honeybee.model import Model
from ladybug.wea import Wea
from honeybee_radiance.config import folders as rad_folders

from handlers.shared import get_vtk_model_result

def run_simulation(
    here: str,
    hbjson_path: pathlib.Path,
    wea_path: pathlib.Path,
    timestep: Optional[int]=1, 
    north: Optional[int]=0, 
    cpu_count: Optional[int]=4, 
    min_sensor_count: Optional[int]=100, 
    grid_filter: Optional[str]='*'):

    # reload model
    data = hbjson_path.read_text()
    model_data = json.loads(data)
    hb_model = Model.from_dict(model_data)

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

    simulation_path = pathlib.Path(f'{here}/simulation')
    simulation_path.mkdir(parents=True, exist_ok=True)

    # set rad folder
    rad_folders.radiance_path = '/home/ladybugbot/'

    project_folder = recipe.run(f'--workers 16 --folder {simulation_path.as_posix()}',
        radiance_check=True)

    st.session_state.results_path = f'{project_folder}/direct_sun_hours/results/cumulative'
    st.session_state.model_dict = model_data


def set_output():
    res_folder = pathlib.Path(st.session_state.results_path)

    viz_file = get_vtk_model_result(st.session_state.model_dict,
        res_folder,
        res_folder)
    
    st.session_state.viz_file = viz_file