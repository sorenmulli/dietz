from enum import StrEnum
from pydantic import UUID4, BaseModel


class Author(BaseModel):
    author_id: UUID4
    name: str
    description: str | None


class AuthorRole(StrEnum):
    PRIMARY = "primary"
    UNSPECIFIED = "unspecified"
    EDITOR = "editor"


class Attribution(BaseModel):
    author_id: UUID4
    """
    Must match id of an existing Author
    """
    year: int | None
    """If possible, when composition happened"""
    year_string: str | None
    """If something else should be presented than just year"""
    author_role: AuthorRole


class Melody(BaseModel):
    authorship: list[Attribution]
