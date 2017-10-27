import asyncio
import argparse
from datetime import datetime, timezone

from aiohttp import web

from omm.mock import ResponseMock


app = web.Application()


def verb_and_path(request):
    verb, path = request.match_info['verb'].upper(), request.match_info['path']
    if verb not in ('GET', 'POST', 'PUT', 'DELETE'):
        return web.Response(status=400, text='No supported verb found for: {}'.format(verb))
    return verb, path


async def call_mock(request):
    """
    Returns data for mocked (verb, path) pair
    :param request: HTTP request
    :type request: web.Request
    :return: web.Response
    """
    received = datetime.now(tz=timezone.utc)
    verb, path = request.method, request.match_info['path']
    with await app['mocks_lock']:
        if (verb, path) not in app['mocks']:
            return web.Response(status=404)
        matching_mocks = app['mocks'][(verb, path)]
        response = None
        for mock in matching_mocks:
            if mock.sent >= mock.repeat:
                continue
            response = mock.response
            mock.sent += 1
            break
        if not response:
            for mock in matching_mocks:
                mock.sent = 0
    if not response:
        return await call_mock(request)
    body = await request.text() if verb in ('POST', 'PUT') else None
    app['mocks_history'][(verb, path)].append({
        'url': str(request.url),
        'remote_addr': request.remote,
        'body': body,
        'received': received.isoformat(),
        'headers': dict(request.headers.items()),
        'response': {
            'status': response.status,
            'headers': dict(response.headers.items()),
            'body': response.text
        }
    })
    return response


async def mock_init(request):
    """
    Creates a mock endpoint responding with given body
    :param request: HTTP request
    :type request: web.Request
    :return: web.Response
    """
    verb, path = verb_and_path(request)
    mock = await ResponseMock.from_request(request)
    with await app['mocks_lock']:
        app['mocks'][(verb, path)] = [mock]
        app['mocks_history'][(verb, path)] = []
    return web.Response(status=200)


async def mock_history(request):
    verb, path = verb_and_path(request)
    history = app['mocks_history'][(verb, path)]
    return web.json_response(history)


async def mock_add(request):
    verb, path = verb_and_path(request)
    mock = await ResponseMock.from_request(request)
    with await app['mocks_lock']:
        app['mocks'].setdefault((verb, path), []).append(mock)
        app['mocks_history'].setdefault((verb, path), [])
    return web.Response(status=200)


async def mock_remove(request):
    verb, path = request.match_info['verb'].upper(), request.match_info['path']
    with await app['mocks_lock']:
        if (verb, path) in app['mocks']:
            del app['mocks'][(verb, path)]
    return web.Response(status=200)


def main():
    parser = argparse.ArgumentParser(description='oh-my-mock server runner')
    parser.add_argument('--host', help='HTTP server host', type=str, default='0.0.0.0')
    parser.add_argument('--port', help='HTTP server port', type=int, default=8080)
    args = parser.parse_args()

    app.router.add_post('/mock/{verb}/{path:.*}', mock_init)
    app.router.add_get('/mock/{verb}/{path:.*}', mock_history)
    app.router.add_put('/mock/{verb}/{path:.*}', mock_add)
    app.router.add_delete('/mock/{verb}/{path:.*}', mock_remove)
    app.router.add_route('*', '/{path:.*}', call_mock)

    app['mocks'] = {}
    app['mocks_lock'] = asyncio.Lock()
    app['mocks_history'] = {}

    web.run_app(app, host=args.host, port=args.port)
