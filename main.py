from subprocess import run

import mongoengine
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.on_event("startup")
def start_mongo():
    run(["docker-compose", "up", "-d"])
    mongoengine.connect()


@app.on_event("shutdown")
def start_mongo():
    mongoengine.disconnect()
    run(["docker-compose", "down"])


class WordSchema(BaseModel):
    name: str
    description: str
    uses: list[str]


class Word(mongoengine.Document):
    name = mongoengine.StringField(unique=True, required=True)
    description = mongoengine.StringField(required=True)
    uses = mongoengine.ListField(mongoengine.StringField(required=True))


@app.post("/add_word")
async def add_word(word: WordSchema):
    try:
        Word(**word.dict()).save()
    except Exception as e:
        return str(e)
    return "ok"


@app.get("/get_word")
async def get_word(name: str):
    return WordSchema(**Word.objects(name__exact=name).first().to_mongo())


@app.get("/get_words")
async def get_words():
    return [WordSchema(**word.to_mongo()) for word in Word.objects]
