from typing import Any

from fastapi import FastAPI, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, field_validator

app = FastAPI(title="Library Management API")


class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    author: str

    @field_validator("title", "author", mode="before")
    @classmethod
    def validate_non_empty_string(cls, v: Any, info) -> str:
        if v is None:
            raise ValueError(f"{info.field_name} cannot be null")
        if not isinstance(v, str):
            raise ValueError(f"{info.field_name} must be a string")
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v_stripped


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    author: str | None = None

    @field_validator("title", "author", mode="before")
    @classmethod
    def validate_non_empty_string(cls, v: Any, info) -> str:
        if v is None:
            raise ValueError(f"{info.field_name} cannot be null")
        if not isinstance(v, str):
            raise ValueError(f"{info.field_name} must be a string")
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v_stripped


class BookResponse(BaseModel):
    id: int
    title: str
    author: str


# In-memory storage and auto-incrementing ID counter
books: dict[int, BookResponse] = {}
current_id: int = 0


@app.get("/books", response_model=list[BookResponse], status_code=status.HTTP_200_OK)
def get_books() -> list[BookResponse]:
    return list(books.values())


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate) -> BookResponse:
    global current_id
    current_id += 1
    new_book = BookResponse(
        id=current_id,
        title=book_in.title,
        author=book_in.author,
    )
    books[current_id] = new_book
    return new_book


@app.get("/books/{id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def get_book(id: int = Path(..., gt=0, description="The ID of the book to retrieve")) -> BookResponse:
    book = books.get(id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {id} not found",
        )
    return book


@app.patch("/books/{id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def update_book(
    id: int = Path(..., gt=0, description="The ID of the book to update"),
    book_in: BookUpdate = ...,
) -> BookResponse:
    book = books.get(id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {id} not found",
        )

    update_data = book_in.model_dump(exclude_unset=True)
    if not update_data:
        return book

    updated_book = BookResponse(
        id=book.id,
        title=update_data.get("title", book.title),
        author=update_data.get("author", book.author),
    )
    books[id] = updated_book
    return updated_book


@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int = Path(..., gt=0, description="The ID of the book to delete")) -> None:
    if id not in books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {id} not found",
        )
    del books[id]
    return None
