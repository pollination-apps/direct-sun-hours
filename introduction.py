"""API cloud info."""

from handlers import api_cloud

def login(host: str):
    api_cloud.set_client_for_simulation(host=host)