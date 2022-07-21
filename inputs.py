
""" A module for inputs. """

from pathlib import Path
import os
import uuid
import streamlit as st
from query import Query
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit_io import get_hbjson
from honeybee.model import Model
from honeybee_vtk.model import Model as VTKModel
from pollination_streamlit_viewer import viewer
from ladybug.wea import Wea
from ladybug.analysisperiod import AnalysisPeriod
from simulation import run_local_study

def initialize():
    """ Initialize any of the session state variables if they don't already exist. """
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())[:8]
    if 'target_folder' not in st.session_state:
        st.session_state.target_folder = Path(__file__).parent.joinpath(
            'data', f'{st.session_state.user_id}').resolve()
    if 'valid_report' not in st.session_state:
        st.session_state.valid_report = None
    # sim session
    if 'query' not in st.session_state:
        st.session_state.query = None
    if 'sim_client' not in st.session_state:
        st.session_state.sim_client = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'epw_path' not in st.session_state:
        st.session_state.epw_path = None
    if 'wea_path' not in st.session_state:
        st.session_state.wea_path = None
    if 'hbjson_path' not in st.session_state:
        st.session_state.hbjson_path = None
    if 'vtk_path' not in st.session_state:
        st.session_state.vtk_path = None
    if 'hb_model' not in st.session_state:
        st.session_state.hb_model = None
    # analysis period
    if 'start_hour' not in st.session_state:
        st.session_state.start_hour = None
    if 'start_day' not in st.session_state:
        st.session_state.start_day = None
    if 'start_month' not in st.session_state:
        st.session_state.start_month = None
    if 'end_hour' not in st.session_state:
        st.session_state.end_hour = None
    if 'end_day' not in st.session_state:
        st.session_state.end_day = None
    if 'end_month' not in st.session_state:
        st.session_state.end_month = None
    # results session
    if 'vtk_result_path' not in st.session_state:
        st.session_state.vtk_result_path = None
    if 'result_json' not in st.session_state:
        st.session_state.result_json = None


def set_api_client(host: str,
    api_key: str,
    owner: str,
    project: str) -> ApiClient:
    """ Set API client for simulations """
    # TODO: replace components with auth pollination-streamlit-io

    # create a query
    query = Query(host)
    query.owner = owner
    query.project = project

    api_client = ApiClient(api_token=api_key)

    # add to session state
    st.session_state.sim_client = api_client
    st.session_state.query = query
    st.session_state.api_key = api_key
    st.session_state.owner = query.owner
    st.session_state.project = query.project


def new_model():
    """Process a newly-uploaded Honeybee Model file."""
    # reset the simulation results and get the file data
    st.session_state.vtk_path = None
    st.session_state.valid_report = None

    st.session_state.result_json = None
    st.session_state.vtk_result_path = None
    # load the model object from the file data
    if 'hbjson' in st.session_state['hbjson_data']:
        hbjson_data = st.session_state['hbjson_data']['hbjson']
        st.session_state.hb_model = Model.from_dict(hbjson_data)


def get_model(column):
    """Get the Model input from the App input."""
    # load the model object from the file data
    with column:
        hbjson_data = get_hbjson(key='hbjson_data', on_change=new_model)
    if st.session_state.hb_model is None and hbjson_data is not None \
            and 'hbjson' in hbjson_data:
        st.session_state.hb_model = Model.from_dict(hbjson_data['hbjson'])


def generate_vtk_model(hb_model: Model, container):
    """Generate a VTK preview of an input model."""
    if not st.session_state.vtk_path:
        directory = st.session_state.target_folder
        if not os.path.isdir(directory):
            os.makedirs(directory)
        hbjson_path = hb_model.to_hbjson(hb_model.identifier, directory)
        vtk_model = VTKModel.from_hbjson(hbjson_path)
        vtk_path = vtk_model.to_vtkjs(folder=directory, name=hb_model.identifier)
        st.session_state.vtk_path = vtk_path
    vtk_path = st.session_state.vtk_path
    with container:
        viewer(content=Path(vtk_path).read_bytes(), key='vtk_preview_model')


def generate_model_validation(hb_model: Model, container):
    """Generate a Model validation report from an input model."""
    if not st.session_state.valid_report:
        report = hb_model.check_all(raise_exception=False, detailed=False)
        st.session_state.valid_report = report
    report = st.session_state.valid_report
    if report == '':
        container.success('Congratulations! Your Model is valid!')
    else:
        container.warning('Your Model is invalid for the following reasons:')
        container.code(report, language='console')


