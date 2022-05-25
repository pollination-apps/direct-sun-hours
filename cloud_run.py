from enum import Enum
import json
from viz import get_vtk_config
import zipfile
import pathlib
from query import Query
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import Job, NewJob, Recipe
from queenbee.job.job import JobStatusEnum
from honeybee_vtk.model import ( HBModel, 
    Model as VTKModel, 
    SensorGridOptions, 
    DisplayMode )

class SimStatus(Enum):
  KO=0
  COMPLETE=1
  INCOPLETE=2

def run_cloud_simulation(query: Query, 
    api_client: ApiClient, 
    model_path: pathlib.Path, 
    wea_path: pathlib.Path):
    query.job_id = None
    # remember to add direct-sun-hours to your cloud project
    recipe = Recipe('ladybug-tools', 'direct-sun-hours',
                    '0.5.4', api_client)
    
    new_job = NewJob(query.owner, 
        query.project, 
        recipe, 
        client=api_client)

    model_project_path = new_job.upload_artifact(
        model_path, 'streamlit-job')

    wea_project_path = new_job.upload_artifact(
        wea_path, 'streamlit-job')

    q = {
        'model': model_project_path,
        'wea': wea_project_path
    }
    
    new_job.arguments = [q]
    job = new_job.create()

    query.job_id = job.id

    return job.id
  
def request_results(query: Query,
    api_client: ApiClient):
    job = Job(query.owner, 
      query.project, 
      query.job_id, 
      client=api_client)

    url = f'https://app.pollination.cloud/projects/{query.owner}/{query.project}/jobs/{query.job_id}'

    if job.status.status in [
            JobStatusEnum.pre_processing,
            JobStatusEnum.running,
            JobStatusEnum.created,
            JobStatusEnum.unknown]:
        return SimStatus.INCOPLETE, url
    elif job.status.status in [JobStatusEnum.failed, JobStatusEnum.cancelled]:
        return SimStatus.KO, url
    else:
        return SimStatus.COMPLETE, url


def post_process_cloud(
    query: Query,
    api_client: ApiClient,
    here: pathlib.Path):
    owner = query.owner
    project = query.project
    job_id = query.job_id

    data_folder = here.joinpath('data')
    data_folder.mkdir(exist_ok=True)

    job = Job(owner, project, job_id, api_client)

    run = job.runs[0]
    input_model_path = job.runs_dataframe.dataframe['model'][0]

    output_folder = pathlib.Path(data_folder, run.id)
    res_folder = output_folder.joinpath('results')
    res_folder.mkdir(parents=True, exist_ok=True)
    
    # download results
    res_zip = run.download_zipped_output('cumulative-sun-hours')
    with zipfile.ZipFile(res_zip) as zip_folder:
        zip_folder.extractall(res_folder.as_posix())

    model_dict = json.load(job.download_artifact(input_model_path))

    # load the configuration file
    cfg_file = get_vtk_config(res_folder.as_posix(), 
        output_folder.resolve())

    # write the visualization file (vtkjs)
    viz_file = output_folder.joinpath('model.vtkjs')

    # load model and results and save them as a vtkjs file
    hb_model = HBModel.from_dict(model_dict)

    model = VTKModel(hb_model, SensorGridOptions.Sensors)
    model.to_vtkjs(folder=viz_file.parent, config=cfg_file,
                    display_mode=DisplayMode.Wireframe)
    
    return viz_file, res_folder.as_posix(), model_dict