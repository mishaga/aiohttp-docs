from collections.abc import Awaitable, Callable

from aiohttp import web

from ._spec_models import OpenApiSpecification

type DocHandler = Callable[[web.Request], Awaitable[web.Response]]


def get_json_spec(spec: OpenApiSpecification) -> DocHandler:
    async def inner(_: web.Request) -> web.Response:
        return web.json_response(spec)

    return inner
