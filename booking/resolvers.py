import json
import os

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

