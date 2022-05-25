from typing import Dict, List
import pathlib
import json
from ladybug.color import Colorset, ColorRange, Color


def create_analytical_mesh(
        results_folder: str, 
        model: Dict
    ):
    # get grid info
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
