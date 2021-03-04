class TPLinkApiResponse:
    def __init__(self, response):
        self._response = response

    @property
    def successful(self):
        return self._response.get('error_code') == 0

    @property
    def result(self):
        return self._response.get('result')
