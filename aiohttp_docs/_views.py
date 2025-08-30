from string import Template

from aiohttp import web
from aiohttp.typedefs import Handler

from ._constants import ROUTE_NAME_SPEC_VIEW, ROUTE_NAME_STATIC, SWAGGER_UI_DIR_PATH
from ._enums import SwaggerLayout
from ._spec_models import OpenApiSpecification


def get_json_spec_view(spec: OpenApiSpecification) -> Handler:
    """Return view with OAS (Open API specification) in JSON format."""

    async def inner(_: web.Request) -> web.Response:
        """Open API specification view."""
        return web.json_response(spec)

    return inner


def get_swagger_view(app: web.Application, layout: SwaggerLayout) -> Handler:
    """Return view with Swagger UI."""
    index_filename = 'index.html'
    index_path = SWAGGER_UI_DIR_PATH / index_filename
    original_index_content = index_path.read_text()

    spec_url = app.router[ROUTE_NAME_SPEC_VIEW].url_for()
    static_url = app.router[ROUTE_NAME_STATIC].url_for(filename=index_filename)

    index_content = Template(original_index_content).substitute(
        path=str(spec_url),
        static=static_url.parent,
        layout=layout.value,
    )

    async def swagger_view(_: web.Request) -> web.Response:
        """Swagger UI view."""
        return web.Response(
            text=index_content,
            content_type='text/html',
        )

    return swagger_view
