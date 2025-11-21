import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.join(os.path.dirname(__file__), "data")
BOOKING_FILE = os.path.join(BASE_DIR, "bookings.json")

USING_MONGO = os.getenv("USING_MONGO", "false").lower() == "true"
MONGO_URL = os.getenv("DB_URL")


# ---------------------------------------------------------
#   VERSION JSON
# ---------------------------------------------------------
class DbJsonBooking:
    def load(self):
        with open(BOOKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)["bookings"]

    def write(self, bookings):
        with open(BOOKING_FILE, "w", encoding="utf-8") as f:
            json.dump({"bookings": bookings}, f, indent=2)


# ---------------------------------------------------------
#   VERSION MONGO
# ---------------------------------------------------------
class DbMongoBooking:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client.get_database()
        self.collection = self.db["bookings"]

        # Initialisation depuis JSON si vide
        if self.collection.count_documents({}) == 0:
            json_repo = DbJsonBooking()
            initial_data = json_repo.load()
            if initial_data:
                self.collection.insert_many(initial_data)

    def load(self):
        return list(self.collection.find({}, {"_id": 0}))

    def write(self, bookings):
        self.collection.delete_many({})
        if bookings:
            self.collection.insert_many(bookings)


# ---------------------------------------------------------
#   MÉTHODES PUBLIQUES APPELÉES PAR LES RESOLVERS
# ---------------------------------------------------------
def _get_repo():
    if USING_MONGO:
        return DbMongoBooking()
    return DbJsonBooking()


def load_booking():
    repo = _get_repo()
    return repo.load()


def write(bookings):
    repo = _get_repo()
    return repo.write(bookings)
