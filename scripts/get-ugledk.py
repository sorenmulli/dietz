from datetime import datetime
from uuid import UUID, uuid4
from pathlib import Path

import requests
from pydantic_settings import BaseSettings
from bs4 import BeautifulSoup, Tag

from dietz.songs import (
    Attribution,
    AuthorRole,
    Author,
    AuthorType,
    Song,
    Melody,
    Source,
    SourceType,
)

NOW = datetime.now()

# TODO: Handle "omkring"
# TODO: Handle "-tallet"
# TODO: Handle "årh."

class Config(BaseSettings):
    root: str = "https://ugle.dk"
    source_name: str = "Jørgen Ebert, ugle.dk"
    out_dir: Path = Path("./local-data/ugledk-raw")
    version_name: str = NOW.isoformat().split("T")[0]

def find_categories(config: Config):
    soup = BeautifulSoup(requests.get(config.root + "/sange.html").content, "html.parser")
    content_table = soup.select_one("body > table:nth-child(6) > tbody:nth-child(2) > tr:nth-child(1)")
    assert content_table is not None
    # Skip first col
    _, *cols =  content_table.find_all("td")
    category_links = [link for col in cols for link in col.find_all("a")]
    print(f"Found {len(category_links)=}")
    return category_links

def find_songs(config: Config, category: Tag):
    soup = BeautifulSoup(
        requests.get(config.root + "/" + category.attrs["href"]).content,
    "html.parser")
    songlist = soup.select_one(".sangliste")
    assert songlist is not None
    songs = songlist.find_all("a")
    print(f"{category.text=},{len(songs)=}")
    return songs


def handle_author_year(author: str) -> tuple[str, int | None, str, None] | tuple[str, None, None,  str | None]:
    if "," in author:
        author_name, year = author.split(",")
        if not any(c.isnumeric() for c in year):
            print(f"Non-numeric year candidate {year=}")
            return author.strip(), None, None, year.strip()
        try:
            numeral_year = int(year.replace("ca.", "").strip())
        except ValueError:
            numeral_year = None
            print(f"Failed numeral {year=}")
        return author_name.strip(), numeral_year, year.strip(), None
    print(f"No year, {author=}")
    return author.strip(), None, None, None

def parse_author(author_str: str) -> tuple[Author, Attribution]:
    author_str = author_str.replace("Tekst:","").strip()
    author, year, year_string, attribution_comment = handle_author_year(author_str)

    author = Author(
        author_id=uuid4(),
        name=author,
        author_type=AuthorType.UNSPECIFIED_TYPE,
        # TODO: Description possible here. Defer with address?
        description=None,
        composer=False,
        writer=True,
    )
    author_attribution = Attribution(
        author_id=author.author_id,
        year=year,
        year_string=year_string,
        author_role=AuthorRole.PRIMARY,
        comment = attribution_comment,
    )

    modify_author(author, author_attribution)
    return author, author_attribution

def parse_melody(melody_str: str) -> tuple[Author, Melody]:
    melody = melody_str.replace("Melodi:","").strip()
    melody, year, year_string, attribution_comment = handle_author_year(melody)

    melody_author = Author(
        author_id=uuid4(),
        name=melody.strip(),
        author_type=AuthorType.UNSPECIFIED_TYPE,
        # TODO: Description possible?
        description=None,
        writer=False,
        composer=True,
    )

    melody_attribution = Attribution(
        author_id=melody_author.author_id,
        year=year,
        year_string=year_string,
        author_role=AuthorRole.PRIMARY,
        comment=attribution_comment,
    )
    modify_author(melody_author, melody_attribution)
    return melody_author, Melody(authorship=[melody_attribution])



def modify_author(author: Author, attribution: Attribution):
    if author.name == "?":
        author.name = None
        author.author_type = AuthorType.UNKNOWN
    elif author.name and (
        "folke" in author.name.lower() or
        "gammel" in author.name.lower()
    ):
        if author.name.lower().strip() not in {"folkevise", "folkemelodi"}:
            if not attribution.comment:
                attribution.comment = author.name
        author.name = None
        author.author_type = AuthorType.FOLK
    else:
        author.author_type = AuthorType.NAMED_AUTHOR


