import json
import os
from graphql import GraphQLError
import os
import sys
from dotenv import load_dotenv

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from checkAdmin import checkAdmin
load_dotenv()

# CREATION DU CHEMIN
BASE_DIR = os.path.join(os.path.dirname(__file__), "data")

# OUVERTURE ET FERMETURE AUTOMATIQUE DU FICHIER ET TRANSFORMATION DES DONNEES JSON EN PYTHON
with open(os.path.join(BASE_DIR, "actors.json"), encoding="utf-8") as f:
    actors_data = json.load(f)["actors"]

with open(os.path.join(BASE_DIR, "movies.json"), encoding="utf-8") as f:
    movies_data = json.load(f)["movies"]

# RECUP TOUT LES FILMS
def resolve_all_movies(_, info):
    return movies_data

# RECUP UN FILM AVEC SON ID
def resolve_movie_with_id(_, info, _id):
    for movie in movies_data:
        if movie["id"] == _id:
            return movie
    return None

# RECUP UN FILM AVEC SON TITRE
def resolve_get_movie_by_title(_, info, title):
    for m in movies_data:
        if m["title"] == title:
            return m
    return None

# AJOUTER UN FILM
def resolve_add_movie(_, info, id, title, rating, director):
    req = info.context
    uid = None
    if hasattr(req, "args"):
        uid = req.args.get("uid")
    elif isinstance(req, dict):
        uid = req.get("uid")

    if (not checkAdmin(uid)):
        raise GraphQLError("Unauthorized")
    
    new_movie = {
        "id": id,
        "title": title,
        "rating": rating,
        "director": director
    }

    movies_data.append(new_movie)
    return new_movie

# UPDATE LE RATING D'UN FILM
def resolve_update_movie(_, info, id, rating):
    req = info.context
    uid = None
    if hasattr(req, "args"):
        uid = req.args.get("uid")
    elif isinstance(req, dict):
        uid = req.get("uid")

    if (not checkAdmin(uid)):
        raise GraphQLError("Unauthorized")
    for m in movies_data:
        if m["id"] == id:
                m["rating"] = rating
    return m

# DELETE MOVIE
def resolve_delete_movie(_, info, id):
    req = info.context
    uid = None
    if hasattr(req, "args"):
        uid = req.args.get("uid")
    elif isinstance(req, dict):
        uid = req.get("uid")

    if (not checkAdmin(uid)):
        raise GraphQLError("Unauthorized")
    
    for m in movies_data:
        if m["id"] == id:
            movies_data.remove(m)
            # Lorsqu'on supprime un film, on le supprime de la liste pour chaque acteur
            for actor in actors_data:
                if m["id"] in actor["films"]:
                    actor["films"].remove(m["id"])
            return True
    return False


# RECUP TOUT LES ACTEURS AVEC LA LISTE DE LEURS FILMS
def resolve_all_actors(_, info):
    actors_list = []
    for actor in actors_data:
        if actor.get("firstname") and actor.get("lastname") and actor.get("birthyear") and actor.get("id"):
            actor_with_films = {
                "id": actor["id"],
                "first_name": actor["firstname"],
                "last_name": actor["lastname"],
                "birthyear": actor["birthyear"],
                "films": [ m for m in movies_data if (m["id"] in actor.get('films',[])) ]
            }
            actors_list.append(actor_with_films)
    return actors_list

# RECUP UN SEUL ACTEUR AVEC SON ID AVEC LA LISTE DE SES FILMS
def resolve_actor_with_id(_, info, _id):
    for actor in actors_data:
        if actor["id"] == _id:
            return {
                "id": actor["id"],
                "first_name": actor["firstname"],
                "last_name": actor["lastname"],
                "birthyear": actor["birthyear"],
                "films": [m for m in movies_data if m["id"] in actor.get("films", [])]
            }
    return None

# AJOUTER UN ACTOR
def resolve_add_actor(_, info, id, first_name, last_name, birthyear, films):
    existing_movie_ids = [movie["id"] for movie in movies_data]
    for film in films:
        if film not in existing_movie_ids:
            raise GraphQLError(f"Movie {film} not found")
    new_actor = {
        "id": id,
        "firstname": first_name,
        "lastname": last_name,
        "birthyear": birthyear,
        "films": films
    }

    actors_data.append(new_actor)

    return {
        "id": id,
        "first_name": first_name,
        "last_name": last_name,
        "birthyear": birthyear,
        "films": [m for m in movies_data if m["id"] in films]
    }

# UPDATE UN ACTOR
def resolve_update_actor_films(_, info, id, films):
    existing_movie_ids = [movie["id"] for movie in movies_data]
    for film in films:
        if film not in existing_movie_ids:
            raise GraphQLError(f"Movie {film} not found")
    for a in actors_data:
        if a["id"] == id:
            a["films"] = films
            return {
                "id": a["id"],
                "first_name": a["firstname"],
                "last_name": a["lastname"],
                "birthyear": a["birthyear"],
                "films": [m for m in movies_data if m["id"] in films]
            }
    return None

# DELETE ACTOR
def resolve_delete_actor(_, info, id):
    for a in actors_data:
        if a["id"] == id:
            actors_data.remove(a)
            return True
    return False

