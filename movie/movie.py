
from flask import Flask, request, jsonify, make_response
from ariadne import make_executable_schema, graphql_sync, QueryType, load_schema_from_path, MutationType
import resolvers as r

app = Flask(__name__)

# Charger le schema GraphQL
type_defs = load_schema_from_path("movie.graphql")

# Déf du Query et de la mutation 
query = QueryType()
mutation = MutationType()

# Lier les queries aux résolveurs 

# Pour les movies
query.set_field("all_movies", r.resolve_all_movies)
query.set_field("movie_with_id", r.resolve_movie_with_id)
query.set_field("movie_by_title", r.resolve_get_movie_by_title)

# Pour les actors 
query.set_field("all_actors", r.resolve_all_actors)
query.set_field("actor_with_id", r.resolve_actor_with_id)

# Lier les mutations aux résolveurs 

# Pour les movies 
mutation.set_field("add_movie", r.resolve_add_movie)
mutation.set_field("update_movie", r.resolve_update_movie)
mutation.set_field("delete_movie", r.resolve_delete_movie)

# Pour les actors
mutation.set_field("add_actor", r.resolve_add_actor)
mutation.set_field("update_actor_films", r.resolve_update_actor_films)
mutation.set_field("delete_actor", r.resolve_delete_actor)

schema = make_executable_schema(type_defs, [query,mutation])

# message racine
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# Endpoint GraphQL
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=True)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
