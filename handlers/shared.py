"""A module to collect shared logic."""

import pathlib
import streamlit as st
from pathlib import Path
from honeybee.model import Model
from honeybee_vtk.model import Model as VTKModel
from honeybee_vtk.vtkjs.schema import SensorGridOptions
from ladybug.analysisperiod import AnalysisPeriod
from streamlit_vtkjs import st_vtkjs
from ladybug.wea import Wea
from viz import get_vtk_config
from honeybee_vtk.model import (HBModel,
                                Model as VTKModel,
                                SensorGridOptions,
                                DisplayMode)


def generate_vtk_model(hbjson_path: Path,
    hb_model: Model) -> str:
    vtk_path = VTKModel.from_hbjson(hbjson_path.as_posix(), 
        SensorGridOptions.Sensors).to_vtkjs(
        folder=hbjson_path.parent, name=hb_model.identifier)
    
    return vtk_path

def show_vtk_viewer(vtk_path: str):
    st_vtkjs(
        content=Path(vtk_path).read_bytes(),
        key='vtk_preview_model'
    )

def get_weather_file(here: Path):
    # upload weather file
    epw_file = st.file_uploader(
        'Upload a weather file (EPW)', 
        type=['epw']
        )
    if epw_file:
        wea, epw_path = generate_wea_file(epw_file, here)
        return wea, epw_path
    else:
        return None, None

def generate_wea_file(epw_file: str,
    here: Path):
    # save EPW in data folder
    epw_path = Path(f'./{here}/data/{epw_file.name}')
    epw_path.parent.mkdir(parents=True, exist_ok=True)
    epw_path.write_bytes(epw_file.read())
    return Wea.from_epw_file(epw_file=epw_path), epw_path

def set_wea_input(wea: Wea, epw_path: Path):
    start_hour = st.slider(label='Start hour', min_value=0, max_value=23, value=9)
    start_day = st.slider(label='Start day', min_value=1, max_value=31, value=21)
    start_month = st.slider(label='Start month', min_value=1, max_value=12, value=6)
    end_hour = st.slider(label='End hour', min_value=0, max_value=23, value=15)
    end_day = st.slider(label='End day', min_value=1, max_value=31, value=21)
    end_month = st.slider(label='End month', min_value=1, max_value=12, value=6)

    period = AnalysisPeriod(st_month=start_month,
        st_day=start_day, st_hour=start_hour, end_hour=end_hour,
        end_day=end_day, end_month=end_month)

    if period:
        wea = wea.filter_by_hoys(period.hoys)
    
    # save wea
    wea_path = epw_path.as_posix()
    wea_path = wea_path.replace('.epw', '.wea')

    wea.write(wea_path)
    wea_path = pathlib.Path(wea_path)

    # add to session state
    st.session_state.wea_path = wea_path

def get_vtk_model_result(model_dict: dict, 
    simulation_folder: pathlib.Path):
    # load the configuration file
    cfg_file = get_vtk_config(folder=simulation_folder.resolve())

    # write the visualization file (vtkjs)
    viz_file = simulation_folder.joinpath('model.vtkjs')

    # load model and results and save them as a vtkjs file
    hb_model = HBModel.from_dict(model_dict)
    if not viz_file.is_file():
        model = VTKModel(hb_model, SensorGridOptions.Mesh)
        model.to_vtkjs(
            folder=viz_file.parent, config=cfg_file,
            model_display_mode=DisplayMode.Wireframe
        )
    
    return viz_file

def run_res_viewer():
    if st.session_state.viz_file.is_file():
        st_vtkjs(content=st.session_state.viz_file.read_bytes(),
            key='vtk-viewer', subscribe=False)