"""Direct sun hour app."""
# generic
import pathlib
import streamlit as st
import extra_streamlit_components as stx
from helper import local_css
# steps
from handlers import bootstrap
from introduction import login
from input_process import get_inputs, run_simulation
from post_process import read
# integration
from pollination_streamlit_io import special


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
    host = special.get_host() or 'web'

    # title
    st.title('Direct sun hour app ☀️')

    # navbar
    step = stx.stepper_bar(
        steps=["Login", "Run simulation", "Read results"])

    # common paths
    target_folder = pathlib.Path(__file__).parent

    # temp variable
    if step == 0:
        login(host=host)
    if step == 1:
        get_inputs(host=host,
            target_folder=target_folder)
        run_simulation()
    elif step == 2:       
        read(host=host, 
            target_folder=target_folder)

if __name__ == '__main__':
    main()