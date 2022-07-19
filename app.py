"""Direct sun hour app."""
# generic
import streamlit as st
import extra_streamlit_components as stx
from helper import local_css
# steps
from handlers import bootstrap
from introduction import login
from input_process import get_inputs, run_cloud_simulation, run_local_simulation
from post_process import read, show_result
# integration
from pollination_streamlit_io import get_host


st.set_page_config(
    page_title='Direct Sun Hours',
    page_icon='https://app.pollination.cloud/favicon.ico',
    initial_sidebar_state='collapsed',
)  # type: ignore


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
        'Do you want to use Pollination Cloud?',
        ('Yes', 'No',))

    st.write('You selected:', option)
    if option == 'Yes':
        layout_server_run(host, target_folder)    
    else:
        layout_local_run(host, target_folder)    


def layout_server_run(host, target_folder):
    step = stx.stepper_bar(
        steps=["Login", "Run simulation", "Read results"])

    if step == 0:
        login(host=host)
    if step == 1:
        get_inputs(host=host,
                   target_folder=target_folder)
        run_cloud_simulation()
    elif step == 2:
        read(host=host,
             target_folder=target_folder)


def layout_local_run(host, target_folder):
    step = stx.stepper_bar(
        steps=["Run simulation", "Read results"])

    if step == 0:
        get_inputs(host=host,
                   target_folder=target_folder)
        run_local_simulation(target_folder=target_folder)
    elif step == 1:
        show_result(host=host)

if __name__ == '__main__':
    main()
