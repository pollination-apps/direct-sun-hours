"""A module to collect helper functions."""

import streamlit as st
from typing import Dict
from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_display.visualization import (
    VisualizationSet, 
    AnalysisGeometry,
    VisualizationData)
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug.color import Colorset
from ladybug.legend import Legend, LegendParameters
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
    """ Generate VisualizationSet from results """
    info_file = pathlib.Path(results_folder, 'grids_info.json')
    info = json.loads(info_file.read_text())
    grids = model['properties']['radiance']['sensor_grids']

    geometries = []
    merged_values = []
    for i, grid in enumerate(info):
        result_file = pathlib.Path(results_folder, f"{grid['full_id']}.res")
        values = [float(v) for v in result_file.read_text().splitlines()]
        merged_values += values
        mesh = Mesh3D.from_dict(grids[i]['mesh'])
        geometries.append(mesh)

    unit = 'hours'
    color_set = Colorset.original()
    l_par = LegendParameters(
        min=min(merged_values), max=max(merged_values), 
        title=unit, segment_count=11,
        base_plane=Plane(o=Point3D(20, 80, 0)))
    l_par.decimal_count = 1
    l_par.colors = color_set
    l_par.text_height = 16

    data_set = VisualizationData(values=merged_values, 
        legend_parameters=l_par)
    analysis_geo = AnalysisGeometry(identifier='analysis-id',
        geometry=geometries, 
        data_sets=[data_set])
    res = VisualizationSet(identifier='vis-id',
        geometry=[analysis_geo])
    return res.to_dict()


def local_css(file_name):
    """Load local css file."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)