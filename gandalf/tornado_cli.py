import tornado.gen as gen
import gandalf.client as client


class AsyncTornadoGandalfClient(client.GandalfClient):

    @gen.coroutine
    def _request(self, *args, **kwargs):
        url = kwargs.pop('url')
        data = kwargs.pop('data', None)
        if data:
            kwargs['body'] = data

        response = yield self.client(url, *args, **kwargs)
        raise gen.Return(response)

    @gen.coroutine
    def healthcheck(self):
        response = yield self._request(
            url=self._get_url('/healthcheck'),
            method="GET",
        )

        if response.code != 200:
            raise gen.Return(False)

        if hasattr(response, 'body'):
            raise gen.Return(response.body.decode('utf-8') == 'WORKING')

        if hasattr(response, 'text'):
            raise gen.Return(response.text == 'WORKING')

        raise gen.Return(False)
