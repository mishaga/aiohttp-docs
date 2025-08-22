from aiohttp import web

from ._spec_builder import build_openapi_spec
from ._spec_models import Info
from ._spec_views import get_json_spec


def setup_docs(
    app: web.Application,
    *,
    info: Info,
    oas_path: str,
) -> None:
    """Add docs to a web app."""
    spec = build_openapi_spec(
        app=app,
        info=info,
    )
    app.add_routes(
        [
            web.get(oas_path, get_json_spec(spec), allow_head=False),
        ],
    )
