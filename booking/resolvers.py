import json
import os
from graphql import GraphQLError
from grpcScheduleClient import get_schedule_by_date
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from checkAdmin import checkAdmin

# CREATION DU CHEMIN
BASE_DIR = os.path.join(os.path.dirname(__file__), "data")

# OUVERTURE ET FERMETURE AUTOMATIQUE DU FICHIER ET TRANSFORMATION DES DONNEES JSON EN PYTHON
with open(os.path.join(BASE_DIR, "bookings.json"), encoding="utf-8") as f:
    booking_data = json.load(f)["bookings"]

with open(os.path.join(BASE_DIR, "movies.json"), encoding="utf-8") as f:
    movies_data = json.load(f)["movies"]

# RECUP TOUTES LES RESERVATIONS
def resolve_all_bookings(_, info):
    booking_list = []

    for booking in booking_data:
        if booking.get("userid") and booking.get("dates"):

            new_dates = []
            for d in booking["dates"]:
                new_dates.append({
                    "date": d["date"],
                    "movies": [m for m in movies_data if m["id"] in d.get("movies", [])]
                })

            booking_list.append({
                "userid": booking["userid"],
                "dates": new_dates
            })

    return booking_list

# RECUP LA RESERVATION AVEC L'ID
def resolve_booking_with_id(_, info, _id):
    for booking in booking_data:
        if booking["userid"] == _id:
            new_dates = []
            for d in booking["dates"]:
                new_dates.append({
                    "date": d["date"],
                    "movies": [m for m in movies_data if m["id"] in d.get("movies", [])]
                })
            return {
                "userid": _id,
                "dates": new_dates
            }
    return None

#AJOUTER UNE RESERVATION
def resolve_add_booking(_, info, userid, date, movies):
    req = info.context
    uid = None
    if hasattr(req, "args"):
        uid = req.args.get("uid")
    elif isinstance(req, dict):
        uid = req.get("uid")

    if (userid != uid) and (not checkAdmin(uid)):
        raise GraphQLError("Unauthorized")
    
    # Vérification que la date existe et que les films sont bien programmés
    scheduled = get_schedule_by_date(date)
    if (not scheduled) or (scheduled.get("date", "") == ""):
        raise GraphQLError("No schedule found for the given date")

    scheduled_movie_ids = scheduled.get("movies", [])
    for movie_id in movies:
        if movie_id not in scheduled_movie_ids:
            raise GraphQLError(f"Movie {movie_id} is not scheduled on the given date")

    # Vérifier si L'user existe déjà
    for booking in booking_data:
        if booking["userid"] == userid:
            # Ajouter une nouvelle date
            booking["dates"].append({
                "date": date,
                "movies": movies
            })
            return resolve_booking_with_id(_, info, userid)

    # Sinon on crée un nouvel utilisateur
    new_booking = {
        "userid": userid,
        "dates": [
            {
                "date": date,
                "movies": movies
            }
        ]
    }
    booking_data.append(new_booking)

    # ON RECUP LA RESERVATION AJOUTEE
    return resolve_booking_with_id(_, info, userid)

def resolve_delete_booking(_, info, userid):
    # TODO : supprimer partiellement un booking
    req = info.context
    uid = None
    if hasattr(req, "args"):
        uid = req.args.get("uid")
    elif isinstance(req, dict):
        uid = req.get("uid")

    if (userid != uid) and (not checkAdmin(uid)):
        raise GraphQLError("Unauthorized")
    
    for b in booking_data:
        if b["userid"] == userid:
            booking_data.remove(b)
            return True
    return False
