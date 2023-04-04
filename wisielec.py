from fastapi import Request, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import sqlalchemy as db
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = db.create_engine('sqlite:///wisielec.db', connect_args={"check_same_thread": False})

connection = engine.connect()

metadata = db.MetaData()

# Definition of creating new tables
categories = db.Table('Categories', metadata,
                      db.Column('id', db.Integer(), primary_key=True, autoincrement=True),
                      db.Column('name', db.String(60), nullable=False),
                      db.Column('description', db.String(100), nullable=False)
                      )

#
words = db.Table('Words', metadata,
                    db.Column('id', db.Integer(), primary_key=True, autoincrement=True),
                    db.Column('category_id', db.Integer(),nullable=False),
                    db.Column('words', db.String(100), nullable=False))

# Wykonujemy tworzenie tabel:

metadata.create_all(engine)

# Tworzymy getowy endpoint category do pobierania kategorii

@app.get("/categories")
def get_categories():
    try:
        query = db.select(categories)
        result= connection.execute(query).fetchall()
        return result
    except Exception as error:
        print(error)
        return {"status": "failed"}

# Tworzymy getowy endpoint do pobierania pojedynczej kategorii po id

@app.get("/categories/{id}")
def get_categories_by_ids(id:int):
    try:
        query=db.select(categories).where(categories.columns.id==id)
        result= connection.execute(query).fetchall()
        return result
    except Exception as error:
        print(error)
        return {"status": "failed"}

# Tworzymy postowy endpoint do dodawania kategorii + dodane query do dodania kategorii

@app.post("/categories")
async def post_categories(request: Request):
    try:
        parsed_json = json.loads (await request.body())
        name=parsed_json["name"]
        description=parsed_json["description"]

        query= db.insert(categories).values(name=name, description=description)
        connection.execute(query)

        print(name, description)
        return {"status": "done"}
    except Exception as error:
        print(error)
        return {"status": "failed"}

# Tworzymy postowy endpoint do dodawania nowego słowa w grze

@app.post("/words")
async def add_words(request: Request):
    try:
        parsed_json = json.loads (await request.body())
        word_name=parsed_json["name"]
        category_id=parsed_json["category_id"]
        print(word_name, category_id)
        query=db.select(categories).where(categories.columns.id==category_id)
        result = connection.execute(query).fetchall()
        if not result:
            return {"status": "failed", "info": "No such categories with this id can not add this word"}
        query=db.insert(words).values(category_id=category_id, words=word_name)
        connection.execute(query)
        return {"status": 'done'}
    except Exception as error:
        print(error)
        return {"status": "failed"}

# Tworzymy getowy endpoint do pobrania losowego słowa z bazy

from  sqlalchemy.sql.expression import func, select

@app.get("/words/random")
def get_words_random():
    try:
        query = db.select(words).order_by(func.random()).limit(1)
        result = connection.execute(query).fetchone()
        print(result)
        cat = result["category_id"]
        query2 = db.select(categories).where(categories.columns.id == cat)
        result2 = connection.execute(query2).fetchone()
        response = {"name": result["name"], "id": result["id"], "category": result2}
        return response
    except Exception as error:
        print(error)
        return {'status': 'failed'}


