import json
import pathlib
import streamlit as st
from ladybug.wea import Wea
from lbt_recipes.recipe import Recipe
from ladybug.color import Color
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug.analysisperiod import AnalysisPeriod
from honeybee.model import Model
from streamlit_vtkjs import st_vtkjs
from pollination_streamlit_io import (button,
                                      special, inputs)
from read_results import create_analytical_mesh
from local_run import (run_simulation,
                       post_process)
from cloud_run import (run_cloud_simulation,
                       request_results, SimStatus, post_process_cloud)
from honeybee_vtk.model import Model as VTKModel
from honeybee_vtk.vtkjs.schema import SensorGridOptions

from query import Query
from pollination_streamlit.api.client import ApiClient
from create_grids import create_grid_from_faces


def hash_fnc_ladybug(_): return _.to_dict()


@st.cache(hash_funcs={Color: hash_fnc_ladybug,
                      Model: hash_fnc_ladybug, Wea: hash_fnc_ladybug})
def run_calculation(recipe: Recipe,
                    here: pathlib.Path,
                    hb_model: Model):
    project_folder = run_simulation(recipe, here)
    viz_file, results_path = post_process(hb_model,
                                          here,
                                          project_folder)

    result_json = create_analytical_mesh(
        results_folder=results_path,
        model=hb_model.to_dict())

    return viz_file, result_json


# settings type
CALCULATION_MODE = {
    'cloud': 'Cloud calculation',
    'local': 'Local calculation',
}

st.set_page_config(
    page_title='Direct Sun Hours App',
    layout='wide',
    page_icon='https://app.pollination.cloud/favicon.ico'
)

# branding, api-key and url
# we should wrap this up as part of the pollination-streamlit library
st.sidebar.image(
    'https://uploads-ssl.webflow.com/6035339e9bb6445b8e5f77d7/616da00b76225ec0e4d975ba_pollination_brandmark-p-500.png',
    use_column_width=True
)

# shared var
if 'result_json' not in st.session_state:
    st.session_state.result_json = {}
if 'viz_file' not in st.session_state:
    st.session_state.viz_file = None
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

# sidebar start
st.sidebar.header(
    'Welcome to pollination direct sun hours app!' +
    '\n1. 💻 Select calculation mode'
    '\n2. 🏡 Upload model'
    '\n3. ⛅ Upload EPW file'
    '\n4. 🕒 Change analysis period'
    '\n5. 🔧 Change settings'
    '\n6. ✅ Run it'
)
st.sidebar.markdown('---')

# rhino integration!
st_query = st.experimental_get_query_params()
platform = special.get_host()
st.write(platform)

# select calc mode
st.session_state.calculation_mode = st.sidebar.selectbox(
    label='Calculation mode',
    options=CALCULATION_MODE.values())

# if cloud mode
query = api_client = None
if st.session_state.calculation_mode == CALCULATION_MODE['cloud']:
    st.session_state.api_key = st.sidebar.text_input(
        'Enter Pollination APIKEY', type='password',
        help=':bulb: You only need an API Key to access private projects. '
        'If you do not have a key already go to the settings tab under your profile to '
        'generate one.'
    ) or None

    # create a query
    query = Query(platform)
    query.owner = st.sidebar.text_input(
        'Project Owner', value=query.owner
    )

    query.project = st.sidebar.text_input(
        'Project Name', value=query.project
    )
    api_client = ApiClient(api_token=st.session_state.api_key)
else:
    pass

# get the current folder
here = pathlib.Path(__file__).parent
hb_model = vtk_path = hbjson_path = None

