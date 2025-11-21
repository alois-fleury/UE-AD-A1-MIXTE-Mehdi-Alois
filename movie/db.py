import json
import os
from pymongo import MongoClient

# Lecture des variables d'environnement
USE_MONGO = os.getenv("USING_MONGO", "false").lower() == "true"
MONGO_URL = os.getenv("DB_URL")

BASE_DIR = os.path.join(os.path.dirname(__file__), "data")
MOVIES_PATH = os.path.join(BASE_DIR, "movies.json")
ACTORS_PATH = os.path.join(BASE_DIR, "actors.json")


# ─────────────────────────────────────────────
#            CHOIX AUTOMATIQUE DB
# ─────────────────────────────────────────────
def get_db():
    if USE_MONGO:
        return DbMongo()
    return DbJson()


# ─────────────────────────────────────────────
#                VERSION JSON
# ─────────────────────────────────────────────
class DbJson:
    def load_movies(self):
        with open(MOVIES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["movies"]

    def load_actors(self):
        with open(ACTORS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["actors"]

    def write_movies(self, movies):
        with open(MOVIES_PATH, "w", encoding="utf-8") as f:
            json.dump({"movies": movies}, f, indent=2)

    def write_actors(self, actors):
        with open(ACTORS_PATH, "w", encoding="utf-8") as f:
            json.dump({"actors": actors}, f, indent=2)


# ─────────────────────────────────────────────
#                VERSION MONGO
# ─────────────────────────────────────────────
class DbMongo:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client.get_database()

        self.movies = self.db["movies"]
        self.actors = self.db["actors"]

        # Initialisation si base vide
        if self.movies.count_documents({}) == 0:
            json_movies = DbJson().load_movies()
            self.movies.insert_many(json_movies)

        if self.actors.count_documents({}) == 0:
            json_actors = DbJson().load_actors()
            self.actors.insert_many(json_actors)

    def load_movies(self):
        return list(self.movies.find({}, {"_id": 0}))

    def load_actors(self):
        return list(self.actors.find({}, {"_id": 0}))

    def write_movies(self, movies):
        self.movies.delete_many({})
        if movies:
            self.movies.insert_many(movies)

    def write_actors(self, actors):
        self.actors.delete_many({})
        if actors:
            self.actors.insert_many(actors)


# ─────────────────────────────────────────────
#       MÉTHODES SIMPLES À IMPORTER
# ─────────────────────────────────────────────
_db = get_db()

def load_movies():
    return _db.load_movies()

def load_actors():
    return _db.load_actors()

def write_movies(movies):
    _db.write_movies(movies)

def write_actors(actors):
    _db.write_actors(actors)
