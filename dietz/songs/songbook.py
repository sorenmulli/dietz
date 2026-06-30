from pydantic import BaseModel, UUID4


class Songbook(BaseModel):
    songbook_id: UUID4
    name: str
