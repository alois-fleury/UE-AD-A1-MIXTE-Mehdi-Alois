import json
import os

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
