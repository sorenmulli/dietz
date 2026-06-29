from enum import StrEnum
from pydantic import UUID4, BaseModel


class AuthorType(StrEnum):
    NAMED_AUTHOR = "named-author"
    BIBLICAL = "biblical"
    FOLK = "folk"
    NATIONALITY = "nationality"
    UNSPECIFIED_TYPE = "unspecified-type"

class Author(BaseModel):
    name: str
    author_type: AuthorType
    description: str | None
    author_id: UUID4

    # TODO: Indication of whether text author or melody composer or both?


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


class Melody(BaseModel):
    authorship: list[Attribution]
