from datetime import datetime
from uuid import uuid4

import requests
from pydantic_settings import BaseSettings
from bs4 import BeautifulSoup, Tag

from dietz.songs import Attribution, AuthorRole, Author, AuthorType, Song, Melody

class Config(BaseSettings):
    root: str = "https://ugle.dk"

def find_categories(config: Config):
    soup = BeautifulSoup(requests.get(config.root + "/sange.html").content, "html.parser")
    content_table = soup.select("body > table:nth-child(6) > tbody:nth-child(2) > tr:nth-child(1)")[0]
    # Skip first col
    _, *cols =  content_table.find_all("td")
    category_links = [link for col in cols for link in col.find_all("a")]
    print(f"Found {len(category_links)=}")
    return category_links

def find_songs(config: Config, category: Tag):
    soup = BeautifulSoup(
        requests.get(config.root + "/" + category.attrs["href"]).content,
    "html.parser")
    songs = soup.select(".sangliste")[0].find_all("a")
    print(f"{category.text=},{len(songs)=}")
    return songs


def numeral_year(year):
    try:
        return int(year)
    except ValueError:
        print(f"Failed numeral {year=}")
        return None

def get_song(config: Config, category: Tag, song: Tag):
    soup = BeautifulSoup(
        requests.get(config.root + "/" + song.attrs["href"]).content,
    "html.parser")
    head = soup.select(".sanghoved")[0]

    head_parts = head.text.strip().split("\n\t")
    title, author, melody = head_parts


    author = author.strip("Tekst:").strip()
    author, year = author.split(",")

    author = Author(
        author_id=uuid4(),
        name = author.strip(),
        # TODO: Description possible here. Defer with address?
        author_type=AuthorType.UNSPECIFIED_TYPE
    )
    author_attribution = Attribution(
        author.author_id,
        year=numeral_year(year),
        year_string=year.strip(),
        author_role=AuthorRole.PRIMARY,
    )



    melody = melody.strip("Melodi:").strip()
    if "," in melody:
        melody, year = melody.split(",")
        year = year.strip()
        year_numeral = numeral_year(year)
    else:
        year, year_numeral = None, None

    melody_author = Author(
        author_id=uuid4(),
        name=melody.strip(),
        author_type=AuthorType.UNSPECIFIED_TYPE,
    )

    melody_attribution = Attribution(
        melody_author.author_id,
        year=year_numeral,
        year_string=year,
        author_role=AuthorRole.PRIMARY,
    )
    melody = Melody(authorship=[melody_attribution])

    Song(
        song_id=uuid4(),
        created=datetime.now(),
        updated=datetime.now(),
        author_ship=[author_attribution],
        melodies=[melody],
        # TODO
    )



if __name__ == "__main__":
    config = Config()
    for category in find_categories(config):
        for song in find_songs(config, category):
            get_song(config, category, song)
            raise
