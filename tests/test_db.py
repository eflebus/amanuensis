import sqlite3
from collections.abc import Iterator

import pytest

from amanuensis import db


@pytest.fixture(scope="session")
def books_table_data() -> list[dict[str, str]]:
    return [
        {
            "ContentID": "3e7608b9-1025-40b6-9be0-b32fa2f45f5a",
            "Title": "Title_1",
            "Attribution": "Author_1",
            "Description": "Description_1",
            "Publisher": "Publisher_1",
            "ISBN": "111-1-11-111111-1",
        },
        {
            "ContentID": "151932c6-2857-47bb-8867-6e5e4e13eae6",
            "Title": "Title_2",
            "Attribution": "Author_2",
            "Description": "Description_2",
            "Publisher": "Publisher_2",
            "ISBN": "222-2-22-222222-2",
        },
        {
            "ContentID": "253f1384-0327-440d-bc0c-e3b96268b72c",
            "Title": "Title_3",
            "Attribution": "Author_3",
            "Description": "Description_3",
            "Publisher": "Publisher_3",
            "ISBN": "333-3-33-333333-3",
        },
    ]


@pytest.fixture(scope="session")
def annotations_table_data() -> list[dict[str, str]]:
    return [
        {
            "BookmarkID": "b5c0cb0c-f180-4d52-8367-2157fd04a3e7",
            "VolumeID": "3e7608b9-1025-40b6-9be0-b32fa2f45f5a",
            "Text": "Text_1",
            "Annotation": "Annotation_1",
            "Type": "note",
        },
        {
            "BookmarkID": "e3382e47-0fb5-4e37-abde-b99826ba11d8",
            "VolumeID": "151932c6-2857-47bb-8867-6e5e4e13eae6",
            "Text": "Text_2",
            "Annotation": "Annotation_2",
            "Type": "highlight",
        },
        {
            "BookmarkID": "b4651f1d-ab6b-406f-993f-a3e8c2ed7dee",
            "VolumeID": "3e7608b9-1025-40b6-9be0-b32fa2f45f5a",
            "Text": "Text_3",
            "Annotation": "Annotation_3",
            "Type": "highlight",
        },
        {
            "BookmarkID": "4df2ce82-fd1d-4ac4-89d6-ff70a00ccc96",
            "VolumeID": "151932c6-2857-47bb-8867-6e5e4e13eae6",
            "Text": "Text_4",
            "Annotation": "Annotation_4",
            "Type": "other",
        },
    ]


@pytest.fixture(scope="session")
def db_cursor(
    books_table_data: list[dict[str, str]], annotations_table_data: list[dict[str, str]]
) -> Iterator[sqlite3.Cursor]:
    with db._open_db(":memory:") as cursor:
        cursor.execute(
            "CREATE TABLE content(ContentID, Title, Attribution, Description, Publisher, ISBN)"
        )
        cursor.execute(
            "CREATE TABLE Bookmark(BookmarkID, VolumeID, Text, Annotation, Type)"
        )

        cursor.executemany(
            "INSERT INTO content VALUES(:ContentID, :Title, :Attribution, :Description, :Publisher, :ISBN)",
            books_table_data,
        )
        cursor.executemany(
            "INSERT INTO Bookmark VALUES(:BookmarkID, :VolumeID, :Text, :Annotation, :Type)",
            annotations_table_data,
        )

        yield cursor


def test_db_query_selects_annotations_with_type_highlight_or_note(
    db_cursor: sqlite3.Cursor, annotations_table_data: list[dict[str, str]]
) -> None:
    expected_selected_ids = {
        annotation["BookmarkID"] for annotation in annotations_table_data[:-1]
    }
    expected_excluded_id = annotations_table_data[-1]["BookmarkID"]

    annotations = db._read_annotations(db_cursor)
    ids = {str(annotation.id) for annotation in annotations}

    assert len(ids) == 3
    assert ids == expected_selected_ids
    assert expected_excluded_id not in ids


def test_db_query_selects_books_with_at_least_one_annotation(
    db_cursor: sqlite3.Cursor, books_table_data: list[dict[str, str]]
) -> None:
    expected_selected_ids = {item["ContentID"] for item in books_table_data[:-1]}
    expected_discarded_id = books_table_data[-1]["ContentID"]

    books = db._read_annotated_books(db_cursor)
    ids = {str(book.id) for book in books}

    assert len(books) == 2
    assert ids == expected_selected_ids
    assert expected_discarded_id not in ids


def test_annotations_of_the_same_book_are_grouped_together(
    db_cursor: sqlite3.Cursor, books_table_data: list[dict[str, str]]
) -> None:
    expected_selected_books_id = (
        "3e7608b9-1025-40b6-9be0-b32fa2f45f5a",
        "151932c6-2857-47bb-8867-6e5e4e13eae6",
    )
    expected_discarded_book_id = books_table_data[-1]["ContentID"]

    books = db._read_annotated_books(db_cursor)
    annotations_by_book_id = {str(book.id): book.annotations for book in books}

    assert len(books) == 2
    assert expected_discarded_book_id not in annotations_by_book_id
    assert len(annotations_by_book_id[expected_selected_books_id[0]]) == 2
    assert len(annotations_by_book_id[expected_selected_books_id[1]]) == 1
    for book in books:
        assert all(annotation.book_id == book.id for annotation in book.annotations)
