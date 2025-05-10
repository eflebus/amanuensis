"""Database operations."""

import re
import sqlite3
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

from . import models

_ANNOTATIONS_QUERY = " ".join(
    (
        "SELECT BookmarkID, VolumeID, Text, Annotation",
        "FROM Bookmark",
        'WHERE Type in ("highlight", "note")',
    )
)
_BOOKS_QUERY = " ".join(
    (
        "SELECT ContentID, Title, Attribution, Description, Publisher, ISBN",
        "FROM content",
        "WHERE ContentID == ?",
    )
)


def read_annotated_books(db_path: Path | str) -> frozenset[models.Book]:
    """Read books and their annotations from the eReader's database.

    Args:
        db_path (Path | str): SQLite database path.

    Returns:
        frozenset[models.Book]: Annotated books.
    """
    with _open_db(db_path) as cursor:
        return _read_annotated_books(cursor)


@contextmanager
def _open_db(path: Path | str) -> Iterator[sqlite3.Cursor]:
    db = sqlite3.connect(path)
    cursor = db.cursor()
    yield cursor
    db.commit()
    cursor.close()
    db.close()


def _read_annotated_books(cursor: sqlite3.Cursor) -> frozenset[models.Book]:
    annotations = _read_annotations(cursor)

    return _read_books(
        cursor, annotations_by_book_id=_group_annotations_by_book_id(annotations)
    )


def _read_annotations(cursor: sqlite3.Cursor) -> set[models.Annotation]:
    return {
        models.Annotation(
            id=UUID(row[0]),
            book_id=UUID(row[1]),
            highlight=_clean_text(row[2], replace_pattern=r"\s+", with_this=" "),
            note=_clean_text(row[3] or "", replace_pattern=r"\s+", with_this=" "),
        )
        for row in cursor.execute(_ANNOTATIONS_QUERY).fetchall()
    }


def _read_books(
    cursor: sqlite3.Cursor, annotations_by_book_id: dict[UUID, set[models.Annotation]]
) -> frozenset[models.Book]:
    return frozenset(
        models.Book(
            id=UUID(row[0]),
            title=_clean_text(row[1], replace_pattern=r"\(.*\)", with_this=""),
            authors=row[2],
            description=_clean_text(row[3], replace_pattern=r"<.*?>", with_this=""),
            publisher=row[4],
            isbn=row[5],
            annotations=frozenset(book_annotations),
        )
        for book_id, book_annotations in annotations_by_book_id.items()
        if (row := cursor.execute(_BOOKS_QUERY, (str(book_id),)).fetchone()) is not None
    )


def _group_annotations_by_book_id(
    annotations: set[models.Annotation],
) -> dict[UUID, set[models.Annotation]]:
    annotations_per_book: dict[UUID, set[models.Annotation]] = defaultdict(set)

    for annotation in annotations:
        annotations_per_book[annotation.book_id].add(annotation)

    return annotations_per_book


def _clean_text(text: str, /, replace_pattern: str, with_this: str) -> str:
    return re.sub(replace_pattern, with_this, text).strip()
