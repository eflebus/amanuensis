import argparse
import dataclasses
import logging
import shutil
import sys
import tempfile
from pathlib import Path

from . import __version__, db, markdown

HELP_DESCRIPTION = """Export highlights and notes from your Kobo eReader as markdown.

A markdown file is written for each book, containing all its annotations.
Data is read from a temporary copy of the Kobo database.
"""

logging.basicConfig()
logger = logging.getLogger(__package__)
logger.setLevel(logging.INFO)


@dataclasses.dataclass
class Args:
    output_dir_path: Path
    db_path: Path


def _main(args: Args) -> None:
    with tempfile.NamedTemporaryFile() as file:
        tmp_db_path = Path(file.name)
        shutil.copy(src=args.db_path, dst=tmp_db_path)
        logger.info("Reading annotations from database")
        annotated_books = db.read_annotated_books(tmp_db_path)

    logger.info("Found %d books with annotations", len(annotated_books))
    logger.info("Saving annotations to '%s'", args.output_dir_path)

    args.output_dir_path.mkdir(parents=True, exist_ok=True)
    for book in annotated_books:
        logger.info("Book '%s', %d annotations", book.title, len(book.annotations))
        filename = f"{book.title.lower().replace(' ', '_')}.md"
        markdown.dump(args.output_dir_path / filename, book)


def _parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog=__package__,
        description=HELP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("outputdir", type=Path, help="output directory")
    parser.add_argument("dbpath", type=Path, help="Kobo SQLite database")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    args = parser.parse_args()

    return Args(args.outputdir, args.dbpath)


def main() -> None:
    args = _parse_args()
    try:
        _main(args)
    except Exception as exc:
        logger.error("An unexpected error occurred (%s)", exc)
        logger.info("Removing directory '%s'", args.output_dir_path)
        shutil.rmtree(args.output_dir_path, ignore_errors=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
