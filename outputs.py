""" A module for outpus. """

import streamlit as st
import json
import pathlib
from honeybee.model import Model
from honeybee_vtk.model import Model as VTKModel
from honeybee_vtk.vtkjs.schema import SensorGridOptions
from honeybee_vtk.model import (HBModel,
                                Model as VTKModel,
                                SensorGridOptions,
                                DisplayMode)
from pollination_streamlit_viewer import viewer
from pollination_streamlit.interactors import Job

def get_vtk_config(folder: pathlib.Path,
    values_path: pathlib.Path) -> str:
    '''Write Direct Sun Hours config to a folder.'''

    cfg = {
        "data": [
            {
                "identifier": "Direct Sun Hours",
                "object_type": "grid",
                "unit": "Hour",
                "path": values_path.as_posix(),
                "hide": False,
                "legend_parameters": {
                    "hide_legend": False,
                    "min": 0,
                    "max": 5,
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

    config_file = folder.joinpath('config.json')
    config_file.write_text(json.dumps(cfg))

    return config_file.as_posix()


def get_vtk_model_result(model_dict: dict, 
    simulation_folder: pathlib.Path,
    values_path: pathlib.Path,
    container):
    # load the configuration file
    cfg_file = get_vtk_config(
        folder=simulation_folder.resolve(),
        values_path=values_path)

    # load model and results and save them as a vtkjs file
    hb_model = HBModel.from_dict(model_dict)
    if not st.session_state.vtk_result_path:
        vtk_model = VTKModel.from_hbjson(hb_model, SensorGridOptions.Mesh)
        vtk_result_path = vtk_model.to_vtkjs(folder=st.session_state.target_folder,
            config=cfg_file,
            model_display_mode=DisplayMode.Wireframe,
            name=hb_model.identifier + 'res')
        st.session_state.vtk_result_path = vtk_result_path
    vtk_result_path = st.session_state.vtk_result_path

    with container:
        viewer(content=pathlib.Path(vtk_result_path).read_bytes(), 
        key='vtk_res_model')


    # viz_file = get_vtk_model_result(model_dict,
    #     simulation_folder,
    #     simulation_folder.joinpath('results'))

    # return viz_file, res_folder.as_posix(), model_dict, simulation_folder