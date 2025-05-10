# Amanuensis

Export highlights and notes from your Kobo eReader as markdown.

## Usage

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Connect the Kobo eReader to your PC via USB.
3. Run the command `uv run --no-dev amanuensis /path/to/output/dir /path/to/mounted/volume/.kobo/KoboReader.sqlite`.

Example:

```bash
uv run --no-dev amanuensis ~/Downloads/my_kobo_annotations /media/ema/KOBOeReader/.kobo/KoboReader.sqlite
```

Run `uv run --no-dev amanuensis -h` to display the help.

Python 3.10+ is supported.

## Tests

Run the command `uv run --python 3.x coverage run -m pytest`.

## Acknowledgments

Inspired by [export-kobo](https://github.com/pettarin/export-kobo) (read this [article](https://www.albertopettarin.it/exportnotes.html) for further details).

## Resources

- Useful [article](https://shallowsky.com/blog/tech/kobo-hacking.html) exploring Kobo's database.
