from datetime import datetime
from enum import StrEnum
from pydantic import UUID4, BaseModel

from .authorship import Attribution, Melody

class SourceType(StrEnum):
    OFFICIAL_HYMNAL = "official-hymnal"
    OFFICIAL_HIGHSCHOOL = "official-highschool"
    UNOFFICIAL_CATALOGUE = "unofficial-catalogue"
    INDIVIDUAL_CONTRIBUTION = "individual-contribution"


class Source(BaseModel):
    name: str
    accessed: datetime
    address: str | None
    description: str | None
    source_type: SourceType
    comment: str | None

class Song(BaseModel):
    """
    The central class describing one presented song.
    """

    songbook_ids: list[UUID4]
    """
    Which songbooks does this song belong to?
    Must match an ID for a sonbook
    """

    titles: list[str]
    """
    Different candidate tiles.
    First one considered primary
    """

    categories: list[str]
    """
    Categories.
    """

    authorship: list[Attribution]
    """
    Authorship as potentially multiple attributions.
    """

    melodies: list[Melody]
    """
    Different candidate melodies.
    First one is considered primary
    """


    sources: list[Source]
    """
    The source(s) for this song.
    """


    verses: list[str]
    """
    Full lyrics divided into verses
    """

    description: str | None
    """
    Potential details about the song
    """

    song_id: UUID4
    created: datetime
    updated: datetime
