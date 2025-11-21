import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

USING_MONGO = os.getenv("USING_MONGO", "false").lower() == "true"
MONGO_URL = os.getenv("DB_URL")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "times.json")


def get_schedule_db():
    """Retourne automatiquement la DB JSON ou Mongo selon l'environnement."""
    if USING_MONGO:
        return MongoScheduleDB()
    return JsonScheduleDB()


# -----------------------------
# JSON IMPLEMENTATION
# -----------------------------
class JsonScheduleDB:
    def load(self):
        """Charge toutes les entrées depuis times.json."""
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["schedule"]

    def write(self, schedule):
        """Écrase totalement le fichier JSON avec la nouvelle liste."""
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump({"schedule": schedule}, f, indent=2)


# -----------------------------
# MONGO IMPLEMENTATION
# -----------------------------
class MongoScheduleDB:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client.get_database()
        self.collection = self.db["schedule"]

        # Si la collection est vide, on la remplit depuis le JSON
        if self.collection.count_documents({}) == 0:
            js = JsonScheduleDB()
            initial = js.load()
            if initial:
                self.collection.insert_many(initial)

    def load(self):
        """Récupère tous les documents Mongo (sans _id)."""
        return list(self.collection.find({}, {"_id": 0}))

    def write(self, schedule):
        """Supprime tout et réinsère entièrement la planification."""
        self.collection.delete_many({})
        if schedule:
            self.collection.insert_many(schedule)
