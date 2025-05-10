import tempfile
from pathlib import Path
from uuid import UUID

import pytest

from amanuensis import markdown, models

EXPECTED_TEXT = """## Details

- **Title**: Unknown
- **Authors**: Someone
- **Publisher**: Company
- **ISBN**: 111-1-11-111111-1

**Description**

Description...

## Annotations

### Highlight

Highlight_1

### Note

Note_1

---

### Highlight

Highlight_2

---
"""


@pytest.fixture(scope="session")
def annotations() -> frozenset[models.Annotation]:
    return frozenset(
        (
            models.Annotation(
                id=UUID("c1509e71-5cda-4ba5-aa6c-c0b4264efd45"),
                book_id=UUID("3e53cbb0-75a4-474c-a3f4-eac768bc5950"),
                highlight="Highlight_1",
                note="Note_1",
            ),
            models.Annotation(
                id=UUID("d114ecba-2c4d-4f5f-8fbf-0ab48d00b803"),
                book_id=UUID("a9ba76fe-4c5c-48e2-9982-8f147d2f0860"),
                highlight="Highlight_2",
                note="",
            ),
        )
    )


@pytest.fixture(scope="session")
def book(annotations: frozenset[models.Annotation]) -> models.Book:
    return models.Book(
        id=UUID("6cf6802b-7c91-47c2-8ef6-5e1e41be2fc7"),
        title="Unknown",
        authors="Someone",
        description="Description...",
        publisher="Company",
        isbn="111-1-11-111111-1",
        annotations=annotations,
    )


def test_generates_well_formatted_markdown(book: models.Book) -> None:
    with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".md") as file:
        markdown.dump(Path(file.name), book)
        file.seek(0)
        text = file.read()

    assert text == EXPECTED_TEXT
