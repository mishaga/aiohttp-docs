"""Example."""

import logging
from http import HTTPStatus
from typing import Literal

from aiohttp import web
from pydantic import BaseModel

from aiohttp_docs import docs, OpenapiJsonSpec, OpenapiYamlSpec, ResponseData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('example')


class PathResponse(BaseModel):
    """Path response model."""

    okay: Literal[True]
    path: str
    fake: Literal['yes', 'no'] = 'no'


class ErrorResponse(BaseModel):
    """Error response model."""

    okay: Literal[False]
    error_message: str


@docs(
    # tags=['Index'],
    response_models={
        HTTPStatus.OK: ResponseData(model=PathResponse),
        400: ResponseData(model=ErrorResponse),
        401: ErrorResponse,
    },
)
async def func_page(request: web.Request) -> web.Response:
    """Function."""
    return web.json_response({'okay': True, 'path': request.path})


class ClassPage(web.View):
    """Class page view."""

    @docs(
        # tags=['Index'],
        response_models={
            HTTPStatus.OK: ResponseData(model=PathResponse),
            HTTPStatus.BAD_REQUEST: ResponseData(model=ErrorResponse),
        },
    )
    async def get(self) -> web.Response:
        """Class method."""
        return web.json_response({'okay': True, 'path': self.request.path, 'method': 'GET'})

    @docs(
        # tags=['Index'],
        response_models={
            HTTPStatus.OK: ResponseData(model=PathResponse, description='Info about...'),
            HTTPStatus.BAD_REQUEST: ErrorResponse,
        },
    )
    async def post(self) -> web.Response:
        """Class method."""
        return web.json_response({'okay': True, 'path': self.request.path, 'method': 'POST'})


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


def setup_docs(app: web.Application) -> None:
    """Add docs to a web app."""
    app.add_routes(
        [
            web.view('/openapi.json', OpenapiJsonSpec),
            web.view('/openapi.yaml', OpenapiYamlSpec),
        ],
    )


def main() -> None:
    """Main."""
    # print(PathResponse.model_json_schema())
    # logger.info(getattr(func_page, '_openapi_docs', None))
    # logger.info(getattr(ClassPage.get, '_openapi_docs', None))

    app = create_app()
    setup_docs(app=app)
    web.run_app(app=app)


if __name__ == '__main__':
    main()