# inputs
with st.sidebar.container():
    if platform is None:
        hbjson_file = st.file_uploader(
            'Upload a hbjson file',
            type=['hbjson', 'json']
        )
        if hbjson_file:
            # save HBJSON in data folder
            hbjson_path = pathlib.Path(f'./{here}/data/{hbjson_file.name}')
            hbjson_path.parent.mkdir(parents=True, exist_ok=True)
            data = hbjson_file.read()
            hbjson_path.write_bytes(data)
            model_data = json.loads(data)
            hb_model = Model.from_dict(model_data)
    elif platform == 'rhino':
        token = special.sync(key='pollination-sync',
                             delay=50)
        data = button.get(is_pollination_model=True,
                          sync_token=token,
                          key='pollination-model')
        if data:
            model_data = data
            hb_model = Model.from_dict(model_data)
            hbjson_path = pathlib.Path(f'./{here}/data/{hb_model.identifier}.hbjson')
            hbjson_path.parent.mkdir(parents=True, exist_ok=True)
            hbjson_path.write_text(json.dumps(hb_model.to_dict()))
    elif platform == 'sketchup':
        st.warning('Sketchup does not support sync for now...')
        data = button.get(is_pollination_model=True,
                          key='pollination-model',
                          platform='sketchup')

        if data:
            # create grids
            with st.container():
                grid_size = st.number_input(
                    label='Grid size(m)',
                    min_value=0.1,
                    max_value=5.0,
                    value=0.6096)
                grid_height = st.number_input(
                    label='Workplane height(m)',
                    min_value=0.1,
                    max_value=5.0,
                    value=0.762)
            # honeybee openstudio does not expose grids :(
            st.write('Select a skp group to generate sensor grids.')
            faces = button.get(
                key='faces-for-sensors',
                button_text='Create SensorGrid',
                platform='sketchup')
            if faces:
                grids, error_msg = create_grid_from_faces(faces,
                                                          grid_size=grid_size, offset=grid_height)
                model_data = data
                hb_model = Model.from_dict(model_data)

                hb_model = hb_model.duplicate()
                # grids = create_room_grids(hb_model.rooms,
                # grid_size=grid_size, dist_floor=grid_height)
                if grids:
                    hb_model.properties.radiance.add_sensor_grids([grids])
                else:
                    st.warning('Unable to create sensor grids... '
                               'use a skp group made by planar faces.'
                               ' {}'.format('ERROR: ' + str(error_msg)))

                hbjson_path = pathlib.Path(f'./{here}/data/{hb_model.identifier}.hbjson')
                hbjson_path.parent.mkdir(parents=True, exist_ok=True)
                hbjson_path.write_text(json.dumps(hb_model.to_dict()))

    # model preview
    if hbjson_path:
        vtk_path = VTKModel.from_hbjson(hbjson_path.as_posix(),
                                        SensorGridOptions.Sensors).to_vtkjs(
            folder=hbjson_path.parent, name=hb_model.identifier)

# TODO: use state variable
if vtk_path:
    st_vtkjs(
        content=pathlib.Path(vtk_path).read_bytes(),
        key='vtk_preview_model'
    )

# upload weather file
epw_file = st.sidebar.file_uploader(
    'Upload a weather file (EPW)',
    type=['epw']
)

wea = wea_path = None
if epw_file:
    # save EPW in data folder
    epw_path = pathlib.Path(f'./{here}/data/{epw_file.name}')
    epw_path.parent.mkdir(parents=True, exist_ok=True)
    epw_path.write_bytes(epw_file.read())

    wea = Wea.from_epw_file(epw_file=epw_path)

    with st.sidebar.expander(label='Analysis Period', expanded=False):
        start_hour = st.slider(label='Start hour', min_value=0, max_value=23, value=9)
        start_day = st.slider(label='Start day', min_value=1, max_value=31, value=21)
        start_month = st.slider(label='Start month', min_value=1, max_value=12, value=6)
        end_hour = st.slider(label='End hour', min_value=0, max_value=23, value=15)
        end_day = st.slider(label='End day', min_value=1, max_value=31, value=21)
        end_month = st.slider(label='End month', min_value=1, max_value=12, value=6)

        period = AnalysisPeriod(st_month=start_month,
                                st_day=start_day, st_hour=start_hour, end_hour=end_hour,
                                end_day=end_day, end_month=end_month)

        if period:
            wea = wea.filter_by_hoys(period.hoys)

        # save wea
        wea_path = epw_path.as_posix()
        wea_path = wea_path.replace('.epw', '.wea')

        wea.write(wea_path)
        wea_path = pathlib.Path(wea_path)

