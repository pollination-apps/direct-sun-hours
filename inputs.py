
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

def initialize():
    """ Initialize any of the session state variables if they don't already exist. """
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())[:8]
    if 'target_folder' not in st.session_state:
        st.session_state.target_folder = Path('/home/ladybugbot/app').resolve()
    if 'valid_report' not in st.session_state:
        st.session_state.valid_report = None
    # sim session
    if 'query' not in st.session_state:
        st.session_state.query = None
    if 'sim_client' not in st.session_state:
        st.session_state.sim_client = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'wea_path' not in st.session_state:
        st.session_state.wea_path = None
    if 'hbjson_path' not in st.session_state:
        st.session_state.hbjson_path = None
    if 'vtk_path' not in st.session_state:
        st.session_state.vtk_path = None
    if 'hb_model' not in st.session_state:
        st.session_state.hb_model = None
    # results session
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
        directory = os.path.join(
            st.session_state.target_folder.as_posix(),
            'data', st.session_state.user_id
        )
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


def get_model_inputs(host: str, container):
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


