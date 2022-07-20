"""Direct sun hour app."""
# generic
import streamlit as st
from helper import local_css
# steps
from handlers import bootstrap
from introduction import login
from input_process import get_inputs, run_cloud_simulation, run_local_simulation
from post_process import read_from_cloud, read_from_local
# integration
from pollination_streamlit_io import get_host


st.set_page_config(
    page_title='Direct Sun Hours',
    page_icon='https://app.pollination.cloud/favicon.ico',
    initial_sidebar_state='collapsed',
)  # type: ignore
st.sidebar.image(
    'https://uploads-ssl.webflow.com/6035339e9bb6445b8e5f77d7/616da00b76225ec0e4d975ba'
    '_pollination_brandmark-p-500.png',
    use_column_width=True
)

LAYOUT_OPTIONS = {
    0: 'Create a new study',
    1: 'Visualize an existing study'
}

def main():
    # load local css
    local_css('style.css')

    # bootstrap session variables
    bootstrap.initialize()

    # find the host the app is being run inside
    host = get_host() or 'web'

    # title
    st.title('Direct sun hour app ☀️')

    # common paths
    target_folder = "/home/ladybugbot/app"

    # layout selection
    option = st.selectbox(
        'Hello👋! What do you want to do?',
        LAYOUT_OPTIONS.values())
    
    if option == LAYOUT_OPTIONS[0]:
        layout_selector(host=host, 
            target_folder=target_folder)
    else:
        read_from_cloud(host=host,
            target_folder=target_folder)

def layout_selector(host, 
    target_folder):
    run_mode = st.radio(
    "Run on cloud", ('Yes', 'No'))
    if run_mode == 'Yes':
        layout_server_run(host, target_folder)    
    else:
        layout_local_run(host, target_folder)

def layout_server_run(host, target_folder):
    # login part
    login(host=host)
    get_inputs(host=host,
                target_folder=target_folder)
    run_cloud_simulation()

def layout_local_run(host, target_folder):
    get_inputs(host=host,
                target_folder=target_folder)
    run_local_simulation(target_folder=target_folder)
    read_from_local(host=host)

if __name__ == '__main__':
    main()
