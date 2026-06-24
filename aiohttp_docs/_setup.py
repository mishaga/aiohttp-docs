from aiohttp import web

from ._constants import ROUTE_NAME_SPEC_VIEW, ROUTE_NAME_SWAGGER_STATIC, ROUTE_NAME_SWAGGER_VIEW, SWAGGER_UI_DIR_PATH
from ._enums import SwaggerLayout
from ._spec_builder import build_openapi_spec
from ._spec_models import Info, SecurityRequirement, SecurityScheme, Server
from ._views import get_json_spec_view, get_swagger_view


def setup_docs(  # noqa: PLR0913
    app: web.Application,
    *,
    info: Info,
    servers: list[Server] | None = None,
    security_schemes: dict[str, SecurityScheme] | None = None,
    security: list[SecurityRequirement] | None = None,
    spec_url_path: str = '/api/openapi.json',
    swagger_url_path: str = '/api/docs',
    static_url_path: str = '/static/swagger',
    layout: SwaggerLayout = SwaggerLayout.BASE,
    enabled: bool = True,
) -> None:
    """Add docs to a web app."""
    if not enabled:
        return

    spec = build_openapi_spec(
        app=app,
        info=info,
        servers=servers,
        security_schemes=security_schemes,
        security=security,
    )

    app.router.add_static(
        prefix=static_url_path,
        path=SWAGGER_UI_DIR_PATH,
        name=ROUTE_NAME_SWAGGER_STATIC,
    )
    app.router.add_get(
        path=spec_url_path,
        handler=get_json_spec_view(spec=spec),
        name=ROUTE_NAME_SPEC_VIEW,
        allow_head=False,
    )
    app.router.add_get(
        path=swagger_url_path,
        handler=get_swagger_view(app=app, layout=layout),
        name=ROUTE_NAME_SWAGGER_VIEW,
        allow_head=False,
    )
