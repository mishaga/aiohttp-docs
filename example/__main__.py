"""Example."""

import logging
from http import HTTPStatus
from typing import Literal

from aiohttp import web
from pydantic import BaseModel, Field

from aiohttp_docs import Example, Info, Response, docs, setup_docs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('example')


class PathResponse(BaseModel):
    """Path response model."""

    okay: Literal[True] = True
    path: str
    method: str
    fake: Literal['yes', 'no'] = 'no'


class PathModel(BaseModel):
    """Path parameters model."""

    name: str


class QueryModel(BaseModel):
    """Query model."""

    page: int
    limit: int = 100


class HeaderModel(BaseModel):
    """Headers model."""

    content_type: str = Field(
        default='application/xml',
        description='Okay, this is a CT description',
        alias='Content-Type',
    )
    x_accept: str | None = Field(
        default=None,
        deprecated='This header is deprecated',
        examples=[
            Example(summary='Summary', value='*/1'),
            Example(description='Description', value='*/2'),
            Example(summary='all', description='Accept all', value='*/*'),
            Example(summary='xml', description='Accept XML only', value='application/xml'),
            Example(summary='text', description='Accept text only', externalValue='/func'),
            Example(description='last one'),
        ],
        alias='X-Accept',
    )
    x_ip: str = Field(serialization_alias='X-IP')


class CookieModel(BaseModel):
    """Cookie model."""

    first_name: str
    last_name: str
    path: PathModel


class BodyModel(BaseModel):
    """Post request model."""

    name: str
    age: int
    is_male: bool = False
    height: float
    weight: float


class ErrorResponse(BaseModel):
    """Error response model."""

    okay: Literal[False] = False
    error_message: str


async def terms_view(_: web.Request) -> web.Response:
    """Terms of service page."""
    return web.Response(text='My terms of service')


@docs(
    tags=['Index'],
    response_models={
        HTTPStatus.OK: Response(model=PathResponse),
        400: Response(model=ErrorResponse),
        401: ErrorResponse,
    },
)
async def func_page(request: web.Request) -> web.Response:
    """My fancy function.

    Lorem ipsum dolor sit amet consectetur adipiscing elit. Placerat in id cursus mi pretium tellus duis.
    Urna tempor pulvinar vivamus fringilla lacus nec metus. Integer nunc posuere ut hendrerit semper vel class.
    Conubia nostra inceptos himenaeos orci varius natoque penatibus. Mus donec rhoncus eros lobortis
    nulla molestie mattis. Purus est efficitur laoreet mauris pharetra vestibulum fusce.

    ```python
    import requests

    res = requests.get('https://mishaga.com/)
    print(res.status)
    print(res.text)
    ```

    Here is the list:
    - Okay
    - Not Okay
    - Absolutely *not* **okay**
    """
    resp = PathResponse(
        path=request.path,
        method=request.method,
    )
    return web.json_response(resp.model_dump())


@docs(
    tags=['Index'],
    response_models={
        HTTPStatus.OK: Response(model=PathResponse),
        HTTPStatus.NOT_FOUND: Response(model=PathResponse, description='Not really found :('),
    },
    summary='1 2 3',
    description='4 5 6',
    path_model=PathModel,
    query_model=QueryModel,
    header_model=HeaderModel,
    cookie_model=CookieModel,
)
async def with_param(request: web.Request) -> web.Response:
    """With param function."""
    name = request.match_info['name']
    return web.Response(text=f'name: {name}')


class ClassPage(web.View):
    """Class page view."""

    @docs(
        tags=['Index'],
        response_models={
            HTTPStatus.OK: Response(model=PathResponse),
            HTTPStatus.BAD_REQUEST: Response(model=ErrorResponse),
        },
        description='My fancy description',
    )
    async def get(self) -> web.Response:
        """Class GET method."""
        resp = PathResponse(
            path=self.request.path,
            method=self.request.method,
        )
        return web.json_response(resp.model_dump())

    @docs(
        tags=['Index'],
        response_models={
            HTTPStatus.OK: Response(
                model=PathResponse,
                description='Info about...',
            ),
            400: Response(
                model=ErrorResponse,
                description='Well... not really good',
            ),
            401: ErrorResponse,
            402: ErrorResponse,
            403: ErrorResponse,
        },
        summary='Well well well...',
        body_model=BodyModel,
    )
    async def post(self) -> web.Response:
        """Class POST method."""
        resp = PathResponse(
            path=self.request.path,
            method=self.request.method,
        )
        return web.json_response(resp.model_dump())


def create_app() -> web.Application:
    """Create web server application."""
    app = web.Application()
    app.add_routes(
        [
            web.get('/with-param/{name}', with_param, allow_head=False),
            web.get('/func', func_page, allow_head=False),
            web.view('/cls', ClassPage),
            web.get('/terms', terms_view, allow_head=False),
        ],
    )
    return app


def main() -> None:
    """Main."""
    app = create_app()
    setup_docs(
        app,
        info=Info(
            title='Test API of mine',
            version='1.0.2',
            summary='Summary',
            description='Description',
            termsOfService='/terms',
        ),
        spec_path='/api/openapi.json',
        swagger_path='/api/doc',
        static_path='/api/swagger-ui/static-files',
    )
    web.run_app(app=app)


if __name__ == '__main__':
    main()
