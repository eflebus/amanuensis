"""Export data using markdown format."""

from functools import singledispatch
from pathlib import Path

from . import models


def dump(path: Path, book: models.Book) -> None:
    """Write book and its annotations as markdown.

    Args:
        path (Path): Output file path.
        book (models.Book): Annotated book.
    """
    with path.open(mode="w", encoding="utf-8") as file:
        file.writelines(
            (
                _markdownify(book),
                "\n\n## Annotations\n\n",
                "\n\n".join(map(_markdownify, book.annotations)),
                "\n",
            )
        )


@singledispatch
def _markdownify(_) -> str: ...


@_markdownify.register
def _(annotation: models.Annotation) -> str:
    paragraphs = [
        f"### Highlight\n\n{annotation.highlight}",
    ]
    if annotation.note:
        paragraphs.append(f"\n### Note\n\n{annotation.note}\n\n---")
    else:
        paragraphs.append("\n---")

    return "\n".join(paragraphs)


@_markdownify.register
def _(book: models.Book) -> str:
    return "\n".join(
        (
            f"## Details\n\n- **Title**: {book.title}",
            f"- **Authors**: {book.authors}",
            f"- **Publisher**: {book.publisher}",
            f"- **ISBN**: {book.isbn}",
            f"\n**Description**\n\n{book.description}",
        )
    )