def new_weather_file():
    """Process a newly-uploaded EPW file."""
    # reset the simulation results and get the file data
    st.session_state.result_json = None
    st.session_state.vtk_result_path = None

    # from key name
    epw_file = st.session_state.epw_data
    if epw_file:
        # save EPW in data folder
        epw_path = st.session_state.target_folder.joinpath(f'{epw_file.name}')
        epw_path.parent.mkdir(parents=True, exist_ok=True)
        epw_path.write_bytes(epw_file.read())
        # create a WEA file from the EPW
        period = AnalysisPeriod(
            st_month=st.session_state.start_month or 1,
            st_day=st.session_state.start_day or 1, 
            st_hour=st.session_state.start_hour or 0, 
            end_hour=st.session_state.end_hour or 23,
            end_day=st.session_state.end_day or 31, 
            end_month=st.session_state.end_month or 12)
        wea_file = epw_path.as_posix().replace('.epw', '.wea')
        wea = Wea.from_epw_file(epw_file=epw_path)
        wea = wea.filter_by_hoys(period.hoys)
        wea.write(wea_file)
        wea_path = Path(wea_file)
        
        # set the session state variables
        st.session_state.wea_path = wea_path
        st.session_state.epw_path = epw_path
    else:
        st.session_state.epw_path = None


def update_wea(
    start_hour: int = None,
    start_day: int = None,
    start_month: int = None,
    end_hour: int = None,
    end_day: int = None,
    end_month: int= None):
    period = AnalysisPeriod(
        st_month=start_month or st.session_state.start_month,
        st_day=start_day or st.session_state.start_day, 
        st_hour=start_hour or st.session_state.start_hour, 
        end_hour=end_hour or st.session_state.end_hour,
        end_day=end_day or st.session_state.end_day, 
        end_month=end_month or st.session_state.end_month)

    # read from file
    st.session_state.wea_path = None
    if st.session_state.epw_path:
        # create a WEA file from the EPW
        wea_file = st.session_state.epw_path.as_posix().replace('.epw', '.wea')
        wea = Wea.from_epw_file(epw_file=st.session_state.epw_path)
        wea = wea.filter_by_hoys(period.hoys)
        wea.write(wea_file)
        wea_path = Path(wea_file)
        
        # save wea
        st.session_state.wea_path = wea_path


def is_api_client_valid():
    return st.session_state.sim_client and \
    st.session_state.query and \
    st.session_state.api_key and \
    st.session_state.owner and \
    st.session_state.project

def get_weather_file(column):
    """Get the EPW weather file from the App input."""
    # upload weather file
    column.file_uploader(
        'Weather file (EPW)', type=['epw'],
        on_change=new_weather_file, key='epw_data',
        help='Select an EPW weather file to be used in the simulation.'
    )


def get_api_inputs(host: str, container):
    """ API Client user inputs """
    with container:
        api_key = st.sidebar.text_input(
            'Enter Pollination APIKEY', type='password',
            help=':bulb: You only need an API Key to access private projects. '
            'If you do not have a key already go to the settings tab under your profile to '
            'generate one.'
        )
        owner_name = st.sidebar.text_input('Project Owner')
        project_name = st.sidebar.text_input('Project Name')

        set_api_client(host=host, 
            api_key=api_key,
            owner=owner_name,
            project=project_name)


def get_inputs(host: str, container):
    """Get Model user inputs."""
    # get the input model
    m_col_1, m_col_2 = container.columns([2, 1])
    get_model(m_col_1)
    # add options to preview the model in 3D and validate it
    if st.session_state.hb_model:
        if m_col_2.checkbox(label='Preview Model', value=False):
            generate_vtk_model(st.session_state.hb_model, container)
        if m_col_2.checkbox(label='Validate Model', value=False):
            generate_model_validation(st.session_state.hb_model, container)

    # get the input EPW and WEA files
    w_col_1, = container.columns([1])
    get_weather_file(w_col_1)

    with container.form(key='Analysis Period'):
        c1, c2 = st.columns([1, 1])
        with c1:
            start_hour = st.number_input(
                label='Start hour', min_value=0, max_value=23, value=0, step=1)
            if start_hour != st.session_state.start_hour:
                st.session_state.start_hour = start_hour
            start_day = st.number_input(
                label='Start day', min_value=1, max_value=31, value=1, step=1)
            if start_day != st.session_state.start_day:
                st.session_state.start_day = start_day
            start_month = st.number_input(
                label='Start month', min_value=1, max_value=12, value=1, step=1)
            if start_month != st.session_state.start_month:
                st.session_state.start_month = start_month  
        with c2:
            end_hour = st.number_input(
                label='End hour', min_value=0, max_value=23, value=23, step=1)
            if end_hour != st.session_state.end_hour:
                st.session_state.end_hour = end_hour
            end_day = st.number_input(
                label='End day', min_value=1, max_value=31, value=31, step=1)
            if end_day != st.session_state.end_day:
                st.session_state.end_day = end_day
            end_month = st.number_input(
                label='End month', min_value=1, max_value=12, value=12, step=1)
            if end_month != st.session_state.end_month:
                st.session_state.end_month = end_month
            is_cloud = st.checkbox(label='On Cloud', value=False)
        submit = st.form_submit_button(label='Run Study')
        if submit:
            update_wea(start_hour, start_day, start_month, end_hour,
                end_day, end_month)
            if is_cloud:
                if not is_api_client_valid():
                    st.warning('Please, check API data on the sidebar.')
                    return
                else:
                    pass
            else:
                status, error = run_local_study(st.session_state.target_folder,
                    st.session_state.hb_model,
                    st.session_state.wea_path)
                if status:
                    st.success('Done!')
                else:
                    st.warning(error)
