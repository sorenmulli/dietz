from datetime import datetime
from enum import StrEnum
from pydantic import UUID4, BaseModel

from .authorship import Attribution, Melody

class SourceType(StrEnum):
    OFFICIAL_HYMNAL = "official-hymnal"
    OFFICIAL_HIGHSCHOOL = "official-highschool"


class Source(BaseModel):
    accessed: datetime
    address: str | None
    description: str | None
    source_type: SourceType

class Song(BaseModel):
    """
    The central class describing one presented song.
    """
    song_id: UUID4
    created: datetime
    updated: datetime

    songbook_ids: list[UUID4]
    """
    Which songbooks does this song belong to?
    Must match an ID for a sonbook
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

    titles: list[str]
    """
    Different candidate tiles.
    First one considered primary
    """

    source: Source
    """
    The source for this song.
    """

    verses: list[str]
    """
    Full lyrics divided into verses
    """

    categories: list[str]
    """
    Categories.
    """

    description: str | None
    """
    Potential details about the song
    """
