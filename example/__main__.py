"""Example."""

import logging
from http import HTTPStatus
from typing import Literal

from aiohttp import web
from pydantic import BaseModel

from aiohttp_docs import Info, Response, docs, setup_docs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('example')


class PathResponse(BaseModel):
    """Path response model."""

    okay: Literal[True] = True
    path: str
    method: str
    fake: Literal['yes', 'no'] = 'no'


class ErrorResponse(BaseModel):
    """Error response model."""

    okay: Literal[False] = False
    error_message: str


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
            web.get('/func', func_page, allow_head=False),
            web.view('/cls', ClassPage),
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
        ),
        oas_path='/api/openapi.json',
    )
    web.run_app(app=app)


if __name__ == '__main__':
    main()
