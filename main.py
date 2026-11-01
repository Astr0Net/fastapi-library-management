from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from settings import settings


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(300), nullable=False)


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    with SessionLocal() as db:
        yield db


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Library Management API", lifespan=lifespan)


class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    author: str

    @field_validator("title", "author", mode="before")
    @classmethod
    def validate_non_empty_string(cls, value: Any, info) -> str:
        if value is None:
            raise ValueError(f"{info.field_name} cannot be null")
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a string")
        value = value.strip()
        if not value:
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return value


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = None
    author: str | None = None

    @field_validator("title", "author", mode="before")
    @classmethod
    def validate_non_empty_string(cls, value: Any, info) -> str:
        if value is None:
            raise ValueError(f"{info.field_name} cannot be null")
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a string")
        value = value.strip()
        if not value:
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return value


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    author: str


@app.get("/books", response_model=list[BookResponse], status_code=status.HTTP_200_OK)
def get_books(db: Session = Depends(get_db)) -> list[Book]:
    return list(db.scalars(select(Book).order_by(Book.id)).all())


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)) -> Book:
    book = Book(title=book_in.title, author=book_in.author)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def find_book(book_id: int, db: Session) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
    return book


@app.get("/books/{id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def get_book(id: int = Path(..., gt=0, description="The ID of the book to retrieve"), db: Session = Depends(get_db)) -> Book:
    return find_book(id, db)


@app.patch("/books/{id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def update_book(id: int = Path(..., gt=0, description="The ID of the book to update"), book_in: BookUpdate = ..., db: Session = Depends(get_db)) -> Book:
    book = find_book(id, db)
    for field, value in book_in.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int = Path(..., gt=0, description="The ID of the book to delete"), db: Session = Depends(get_db)) -> None:
    book = find_book(id, db)
    db.delete(book)
    db.commit()
