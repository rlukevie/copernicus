import pytest
from factorytools.request import Request, RequestQueue


class TestRequest:
    def test_good_request(self):
        good_request = Request({"q": 'beginposition:[NOW-10MONTHS TO NOW] AND footprint:"'
                                     'Intersects(48.2000, 16.1000)" AND producttype:"S2MSI1C" AND '
                                     'cloudcoverpercentage:[0 TO 10]',
                                "rows": "10"})

        assert good_request.request == {"q": 'beginposition:[NOW-10MONTHS TO NOW] AND '
                                             'footprint:"Intersects(48.2000, 16.1000)" AND '
                                             'producttype:"S2MSI1C" AND cloudcoverpercentage:[0 TO '
                                             '10]',
                                        "rows": "10"}

    def test_request_wrong_type(self):
        with pytest.raises(TypeError):
            bad_request = Request('123')

    def test_request_q_not_in_keys(self):
        with pytest.raises(KeyError):
            no_q_request = Request({'w': '123'})


class TestRequestQueue:
    def test_request_queue_initialize(self):
        request1 = Request({"q": 'beginposition:[NOW-10MONTHS TO NOW] AND footprint:"Intersects('
                                 '48.2000, 16.1000)" AND producttype:"S2MSI1C" AND '
                                 'cloudcoverpercentage:[0 TO 10]',
                            "rows": "10"})
        request2 = Request({"q": 'beginposition:[NOW-10MONTHS TO NOW] AND footprint:"Intersects('
                                 '49.2000, 16.1000)" AND producttype:"S2MSI1C" AND '
                                 'cloudcoverpercentage:[0 TO 10]',
                            "rows": "10"})
        queue = RequestQueue()
        queue.append(request1)
        queue.append(request2)

        assert queue.queries[0].request['q'] == 'beginposition:[NOW-10MONTHS TO NOW] AND ' \
                                                'footprint:"Intersects(48.2000, 16.1000)" AND ' \
                                                'producttype:"S2MSI1C" AND '\
                                                'cloudcoverpercentage:[0 TO 10]'
        assert queue.queries[1].request['q'] == 'beginposition:[NOW-10MONTHS TO NOW] AND ' \
                                                'footprint:"Intersects(49.2000, 16.1000)" AND ' \
                                                'producttype:"S2MSI1C" AND '\
                                                'cloudcoverpercentage:[0 TO 10]'

    def test_request_queue_type(self):
        with pytest.raises(TypeError):
            queue = RequestQueue()
            queue.append({'q': 'd'})

