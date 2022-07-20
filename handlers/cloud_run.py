""" A module to run cloud calculation. """

from enum import Enum
import json
from handlers.shared import get_vtk_model_result
import zipfile
import pathlib
from .query import Query
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import Job, NewJob, Recipe


class SimStatus(Enum):
    KO = 0
    COMPLETE = 1
    INCOPLETE = 2


def run_cloud_simulation(query: Query,
                         api_client: ApiClient,
                         model_path: pathlib.Path,
                         wea_path: pathlib.Path):
    query.job_id = None
    # remember to add direct-sun-hours to your cloud project
    recipe = Recipe('ladybug-tools', 'direct-sun-hours',
                    '0.5.5-viz', api_client)

    new_job = NewJob(query.owner,
                     query.project,
                     recipe,
                     client=api_client)

    model_project_path = new_job.upload_artifact(model_path)

    wea_project_path = new_job.upload_artifact(wea_path)

    q = {
        'model': model_project_path,
        'wea': wea_project_path
    }

    new_job.arguments = [q]
    job = new_job.create()

    query.job_id = job.id

    return job.id


def post_process_job(job: Job, here: str):
    data_folder = pathlib.Path(here).joinpath('data')
    data_folder.mkdir(exist_ok=True)

    run = job.runs[0]
    input_model_path = job.runs_dataframe.dataframe['model'][0]

    simulation_folder = pathlib.Path(data_folder, run.id)
    res_folder = simulation_folder.joinpath('results')
    res_folder.mkdir(parents=True, exist_ok=True)

    # download results
    res_zip = run.download_zipped_output('cumulative-sun-hours')
    with zipfile.ZipFile(res_zip) as zip_folder:
        zip_folder.extractall(res_folder.as_posix())

    model_dict = json.load(job.download_artifact(input_model_path))

    viz_file = get_vtk_model_result(model_dict,
        simulation_folder,
        simulation_folder.joinpath('results'))

    return viz_file, res_folder.as_posix(), model_dict, simulation_folder