def construct_source(config: Config, song: Tag) -> Source:
    return Source(
        name=config.source_name,
        accessed=NOW,
        address=config.root + "/" + song.attrs["href"],
        source_type=SourceType.UNOFFICIAL_CATALOGUE,
        description=None,
        comment=None,
    )

def parse_song(lyrics: Tag):
    return lyrics.text.replace("\t", "").strip().split("\n\n")

def parse_description(note: Tag | None) -> str | None:
    if note is None:
        return None
    return note.text.strip()

def get_song(config: Config, category: Tag, song: Tag) -> tuple[Song, list[Author]]:
    print(f"\t{song.text=}...")
    soup = BeautifulSoup(
        requests.get(config.root + "/" + song.attrs["href"]).content,
    "html.parser")
    head = soup.select_one(".sanghoved")
    assert head is not None

    head_parts = head.text.strip().split("\n\t")
    title_str, author_str, melody_str = head_parts
    author, author_attribution = parse_author(author_str)
    melody_author, melody = parse_melody(melody_str)

    body = soup.select_one(".sangtekst")
    assert body is not None

    song = Song(
        song_id=uuid4(),
        created=datetime.now(),
        updated=datetime.now(),
        authorship=[author_attribution],
        melodies=[melody],
        titles=[title_str],
        sources=[construct_source(config, song)],
        verses=parse_song(body),
        categories=[category.text],
        description=parse_description(soup.select_one(".sangnote")),
        songbook_ids=[],
    )

    return song, [author, melody_author]


def merge_authors(authors: list[Author], songs: list[Song]) -> tuple[list[Author], list[Song]]:
    out_authors: dict[tuple[str | None, AuthorType], Author] = {}
    to_update: dict[UUID, UUID] = {}
    for author in authors:
        if (key := (author.name, author.author_type)) not in out_authors:
            out_authors[key] = author
            continue
        first_author = out_authors[key]
        if first_author.description != author.description:
            print(f"Differing description for\n{first_author=}\n{author=}")
        if author.writer:
            first_author.writer = True
        if author.composer:
            first_author.composer = True
        to_update[author.author_id] = first_author.author_id
    for song in songs:
        for attribution in song.authorship:
            if attribution.author_id in to_update:
                attribution.author_id = to_update[attribution.author_id]
    return list(out_authors.values()), songs

def merge_songs(songs: list[Song]) -> list[Song]:
    named_songs = {song.titles[0]: song for song in songs}
    for song in songs:
        if "(1)" not in song.title: continue
        matches = [
            named_songs[candidate]
            for i in range(2, 9)
            if (candidate := song.title.replace("(1)", f"({i})")) in named_songs
        ]
        for match in matches:
            assert song.authorship[0].author_id == match.authorship[0].author_id
            song.melodies.extend(match.melodies)
            named_songs.pop(match.title)
            song.titles = [song.title.replace("(1)", "").strip()]
            print(f"Removed {match.title=}, merged with {song.title=}")
    return list(named_songs.values())

if __name__ == "__main__":
    config = Config()
    (out_dir := config.out_dir / config.version_name).mkdir(
        parents=True,
        exist_ok=True,
    )

    all_songs: list[Song] = []
    all_authors: list[Author] = []
    for category in find_categories(config):
        # TODO: Remove and generate full
        if not "Aften" in category.text:
            continue

        for song in find_songs(config, category):
            out_song, authors = get_song(config, category, song)
            all_songs.append(out_song)
            all_authors.extend(authors)

    authors, songs = merge_authors(all_authors, all_songs)
    songs = merge_songs(all_songs)
    (song_out_path := out_dir / "songs.jsonl").write_text("\n".join(
        song.model_dump_json() for song in songs
    ))
    (authors_out_path := out_dir / "authors.jsonl").write_text("\n".join(
        author.model_dump_json() for author in authors
    ))


    print(f"Wrote to\n{str(song_out_path)}\n{str(authors_out_path)}")
