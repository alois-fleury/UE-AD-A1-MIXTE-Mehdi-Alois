import json
import os
from graphql import GraphQLError
from grpcScheduleClient import get_schedule_by_date
import os
import sys
import requests
from dotenv import load_dotenv

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from checkAdmin import checkAdmin
load_dotenv()

MOVIE_SERVICE_URL=os.getenv("MOVIE_SERVICE_URL") + "/graphql"

from db import load_booking, write

def fetch_movie_from_movies_service(movie_id):
    query = """
    query($id: String!) {
        movie_with_id(_id: $id) {
            id
            title
            rating
            director
        }
    }
    """
    payload = {"query": query, "variables": {"id": movie_id}}

    response = requests.post(MOVIE_SERVICE_URL, json=payload)
    data = response.json()
    return data["data"]["movie_with_id"]

# RECUP TOUTES LES RESERVATIONS
def resolve_all_bookings(_, info):
    booking_list = []
    booking_data = load_booking()

    for booking in booking_data:
        if booking.get("userid") and booking.get("dates"):

            new_dates = []
            for d in booking["dates"]:
                movies_details = []

                for movie_id in d.get("movies", []):
                    movie = fetch_movie_from_movies_service(movie_id)
                    movies_details.append(movie)

                new_dates.append({
                    "date": d["date"],
                    "movies": movies_details
                })

            booking_list.append({
                "userid": booking["userid"],
                "dates": new_dates
            })

    return booking_list

# RECUP LA RESERVATION AVEC L'ID
def resolve_booking_with_id(_, info, _id):
    booking_data = load_booking()
    for booking in booking_data:
        if booking["userid"] == _id:
            new_dates = []
            for d in booking["dates"]:
                movies_details = []
                for movie_id in d.get("movies", []):
                    movie = fetch_movie_from_movies_service(movie_id)
                    movies_details.append(movie)

                new_dates.append({
                    "date": d["date"],
                    "movies": movies_details
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

    booking_data = load_booking()

    # Vérification que la date existe et que les films sont bien programmés
    scheduled = get_schedule_by_date(date)
    if (not scheduled) or (scheduled.get("date", "") == ""):
        raise GraphQLError("No schedule found for the given date")

    # Vérifie si le film est prévu à la date donnée
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

    write(booking_data)

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
    
    booking_data = load_booking()
    for b in booking_data:
        if b["userid"] == userid:
            booking_data.remove(b)
            return True
    write(booking_data)
    return False
