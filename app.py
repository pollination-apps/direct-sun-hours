import streamlit as st
from inputs import initialize, get_api_inputs
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

def main(platform):
    """Perform sunlight hours simulations."""
    # title
    st.header('Sunlight hours')
    st.markdown("""---""")  # horizontal divider line between title and input

    # initialize the app and load up all of the inputs
    initialize()
    sidebar_container = st.container()  # container to hold the inputs
    get_api_inputs(platform, sidebar_container)


if __name__ == '__main__':
    platform = get_host() or 'web'
    main(platform)