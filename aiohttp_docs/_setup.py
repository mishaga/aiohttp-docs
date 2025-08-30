from aiohttp import web

from ._constants import ROUTE_NAME_SPEC_VIEW, ROUTE_NAME_STATIC, ROUTE_NAME_SWAGGER_VIEW, SWAGGER_UI_DIR_PATH
from ._enums import SwaggerLayout
from ._spec_builder import build_openapi_spec
from ._spec_models import Info
from ._views import get_json_spec_view, get_swagger_view


def setup_docs(  # noqa: PLR0913
    app: web.Application,
    *,
    info: Info,
    spec_path: str,
    swagger_path: str,
    static_path: str = '/static/swagger',
    layout: SwaggerLayout = SwaggerLayout.BASE,
    enabled: bool = True,
) -> None:
    """Add docs to a web app."""
    if not enabled:
        return

    spec = build_openapi_spec(
        app=app,
        info=info,
    )

    app.router.add_static(
        prefix=static_path,
        path=SWAGGER_UI_DIR_PATH,
        name=ROUTE_NAME_STATIC,
    )
    app.router.add_get(
        path=spec_path,
        handler=get_json_spec_view(spec=spec),
        name=ROUTE_NAME_SPEC_VIEW,
        allow_head=False,
    )
    app.router.add_get(
        path=swagger_path,
        handler=get_swagger_view(app=app, layout=layout),
        name=ROUTE_NAME_SWAGGER_VIEW,
        allow_head=False,
    )
