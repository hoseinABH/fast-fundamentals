from pydantic import field_validator
from datetime import date
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class GenreChoices(Enum):
    ROCK = "Rock"
    ELECTRONIC = "Electronic"
    METAL = "Metal"
    HIP_HOP = "Hip-Hop"
    Pop = "POP"


class AlbumBase(SQLModel):
    title: str
    release_date: date
    band_id: int | None = Field(foreign_key="band.id")


class Album(AlbumBase, table=True):
    id: int = Field(default=None, primary_key=True)
    band: "Band" = Relationship(back_populates="albums")


class BandBase(SQLModel):
    name: str
    genre: GenreChoices


class AlbumCreate(SQLModel):
    title: str
    release_date: date


class BandCreate(BandBase):
    albums: list[AlbumCreate] | None = None

    @field_validator("genre", mode="before")
    @classmethod
    def normalize_genre(cls, v: str):
        v = v.strip().title()
        return GenreChoices(v)


class Band(BandBase, table=True):
    id: int = Field(default=None, primary_key=True)
    albums: list[Album] = Relationship(back_populates="band")
