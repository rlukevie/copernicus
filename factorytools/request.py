class Request:
    def __init__(self, request):
        if not isinstance(request, dict):
            raise TypeError("Requests have to be dictionaries")
        if "q" not in request:
            raise KeyError("No key 'q' in request")
        else:
            self.request = request


class RequestQueue:
    def __init__(self):
        self.requests = []

    def append(self, query_instance):
        if not isinstance(query_instance, Request):
            raise TypeError("Only instances of Request can be appended")
        else:
            self.requests.append(query_instance)
