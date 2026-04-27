"""Example."""

from datetime import datetime
from enum import StrEnum
from http import HTTPStatus

from aiohttp import web
from pydantic import BaseModel, PositiveFloat, PositiveInt

from aiohttp_docs import Info, docs, setup_docs


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


@docs(
    tags=['Users'],
    path_model=PathUser,
    response_models={
        HTTPStatus.OK: User,
    },
)
async def user_info(_: web.Request) -> web.Response:
    """Index page."""
    return web.json_response({})


def main() -> None:
    """Main function."""
    app = web.Application()

    app.add_routes(
        [
            web.get('/user/{id}', user_info, allow_head=False),
        ],
    )
    setup_docs(
        app=app,
        info=Info(
            title='Title',
            version='version',
        ),
        servers=[],
    )

    web.run_app(app)


if __name__ == '__main__':
    main()
