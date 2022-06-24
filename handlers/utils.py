"""A module to collect utility functions."""
import json
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.mesh import Mesh3D
from honeybee_radiance.sensorgrid import SensorGrid

def create_grid_from_mesh(meshes):
    error_msg = None
    grids = []
    for i, m in enumerate(meshes):
        try:
            dictionary = json.loads(m)
            mesh = Mesh3D.from_dict(dictionary)
            grid = SensorGrid.from_mesh3d(
                f'skp-sensor-grid-{i}', mesh)
        except Exception as e:
            error_msg = e
            grid = None
        grids.append(grid)            
    
    return grids, error_msg

def create_grid_from_faces(
    faces,
    grid_size: float,
    offset: float
    ):
    error_msg = None
    try:
        faces = [Face3D.from_dict(g) for g in faces]
        
        grids = SensorGrid.from_face3d(
            identifier='skp-sensor-grid-xxxxxx', 
            faces=faces, 
            x_dim=grid_size, 
            y_dim=grid_size, 
            offset=offset, 
            flip=False)
    except Exception as e:
        error_msg = e
        grids = None
    
    return grids, error_msg