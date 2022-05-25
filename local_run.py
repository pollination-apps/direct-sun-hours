import pathlib
from viz import get_vtk_config
from typing import ( Tuple, Optional )
from lbt_recipes.recipe import Recipe
from honeybee.model import Model
from honeybee_vtk.model import ( HBModel, 
    Model as VTKModel, 
    SensorGridOptions, 
    DisplayMode )

def run_simulation(
        recipe: Recipe,
        app_path: pathlib.Path) -> str:
    '''Run the recipe.'''

    simulation_path = pathlib.Path(f'./{app_path}/simulation')
    simulation_path.mkdir(parents=True, exist_ok=True)

    project_folder = recipe.run(f'--workers 16 --folder {simulation_path.as_posix()}',
        radiance_check=True)
    
    return project_folder

def post_process(
        hb_model: Model, 
        app_path: pathlib.Path,
        project_folder: str,
        results_folder_name: Optional[str] 
            = 'results') -> Tuple[pathlib.Path, str]:
    ''' Direct Sun Hours post-process. Write and get viz file and path '''

    # get the simulation folder
    output_folder = pathlib.Path(app_path, 
        project_folder, 
        'direct_sun_hours').resolve()
    # get the result folder
    results_path = output_folder.joinpath(results_folder_name, 'cumulative').as_posix()

    # load the configuration file
    cfg_file = get_vtk_config(results_path, output_folder)

    # write the visualization file (vtkjs)
    viz_file = output_folder.joinpath('model.vtkjs')
    # load model and results and save them as a vtkjs file
    hb_model = HBModel.from_dict(hb_model.to_dict())
    model = VTKModel(hb_model, SensorGridOptions.Sensors)
    model.to_vtkjs(folder=viz_file.parent, config=cfg_file,
                    model_display_mode=DisplayMode.Wireframe)
    
    return viz_file, results_path