from pathlib import Path
from typing import Iterable
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .songs import Author, Song, Songbook
from .generation import  (
    generate_song_pages,
    generate_category_pages,
    generate_author_pages,
    generate_songbook_index,
    generate_global_index,
)


class Config(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)

    input_dir: Path = Field(alias="i")
    """
    Contains
        songbooks.jsonl
        songs.jsonl
        authors.jsonl
    """

    output_dir: Path = Field(alias="o")
    """
    Where to build website to
    """

    song_prefix: str = "sang"

def _jsonl(path: Path) -> Iterable[str]:
    return (
        line for line in path.read_text().splitlines() if line
    )

def run(config: Config):
    authors = [
        Author.model_validate_json(line)
        for line in _jsonl(config.input_dir / "authors.jsonl")
    ]
    songbooks = [
        Songbook.model_validate_json(line)
        for line in _jsonl(config.input_dir / "songbooks.jsonl")

    ]
    songs = [
        Song.model_validate_json(line)
        for line in _jsonl(config.input_dir / "songs.jsonl")
    ]
    print(f"{len(authors)=}, {len(songbooks)=}, {len(songs)=}")

    for songbook in songbooks:
        generate_song_pages(songs, authors, songbook)
        generate_category_pages(songs, authors, songbook)
        generate_author_pages(songs, authors, songbook)
        generate_songbook_index(songs, authors, songbook)
    generate_global_index(songs, authors, songbooks)

if __name__ == "__main__":
    run(Config())
