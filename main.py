from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Path
from sqlmodel import Session, select

from typing import Annotated, Sequence

from db import get_session, init_db
from models import Band, BandCreate, Album, GenreChoices


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/bands", name="Get All Bands")
async def getBands(
    genre: GenreChoices | None = None,
    has_album: bool = False,
    session: Session = Depends(get_session),
) -> Sequence[Band]:
    bands_list = session.exec(select(Band)).all()
    if genre:
        bands_list = [b for b in bands_list if b.genre.value == genre.value]
    if has_album:
        bands_list = [b for b in bands_list if len(b.albums) > 0]
    return bands_list


@app.get("/bands/{band_id}", name="Get Band By ID")
async def getBand(
    band_id: Annotated[int, Path(title="The band ID")],
    session: Session = Depends(get_session),
) -> Band:
    band = session.get(Band, band_id)
    if band is None:
        raise HTTPException(
            status_code=404, detail=f"Band with id {band_id} not found!"
        )
    return band


# @app.get("/bands/genre/{genre}", name="Get Bands Filtered By Genre")
# async def bands_for_genre(genre: str) -> list[Band]:
#     return [Band(**b) for b in BANDS if b["genre"].lower() == genre.lower()]


@app.post("/bands", name="Create New Band")
async def create_band(
    band_data: BandCreate, session: Session = Depends(get_session)
) -> Band:
    band = Band(name=band_data.name, genre=band_data.genre)
    session.add(band)

    if band_data.albums:
        for album in band_data.albums:
            album_obj = Album(
                title=album.title,
                release_date=album.release_date,
                band=band,
                band_id=band.id,
            )
        session.add(album_obj)

    session.commit()
    session.refresh(band)

    return band
