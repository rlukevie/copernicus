import requests
from factorytools.settings import *


class ProductSelector:
    def __init__(self, request):
        if not isinstance(request, dict):
            raise TypeError("Requests have to be dictionaries")
        if "q" not in request:
            raise KeyError("No key 'q' in request")
        else:
            self.request = request
            self.response = None

    def send(self):
        logging.info('Opensearch request: {}'.format(self.request))
        try:
            _response = requests.get(
                open_data_hub_url,
                params=self.request, auth=(opendatahub_user,
                                           opendatahub_password))
            if _response.status_code == 200:
                self.response = _response
            else:
                self.response = None
        except IOError:
            pass

    def parse(self):
        pass

    def select(self):
        pass


class SelectorQueue:
    def __init__(self):
        self.queue = []

    def append(self, request_instance):
        """Append ProductSelector instances to queue"""
        if not isinstance(request_instance, ProductSelector):
            raise TypeError("Only instances of ProductSelector can be appended")
        else:
            self.queue.append(request_instance)

    def send(self):
        """Send all requests in queue to Open Data Hub
        and return responses"""
        for request in self.queue:
            request.send()
