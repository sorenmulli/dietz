from enum import StrEnum
from pydantic import UUID4, BaseModel


class AuthorType(StrEnum):
    NAMED_AUTHOR = "named-author"
    BIBLICAL = "biblical"
    FOLK = "folk"
    UNSPECIFIED_TYPE = "unspecified-type"
    UNKNOWN = "unknown"

class Author(BaseModel):
    name: str | None
    author_type: AuthorType
    description: str | None
    author_id: UUID4

    composer: bool
    writer: bool


class AuthorRole(StrEnum):
    PRIMARY = "primary"
    UNSPECIFIED = "unspecified"
    EDITOR = "editor"


class Attribution(BaseModel):
    year: int | None
    """If possible, when composition happened"""
    year_string: str | None
    """If something else should be presented than just year"""
    author_role: AuthorRole
    author_id: UUID4
    """
    Must match id of an existing Author
    """
    comment: str | None = None


class Melody(BaseModel):
    authorship: list[Attribution]
