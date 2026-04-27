# aiohttp-docs

Auto-generate [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.2) specification and
[Swagger UI](https://swagger.io/tools/swagger-ui/) documentation for
[aiohttp](https://docs.aiohttp.org/) web servers.  
Swagger version: <!-- SWAGGER_UI_VERSION_START -->[v5.32.5](https://github.com/swagger-api/swagger-ui/releases/tag/v5.32.5)<!-- SWAGGER_UI_VERSION_END -->

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
        spec_url_path='/api/openapi.json',  # URL to for OpenAPI Specification
        swagger_url_path='/api/docs',  # URL for Swagger
    )

    web.run_app(app)


if __name__ == '__main__':
    main()
```

After starting the server, open `http://localhost:8080/api/docs` to see the Swagger UI.


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


### Path, query, header, and cookie parameters (and examples for them)

Define Pydantic models for each parameter location and pass them to the decorator.

```python
from datetime import date, datetime, UTC
from decimal import Decimal
from http import HTTPStatus

from aiohttp import web
from pydantic import BaseModel, Field
from aiohttp_docs import Example, Info, docs, setup_docs


def utc_today() -> date:
    return datetime.now(tz=UTC).date()


class UserOrdersInfo(BaseModel):
    user_id: int
    orders_count: int
    total_amount: Decimal
    date_from: date = Field(alias='from')
    date_to: date = Field(alias='to')

class PathParams(BaseModel):
    user_id: int


class QueryParams(BaseModel):
    date_from: date = Field(
        alias='from',
        default_factory=utc_today,
        description='Date from (including); Defaults to today',
        examples=[  # examples for "from" field
            Example(value='1970-01-01', summary='Start of UNIX Era'),
            Example(value='2020-10-10'),
            Example(value='2021-11-21'),
            Example(value=utc_today().isoformat(), summary='Today'),
        ],
    )
    date_to: date = Field(
        alias='to',
        default_factory=utc_today,
        description='Date to (including); Defaults to today',
    )


@docs(
    tags=['Admin', 'Users', 'Orders'],
    summary='List user orders',
    response_models={HTTPStatus.OK: UserOrdersInfo},
    path_model=PathParams,
    query_model=QueryParams,
)
async def admin_user_orders_info(request: web.Request) -> web.Response:
    user_id = int(request.match_info['user_id'])
    dates = QueryParams.model_validate(request.query)
    return web.json_response(
        {
            'user_id': user_id,
            'orders_count': 17,
            'total_amount': 139.95,
            'from': dates.date_from.isoformat(),
            'to': dates.date_to.isoformat(),
        }
    )


def main() -> None:
    app = web.Application()
    app.router.add_get('/admin/user/{user_id}/orders', admin_user_orders_info, allow_head=False)
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


class Item(BaseModel):
    id: int


class ItemResponse(BaseModel):
    id: int
    title: str


class ItemBody(BaseModel):
    title: str


class ItemView(web.View):
    @docs(
        tags=['Items'],
        summary='Get item by ID',
        path_model=Item,
        response_models={HTTPStatus.OK: ItemResponse},
    )
    async def get(self) -> web.Response:
        item_id = int(self.request.match_info['id'])
        return web.json_response({'id': item_id, 'title': 'Thing'})

    @docs(
        tags=['Items'],
        summary='Update item',
        path_model=Item,
        body_model=ItemBody,
        response_models={
            HTTPStatus.OK: Response(model=ItemResponse, description='Item updated'),
        },
    )
    async def put(self) -> web.Response:
        item_id = int(self.request.match_info['id'])
        body = ItemBody.model_validate_json(await self.request.content.read())
        return web.json_response({'id': item_id, 'title': body.title})

    @docs(
        tags=['Items'],
        summary='Delete item',
        path_model=Item,
        response_models={
            HTTPStatus.NO_CONTENT: Response(model=None, description='Item deleted'),
        },
    )
    async def delete(self) -> web.Response:
        return web.json_response(status=HTTPStatus.NO_CONTENT)


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
from http import HTTPStatus
from warnings import deprecated

from aiohttp import web
from pydantic import BaseModel

from aiohttp_docs import Info, docs, setup_docs


class LegacyResponse(BaseModel):
    status: str


@docs(
    tags=['Legacy'],
    deprecated=True,  # this will mark the API method as deprecated only for the documentation
    response_models={HTTPStatus.OK: LegacyResponse},
)
async def old_endpoint(_: web.Request) -> web.Response:
    return web.json_response({'status': 'old'})


@deprecated('Use /v2/resource instead')  # this will mark the function as deprecated, and it will be reflected in the documentation too
@docs(
    tags=['Legacy'],
    response_models={HTTPStatus.OK: LegacyResponse},
)
async def another_old_endpoint(_: web.Request) -> web.Response:
    return web.json_response({'status': 'very old'})


def main() -> None:
    app = web.Application()
    app.add_routes(
        [
            web.get('/one', old_endpoint, allow_head=False),
            web.get('/two', another_old_endpoint, allow_head=False),
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

    # disable docs for production
    # `/api/openapi.json`, `/api/docs` and `/static/swagger` will return 404 Not Found
    setup_docs(
        app,
        info=Info(title='My API', version='0.1.0'),
        enabled=os.getenv('ENVIRONMENT', '') != 'PRODUCTION',
    )

    web.run_app(app)


if __name__ == '__main__':
    main()
```


## Plans

- Nested models, root models
- Links in responses
- Move from TypedDict to pydantic models (because of "termsOfService", and "Parameter.in" for instance)

Version 1:

- authorization
- servers
- webhooks
- components
- security
- tags
- externalDocs

Version 2:

- Automatic validation of the body, response, query, path etc (based on annotations)

## Documentation

OpenAPI Specification: https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.2.md
