from math import ceil
from typing import Generic, TypeVar, Annotated
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


T = TypeVar("T")

Page = Annotated[int, Field(ge=1)]
Limit = Annotated[int, Field(ge=1, le=100)]


class PaginatedResponse(GenericModel, Generic[T]):
    data: list[T]
    total: int
    page: Page
    limit: Limit
    total_pages: int

    @classmethod
    def from_items(
        cls,
        *,
        items: list[T],
        total: int,
        page: int,
        limit: int,
    ) -> "PaginatedResponse[T]":
        total_pages = ceil(total / limit) if total > 0 else 0
        return cls(
            data=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
