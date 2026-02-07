class TPLinkApiResponse:
    def __init__(self, response):
        self._response = response

    @property
    def successful(self):
        return self._response.get('error_code') == 0

    @property
    def error_code(self):
        return self._response.get('error_code')

    @property
    def result(self):
        return self._response.get('result')

    @property
    def msg(self):
        return self._response.get('msg')
