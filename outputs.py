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


def get_vtk_config(res_folder: pathlib.Path) -> str:
    '''Write Direct Sun Hours config to a folder.'''

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

    # load model and results and save them as a vtkjs file
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


