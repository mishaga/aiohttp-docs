"""Example."""

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from http import HTTPStatus
from warnings import deprecated

from aiohttp import web
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

from aiohttp_docs import Example, Info, Response, Server, ServerVariable, SwaggerLayout, docs, setup_docs

# ---------------------------------------------------------------------------
# Shared models
# ---------------------------------------------------------------------------


class PathUser(BaseModel):
    """Path User model."""

    id: PositiveInt


class OrderStatus(StrEnum):
    """Order status enum."""

    CREATED = 'created'
    PAID = 'paid'
    SENT = 'sent'
    DELIVERED = 'delivered'


class Order(BaseModel):
    """Order model."""

    id: PositiveInt
    created_at: datetime
    amount: PositiveFloat
    status: OrderStatus
    items_count: PositiveInt


class User(BaseModel):
    """User model."""

    id: PositiveInt
    first_name: str
    last_name: str
    is_active: bool
    orders: list[Order]


class ErrorResponse(BaseModel):
    """Error response model."""

    error_message: str


# ---------------------------------------------------------------------------
# 1. GET with path_model + nested response (existing)
# ---------------------------------------------------------------------------


@docs(
    tags=['Users'],
    summary='Get user by ID',
    path_model=PathUser,
    response_models={
        HTTPStatus.OK: User,
    },
)
async def user_info(_: web.Request) -> web.Response:
    """Return user details including their orders."""
    return web.json_response({})


# ---------------------------------------------------------------------------
# 2. POST with body_model + multiple response statuses
# ---------------------------------------------------------------------------


class CreateUserRequest(BaseModel):
    """Create user request body."""

    first_name: str
    last_name: str
    email: str
    age: int = Field(ge=18)


class CreateUserResponse(BaseModel):
    """Created user response."""

    id: PositiveInt
    first_name: str
    last_name: str


@docs(
    tags=['Users'],
    summary='Create a new user',
    body_model=CreateUserRequest,
    response_models={
        HTTPStatus.CREATED: Response(model=CreateUserResponse, description='User successfully created'),
        HTTPStatus.BAD_REQUEST: Response(model=ErrorResponse, description='Validation failed'),
        HTTPStatus.CONFLICT: Response(model=ErrorResponse, description='User with this email already exists'),
    },
)
async def create_user(_: web.Request) -> web.Response:
    """Create a new user account."""
    return web.json_response({}, status=HTTPStatus.CREATED)


# ---------------------------------------------------------------------------
# 3. GET with query_model (aliases + examples) and header_model
# ---------------------------------------------------------------------------


class OrdersQuery(BaseModel):
    """Query parameters for listing orders."""

    date_from: date = Field(
        alias='from',
        default_factory=lambda: datetime.now(tz=UTC).date(),
        description='Start date (inclusive)',
        examples=[
            Example(value='2024-01-01', summary='Start of 2024'),
            Example(value='2025-06-15'),
        ],
    )
    date_to: date = Field(
        alias='to',
        default_factory=lambda: datetime.now(tz=UTC).date(),
        description='End date (inclusive)',
    )
    status: OrderStatus | None = Field(default=None, description='Filter by order status')
    min_amount: Decimal | None = Field(default=None, description='Minimum order amount', ge=0)


class AuthHeader(BaseModel):
    """Header parameters for authenticated endpoints."""

    x_api_key: str = Field(alias='X-Api-Key', description='API key for authentication')
    x_request_id: str | None = Field(default=None, alias='X-Request-Id', description='Optional request tracing ID')


class OrderListResponse(BaseModel):
    """Paginated order list response."""

    items: list[Order]
    total: int


@docs(
    tags=['Orders'],
    summary='List orders',
    description='Retrieve orders filtered by date range, status, and minimum amount.',
    path_model=PathUser,
    query_model=OrdersQuery,
    header_model=AuthHeader,
    response_models={
        HTTPStatus.OK: OrderListResponse,
        HTTPStatus.UNAUTHORIZED: Response(model=ErrorResponse, description='Invalid or missing API key'),
    },
)
async def list_orders(_: web.Request) -> web.Response:
    """List orders for a user."""
    return web.json_response({})


