"""Data stored in the Kobo's database."""

import dataclasses
from uuid import UUID


@dataclasses.dataclass(frozen=True, slots=True)
class Annotation:
    """Annotation data.

    Attributes:
        id (UUID): Identifier (version 4).
        book_id (UUID): Book identifier (version 4).
        highlight (str): Highlighted text.
        note (str): User note.
    """

    id: UUID
    book_id: UUID = dataclasses.field(compare=False)
    highlight: str = dataclasses.field(repr=False, compare=False)
    note: str = dataclasses.field(repr=False, compare=False)


@dataclasses.dataclass(frozen=True, slots=True)
class Book:
    """Book data.

    Attributes:
        id (UUID): Identifier (version 4).
        title (str): Title.
        authors (str): Authors.
        description (str): Short description.
        publisher (str): Publisher.
        isbn (str): ISBN code.
        annotations (frozenset[Annotation]): User annotations.
    """

    id: UUID
    title: str = dataclasses.field(compare=False)
    authors: str = dataclasses.field(compare=False)
    description: str = dataclasses.field(repr=False, compare=False)
    publisher: str = dataclasses.field(compare=False)
    isbn: str
    annotations: frozenset[Annotation]
