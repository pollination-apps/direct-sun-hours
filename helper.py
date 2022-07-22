"""A module to collect helper functions."""

import streamlit as st
from typing import Dict
import pathlib
import json

def read_results_from_folder(results_folder: str, 
    config_file: str, model: Dict):
    """ Get grid information - revit """
    info_file = pathlib.Path(results_folder, 'grids_info.json')
    grid_list = json.loads(info_file.read_text())

    config_file = pathlib.Path(config_file)
    config = json.loads(config_file.read_text())
    sensor_grids = model['properties']['radiance']['sensor_grids']
    
    results = {}
    for grid in grid_list:
        result_file = pathlib.Path(results_folder, f"{grid['full_id']}.res")
        values = [float(x) for x in result_file.read_text().splitlines()]
        results[grid['full_id']] = values
    
    return {
        "results": results,
        "sensorGrids": sensor_grids,
        "configs": config['data']
    }


def create_analytical_mesh(
        results_folder: str, 
        model: Dict
    ):
    """ Generate analysis grid - sketchup and rhino """
    info_file = pathlib.Path(results_folder, 'grids_info.json')
    info = json.loads(info_file.read_text())
    grids = model['properties']['radiance']['sensor_grids']

    geometries = []
    merged_values = []
    for i, grid in enumerate(info):
        result_file = pathlib.Path(results_folder, f"{grid['full_id']}.res")
        values = [float(v) for v in result_file.read_text().splitlines()]
        # clean dict
        mesh = json.dumps(grids[i]['mesh'])

        merged_values += values
        geometries.append(json.loads(mesh))

    analytical_mesh = {
        "type": "AnalyticalMesh",
        "mesh": geometries,
        "values": merged_values
    }
    return analytical_mesh


def local_css(file_name):
    """Load local css file."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)