# ---------------------------------------------------------------------------
# 4. Class-based view (GET / PUT / DELETE)
# ---------------------------------------------------------------------------


class PathItem(BaseModel):
    """Path parameters for item endpoints."""

    item_id: PositiveInt


class ItemResponse(BaseModel):
    """Item response model."""

    id: PositiveInt
    title: str
    price: Decimal
    in_stock: bool


class UpdateItemRequest(BaseModel):
    """Update item request body."""

    title: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    in_stock: bool | None = None


class ItemView(web.View):
    """CRUD view for items."""

    @docs(
        tags=['Items'],
        summary='Get item by ID',
        path_model=PathItem,
        response_models={
            HTTPStatus.OK: ItemResponse,
            HTTPStatus.NOT_FOUND: Response(model=ErrorResponse, description='Item not found'),
        },
    )
    async def get(self) -> web.Response:
        """Retrieve a single item."""
        return web.json_response({})

    @docs(
        tags=['Items'],
        summary='Update item',
        path_model=PathItem,
        body_model=UpdateItemRequest,
        response_models={
            HTTPStatus.OK: Response(model=ItemResponse, description='Item updated'),
            HTTPStatus.NOT_FOUND: ErrorResponse,
        },
    )
    async def put(self) -> web.Response:
        """Update an existing item."""
        return web.json_response({})

    @docs(
        tags=['Items'],
        summary='Delete item',
        path_model=PathItem,
        response_models={
            HTTPStatus.NO_CONTENT: Response(description='Item deleted'),
            HTTPStatus.NOT_FOUND: ErrorResponse,
        },
    )
    async def delete(self) -> web.Response:
        """Delete an item."""
        return web.json_response(status=HTTPStatus.NO_CONTENT)


# ---------------------------------------------------------------------------
# 5. Deprecated endpoints (both styles)
# ---------------------------------------------------------------------------


class LegacyUsersResponse(BaseModel):
    """Legacy response with flat user list."""

    users: list[str]


@docs(
    tags=['Legacy'],
    summary='List users (old)',
    deprecated=True,
    response_models={
        HTTPStatus.OK: LegacyUsersResponse,
    },
)
async def legacy_list_users(_: web.Request) -> web.Response:
    """Old user listing endpoint — use GET /users instead."""
    return web.json_response({})


@deprecated('Use GET /user/{id}/orders instead')
@docs(
    tags=['Legacy'],
    summary='Get user orders (old)',
    response_models={
        HTTPStatus.OK: OrderListResponse,
    },
)
async def legacy_user_orders(_: web.Request) -> web.Response:
    """Old user orders endpoint."""
    return web.json_response({})


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------


def main() -> None:
    """Main function."""
    app = web.Application()

    app.add_routes(
        [
            web.get('/user/{id}', user_info, allow_head=False),
            web.post('/users', create_user),
            web.get('/user/{id}/orders', list_orders, allow_head=False),
            web.view('/items/{item_id}', ItemView),
            web.get('/legacy/users', legacy_list_users, allow_head=False),
            web.get('/legacy/orders', legacy_user_orders, allow_head=False),
        ],
    )
    setup_docs(
        app=app,
        info=Info(
            title='Example API',
            version='0.1.0',
        ),
        servers=[
            Server(
                url='https://api.reminder.plus',
                description='Prod API server',
            ),
            Server(
                url='https://api.ffchat.dev',
                description='Dev API server',
                variables={
                    'token': ServerVariable(
                        enum=['one', 'two', 'three'],
                        default='three',
                        description='API token',
                    ),
                },
            ),
        ],
        layout=SwaggerLayout.BASE,
    )

    web.run_app(app)


if __name__ == '__main__':
    main()