# settings
submitted = False
with st.sidebar.expander(label='Recipe settings', expanded=False):
    timestep = st.number_input(label='Timestep',
                               min_value=1,
                               max_value=60,
                               value=1)

    north = st.slider(label='North',
                      min_value=0,
                      max_value=360,
                      value=0)

    cpu_count = st.number_input(label='CPU count',
                                min_value=1,
                                max_value=96,
                                value=4)

    min_sensor_count = st.number_input(label='Min. sensor count',
                                       min_value=50,
                                       max_value=5000,
                                       value=100)

    grid_filter = st.text_input(label='Grid filter',
                                value='*')

UPPER = st.number_input(label='Lower limit', value=0)
LOWER = st.number_input(label='Upper limit', value=6)

# run simulation button
submitted = st.sidebar.button('Run Simulation')

if submitted:
    # create the recipe and set the input arguments
    recipe = Recipe('direct-sun-hours')
    recipe.input_value_by_name('model', hb_model)
    recipe.input_value_by_name('timestep', timestep)
    recipe.input_value_by_name('north', north)
    recipe.input_value_by_name('cpu-count', cpu_count)
    recipe.input_value_by_name('min-sensor-count', min_sensor_count)
    recipe.input_value_by_name('wea', wea)
    recipe.input_value_by_name('grid-filter', grid_filter)

# calculation

if hb_model and submitted:
    # TODO: add cloud run
    if st.session_state.calculation_mode == CALCULATION_MODE['local']:
        st.session_state.viz_file, st.session_state.result_json = run_calculation(recipe,
                                                                                  here,
                                                                                  hb_model)
    else:
        st.session_state.job_id = run_cloud_simulation(query=query,
                                                       api_client=api_client, model_path=hbjson_path,
                                                       wea_path=wea_path)

if st.session_state.calculation_mode == CALCULATION_MODE['cloud'] and \
        st.session_state.job_id:
    clicked = st.button(label='Refresh to get results')
    if clicked:
        status, url = request_results(query=query,
                                      api_client=api_client)

        msg = f'{status.name}, check your job [here]({url})'
        if status.name == "COMPLETE":
            st.success(msg)
        else:
            st.warning(msg)

        if status == SimStatus.COMPLETE:
            viz_file, results_path, model_dict = post_process_cloud(
                query=query,
                api_client=api_client,
                here=here)

            st.session_state.viz_file = viz_file

            st.session_state.result_json = create_analytical_mesh(
                results_folder=results_path,
                model=hb_model.to_dict())
    # else:
    #     st.session_state.viz_file = None
    #     st.session_state.result_json = {}

# outputs
if platform == 'rhino':
    # display grids
    inputs.send(
        data=st.session_state.result_json,
        default_checked=True,
        label='Show Grids!',
        unique_id='unique-id-02',
        options={'layer': 'daylight_factor_results'},
        delay=1000,
        key='pollination-inputs-send-02'
    )

    button.send(action='BakeGeometry',
                data=st.session_state.result_json,
                unique_id='bake-grids',
                key='bake-grids')
elif platform == 'sketchup':
    button.send(action='DrawGeometry',
                data=st.session_state.result_json,
                unique_id='bake-grids-skp',
                key='bake-grids-skp',
                platform=platform)

# if visualization file exists show the viewer
if st.session_state.viz_file:
    if st.session_state.viz_file.is_file():
        st_vtkjs(content=st.session_state.viz_file.read_bytes(),
                 key='vtk-viewer')
