# aiohttp-docs

Auto-generate [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.2) specification and
[Swagger UI](https://swagger.io/tools/swagger-ui/) documentation for
[aiohttp](https://docs.aiohttp.org/) web servers.  
Swagger version: <!-- SWAGGER_UI_VERSION_START -->[v5.31.2](https://github.com/swagger-api/swagger-ui/releases/tag/v5.31.2)<!-- SWAGGER_UI_VERSION_END -->

Annotate your route handlers with the `@docs()` decorator and call `setup_docs()` once at startup — the library
builds the full spec and serves both the JSON endpoint and the interactive Swagger UI.

**Python >= 3.13** is required.


## Installation

```bash
pip install aiohttp-docs
```


## Quick start

```python
from http import HTTPStatus

from aiohttp import web
from pydantic import BaseModel

from aiohttp_docs import Info, docs, setup_docs


class UserResponse(BaseModel):
    id: int
    name: str


@docs(
    tags=['Users'],
    summary='Get current user',
    response_models={HTTPStatus.OK: UserResponse},
)
async def users_me(_: web.Request) -> web.Response:
    """Return the current user."""
    return web.json_response({'id': 1, 'name': 'John'})


def main() -> None:
    app = web.Application()
    app.router.add_get('/users/me', users_me, allow_head=False)

    setup_docs(
        app,
        info=Info(
            title='My API',
            version='0.1.0',
        ),
        spec_uri='/api/openapi.json',  # URL to for OpenAPI Specification
        swagger_uri='/api/doc',  # URL for Swagger
    )

    web.run_app(app)


if __name__ == '__main__':
    main()
```

After starting the server, open `http://localhost:8080/api/doc` to see the Swagger UI.


## Examples


### Request body and response models

Use `body_model` to describe the JSON request body.
Use `response_models` to document possible responses — keys are HTTP status codes (as `int` or `HTTPStatus`),
values are Pydantic models or `Response(model=..., description=...)` dicts.

```python
from http import HTTPStatus

from aiohttp import web
from pydantic import BaseModel, ValidationError

from aiohttp_docs import Info, Response, docs, setup_docs


class CreateUserRequest(BaseModel):
    name: str
    age: int
    is_active: bool = True


class CreateUserResponse(BaseModel):
    id: int
    name: str


class ErrorResponse(BaseModel):
    error_message: str


@docs(
    tags=['Users'],
    summary='Create a new user',
    body_model=CreateUserRequest,
    response_models={
        HTTPStatus.CREATED: Response(model=CreateUserResponse, description='User created'),
        HTTPStatus.BAD_REQUEST: ErrorResponse,
    },
)
async def users_create(request: web.Request) -> web.Response:
    try:
        body = CreateUserRequest.model_validate_json(await request.content.read())
    except ValidationError as e:
        return web.json_response({'error_message': str(e)}, status=HTTPStatus.BAD_REQUEST)

    return web.json_response({'id': 1, 'name': body.name}, status=201)


def main() -> None:
    app = web.Application()
    app.router.add_post('/users', users_create)
    setup_docs(app, info=Info(title='My API', version='0.1.0'))
    web.run_app(app)


if __name__ == '__main__':
    main()
```


### Path, query, header, and cookie parameters

Define Pydantic models for each parameter location and pass them to the decorator.

```python
from aiohttp import web
from pydantic import BaseModel, Field

from aiohttp_docs import Info, docs, setup_docs


class PathParams(BaseModel):
    user_id: int


class QueryParams(BaseModel):
    page: int = 1
    limit: int = Field(default=20, description='Items per page')


@docs(
    tags=['Admin', 'Users', 'Orders'],
    summary='List user orders',
    path_model=PathParams,
    query_model=QueryParams,
)
async def admin_list_user_orders(request: web.Request) -> web.Response:
    user_id = int(request.match_info['user_id'])
    return web.json_response({'user_id': user_id, 'orders': []})


def main() -> None:
    app = web.Application()
    app.router.add_post('/admin/user/orders', admin_list_user_orders)
    setup_docs(app, info=Info(title='My API', version='0.1.0'))
    web.run_app(app)


if __name__ == '__main__':
    main()
```


### Class-based views

The `@docs()` decorator works on individual methods of `aiohttp.web.View` subclasses.

```python
from http import HTTPStatus

from aiohttp import web
from pydantic import BaseModel

from aiohttp_docs import Info, Response, docs, setup_docs


class ItemResponse(BaseModel):
    id: int
    title: str


class ItemBody(BaseModel):
    title: str


class ItemView(web.View):
    @docs(
        tags=['Items'],
        summary='Get item by ID',
        response_models={HTTPStatus.OK: ItemResponse},
    )
    async def get(self) -> web.Response:
        return web.json_response({'id': 1, 'title': 'Thing'})

    @docs(
        tags=['Items'],
        summary='Update item',
        body_model=ItemBody,
        response_models={
            HTTPStatus.OK: Response(model=ItemResponse, description='Updated item'),
        },
    )
    async def put(self) -> web.Response:
        body = ItemBody.model_validate_json(await self.request.content.read())
        return web.json_response({'id': 1, 'title': body.title})


def main() -> None:
    app = web.Application()
    app.router.add_view('/items/{id}', ItemView)
    setup_docs(app, info=Info(title='My API', version='0.1.0'))
    web.run_app(app)


if __name__ == '__main__':
    main()
```


### Deprecating endpoints

Mark an endpoint as deprecated explicitly via the decorator or by using the standard `@deprecated` decorator from `warnings`.

```python
from warnings import deprecated

from aiohttp import web

from aiohttp_docs import Info, docs, setup_docs


@docs(tags=['Legacy'], deprecated=True)
async def old_endpoint(_: web.Request) -> web.Response:
    return web.json_response({'status': 'old'})


@deprecated('Use /v2/resource instead')
@docs(tags=['Legacy'])
async def another_old_endpoint(_: web.Request) -> web.Response:
    return web.json_response({'status': 'old'})


def main() -> None:
    app = web.Application()
    app.add_routes(
        [
            web.get('/one', old_endpoint, allow_head=False),
            web.get('/two', old_endpoint, allow_head=False),
        ],
    )
    setup_docs(app, info=Info(title='My API', version='0.1.0'))
    web.run_app(app)


if __name__ == '__main__':
    main()
```


### Disabling docs in production

Pass `enabled=False` to `setup_docs()` to skip registration entirely.

```python
import os

from aiohttp import web
from aiohttp_docs import Info, setup_docs


def main():
    app = web.Application()

    setup_docs(
        app,
        info=Info(title='My API', version='1.0.0'),
        enabled=os.getenv('ENVIRONMENT', '') != 'PRODUCTION',
    )

    web.run_app(app)


if __name__ == '__main__':
    main()
```


## Plans

- Nested models
- Move from TypedDict to pydantic models
- Authorization
- Automatic validation of the body, response, query, path etc (based on annotations)
