from typing import List, Optional
import json

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.facetype import Floor, Wall
    from honeybee.typing import clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

def create_room_grids(rooms: List[Room],
    grid_size: Optional[float]=1,
    dist_floor: Optional[float]=0.8,
    remove_out: Optional[bool]=True,
    wall_offset: Optional[float]=0.0):
    # TODO: add advanced quad only
    x_axis = None

    # create lists to be filled with content
    grid = []
    clean_rooms = []
    for obj in rooms:
        if isinstance(obj, Model):
            clean_rooms.extend(obj.rooms)
        elif isinstance(obj, Room):
            clean_rooms.append(obj)
        else:
            raise TypeError('Expected Honeybee Room or Model. Got {}.'.format(type(obj)))

    for room in clean_rooms:
        # get all of the floor faces of the room as Breps
        lb_floors = [face.geometry.flip() for face in room.faces if isinstance(face.type, Floor)]

        if len(lb_floors) != 0:
            # create the gridded ladybug Mesh3D
            # if quad_only:  # use Ladybug's built-in meshing methods
            if x_axis:
                lb_floors = [Face3D(f.boundary, Plane(f.normal, f[0], x_axis), f.holes)
                              for f in lb_floors]
            lb_meshes = []

            # TODO: generate a log file for mesh grids errors
            for geo in lb_floors:
                try:
                    lb_meshes.append(geo.mesh_grid(grid_size, 
                        offset=dist_floor))
                except AssertionError as e:
                    print(e)
                    continue
            
            lb_mesh = lb_meshes[0] if len(lb_meshes) == 1 else Mesh3D.join_meshes(lb_meshes)

            # remove points outside of the room volume if requested
            if remove_out:
                pattern = [room.geometry.is_point_inside(pt)
                           for pt in lb_mesh.face_centroids]
                try:
                    lb_mesh, vertex_pattern = lb_mesh.remove_faces(pattern)
                except AssertionError:  # the grid lies completely outside of the room
                    lb_mesh = None

            # remove any sensors within a certain distance of the walls, if requested
            if wall_offset and lb_mesh is not None:
                wall_geos = [f.geometry for f in room.faces if isinstance(f.type, Wall)]
                pattern = []
                for pt in lb_mesh.face_centroids:
                    for wg in wall_geos:
                        if wg.plane.distance_to_point(pt) <= wall_offset:
                            pattern.append(False)
                            break
                    else:
                        pattern.append(True)
                try:
                    lb_mesh, vertex_pattern = lb_mesh.remove_faces(pattern)
                except AssertionError:  # the grid lies completely outside of the room
                    lb_mesh = None

            if lb_mesh is not None:
                # extract positions and directions from the mesh
                base_poss = [(pt.x, pt.y, pt.z) for pt in lb_mesh.face_centroids]
                base_dirs = [(vec.x, vec.y, vec.z) for vec in lb_mesh.face_normals]

                # create the sensor grid
                s_grid = SensorGrid.from_position_and_direction(
                    clean_rad_string(room.display_name), base_poss, base_dirs)
                s_grid.display_name = room.display_name
                s_grid.room_identifier = room.identifier
                s_grid.mesh = lb_mesh
                s_grid.base_geometry = \
                    tuple(f.move(f.normal * dist_floor) for f in lb_floors)

                # append everything to the lists
                grid.append(s_grid)
    
    return grid


# TODO: delete it after fix
def from_face3d(identifier, faces, x_dim, y_dim=None, offset=0, flip=False):
    meshes = []
    for face in faces:
        try:
            f = face.mesh_grid(x_dim, y_dim, offset, flip)
            meshes.append(f)
        except Exception as e:
            continue
    
    if len(meshes) == 1:
        s_grid = SensorGrid.from_mesh3d(identifier, meshes[0])
    elif len(meshes) > 1:
        s_grid = SensorGrid.from_mesh3d(identifier, Mesh3D.join_meshes(meshes))
    s_grid.base_geometry = faces
    return s_grid

def create_grid_from_faces(
    faces,
    grid_size: float,
    offset: float
    ):
    error_msg = None
    try:
        faces = [Face3D.from_dict(g) for g in faces]
        
        grids = from_face3d(
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