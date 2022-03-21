from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from http.client import HTTPException
from pydantic import BaseModel
from typing import Optional


app = FastAPI()
id_count = 0
films_db = {}


class Film(BaseModel):
    title: str
    director: str
    poster: Optional[str]


class FilmUpdate(BaseModel):
    title: Optional[str]
    director: Optional[str]
    poster: Optional[str]


def error(id: int):
    return JSONResponse(
        status_code=404,
        content={
            "error": f"Film with id {id} not found"
        }
    )


@app.get("/films")
def get_all_films():
    return {
        "message": "Get all films success",
        "data": films_db
    }


@app.get("/films/{id}")
def get_film_by_id(id: int):
    if id not in films_db.keys():
        return error(id)

    return {
        "message": f"Get film with id {id} success",
        "data": films_db[id]
    }


@app.post("/films")
def post_film(film: Film):
    global id_count
    id_count += 1

    data = {"id": id_count}
    data = {**data, **dict(film)}

    data["poster"] = None
    films_db[id_count] = data

    return {
        "message": "Film added successfully",
        "data": data
    }


@app.put("/films/{id}")
def update_film(id: int, film_update: FilmUpdate):
    if id not in films_db.keys():
        return error(id)

    film = dict(film_update)
    for key in film.keys():
        if film[key]:
            films_db[id][key] = film[key]

    return {
        "message": f"Update film with id {id} success",
        "data": films_db[id]
    }


@app.put("/films/{id}/image")
def update_film_with_image(id: int, img: UploadFile = File(...)):
    if id not in films_db.keys():
        return error(id)

    if img.content_type not in ["image/png", "image/jpg", "image.jpeg"]:
        raise HTTPException(400, detail="Invalid file format")

    with open(f"images/{img.filename}", "wb") as file:
        file.write(img.file.read())

    global id_count
    films_db[id_count]["poster"] = img.filename

    return {
        "message": "Image uploaded successfully",
        "data": films_db[id_count]
    }


@app.delete("/films/{id}")
def delete_film(id: int):
    if id not in films_db.keys():
        return error(id)

    del films_db[id]
    return {"message": f"Delete film with id {id} success"}
