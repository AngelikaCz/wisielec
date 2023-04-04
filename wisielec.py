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

categories = db.Table('Categories', metadata,
                      db.Column('id', db.Integer(), primary_key=True, autoincrement=True),
                      db.Column('name', db.String(60), nullable=False),
                      db.Column('description', db.String(100), nullable=False)
                      )

metadata.create_all(engine)