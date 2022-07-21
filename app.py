import streamlit as st
from inputs import initialize, get_api_inputs, get_inputs
from simulation import cloud_result_output
from pollination_streamlit_io import get_host 
from helper import local_css

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

def main(platform):
    """Perform sunlight hours simulations."""
    # load local css
    local_css('style.css')

    # title
    st.header('Sunlight hours')

    # initialize the app and load up all of the inputs
    initialize()

    # set tabs
    tab1, tab2 = st.tabs(["Run Study", "Read Result"])

    # sidebar
    with tab1:
        sidebar_container = st.container()
        get_api_inputs(platform, sidebar_container)

        # body
        in_container = st.container()
        get_inputs(platform, in_container)
    with tab2:
        cloud_result_output(platform)


if __name__ == '__main__':
    platform = get_host() or 'web'
    main(platform)