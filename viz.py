import json
import pathlib

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

    config_file = folder.parent.joinpath('config.json')
    config_file.write_text(json.dumps(cfg))

    return config_file.as_posix()
