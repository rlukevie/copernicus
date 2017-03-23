import requests
import xml.etree.cElementTree as ET

from factorytools.settings import *


class ProductSelector:
    instances = []

    def __init__(self, request):
        if not isinstance(request, dict):
            raise TypeError("Requests have to be dictionaries")
        if "q" not in request:
            raise KeyError("No key 'q' in request")
        else:
            self.__class__.instances.append(self)
            self.request = request
            self._tree = None
            self.response = None
            self.selected_product = None

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

    def select(self):
        # TODO: Was, wenn bei "send" None herauskommt?
        self._tree = ET.fromstring(self.response.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        self.selected_product = self._tree.find("./atom:entry", ns)
