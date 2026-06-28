from pydantic import UUID4


class Songbook:
    songbook_id: UUID4
    name: str
