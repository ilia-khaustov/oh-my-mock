from aiohttp import web


class ResponseMock(object):
    @staticmethod
    async def from_request(request):
        """
        Generates ResponseMock object from client request
        :param request: Incoming POST/PUT request
        :type request: web.Request
        :return: ResponseMock
        """
        try:
            status = int(request.query.get('status', 200))
        except (ValueError, TypeError):
            return web.Response(status=400,
                                text='Invalid integer sent in "status" param: {}'.format(request.query['status']))

        try:
            repeat = int(request.query.get('repeat', 1))
        except (ValueError, TypeError):
            return web.Response(status=400,
                                text='Invalid integer sent in "repeat" param: {}'.format(request.query['repeat']))

        headers = {}
        for header, value in request.raw_headers:
            header, value = str(header), str(value)
            if header.startswith('x-mock-'):
                headers[header[7:]] = value

        payload = await request.text()

        return ResponseMock(payload=payload, repeat=repeat, status=status, headers=headers)

    def __init__(self, payload=None, repeat=1, status=200, headers=None):
        self.payload = payload
        self.repeat = repeat
        self.status = status
        self.headers = headers or {}
        self.sent = 0

    @property
    def response(self):
        """
        Returns aiohttp server Response object
        :return: web.Response
        """
        return web.Response(
            status=self.status,
            headers=self.headers,
            body=bytes(self.payload, encoding='utf8')
        )
