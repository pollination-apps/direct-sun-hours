import streamlit as st
from uuid import uuid4

class Query:
    """Class to create the query to submit to Pollination."""
    _defaults = {
        'job_id': None
    }

    def __init__(self, platform = 'web'):
        self._query_params = st.experimental_get_query_params()
        self._job_id = self._query_params.get('job-id', [None])[0]
        self._owner = self._query_params.get('owner', [None])[0]
        self._project = self._query_params.get('project', [None])[0]
        self.model_id = self._query_params.get('model-id', [str(uuid4())])[0]
        self._platform = platform

        self._update_query()

    @property
    def query_params(self):
        params = {
            'model-id': self.model_id,
            '__platform__': self.platform
        }

        if self._job_id is not None:
            params['job-id'] = self._job_id
        if self._owner is not None:
            params['owner'] = self._owner
        if self._project is not None:
            params['project'] = self._project

        return params

    def _update_query(self):
        st.experimental_set_query_params(**self.query_params)
    
    def add_params(self, 
        params : dict):
        self._query_params = {**self._query_params, 
            **params}
        self._update_query()

    @property
    def platform(self):
        return self._platform

    @property
    def job_id(self):
        return self._job_id

    @job_id.setter
    def job_id(self, value):
        self._job_id = value
        self._update_query()

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value
        self._update_query()

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        self._update_query()

