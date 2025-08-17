"""Example."""

import logging
from http import HTTPStatus
from typing import Literal

from aiohttp import web
from pydantic import BaseModel

from aiohttp_docs import docs

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('example')


class PathResponse(BaseModel):
    """Path response model."""

    okay: Literal[True]
    path: str


class ErrorResponse(BaseModel):
    """Error response model."""

    okay: Literal[False]
    error_message: str


@docs(
    tags=['Index'],
    response_models={
        HTTPStatus.OK: PathResponse,
        HTTPStatus.BAD_REQUEST: ErrorResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
)
async def func_page(request: web.Request) -> web.Response:
    """Function."""
    return web.json_response({'okay': True, 'path': request.path})


class ClassPage(web.View):
    """Class page view."""

    @docs(
        tags=['MIndex'],
        response_models={
            HTTPStatus.OK: PathResponse,
            HTTPStatus.BAD_REQUEST: ErrorResponse,
        },
    )
    async def get(self) -> web.Response:
        """Class method."""
        return web.json_response({'okay': True, 'path': self.request.path})


def create_app() -> web.Application:
    """Create web server application."""
    app = web.Application()
    app.add_routes(
        [
            web.get('/func', func_page),
            web.view('/cls', ClassPage),
        ],
    )
    return app


def main() -> None:
    """Main."""
    logger.info(getattr(func_page, '_openapi_docs', None))
    logger.info(getattr(ClassPage.get, '_openapi_docs', None))

    app = create_app()
    web.run_app(app=app)


if __name__ == '__main__':
    main()
