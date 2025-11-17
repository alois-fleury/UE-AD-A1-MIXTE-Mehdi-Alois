
from flask import Flask, request, jsonify, make_response
from ariadne import make_executable_schema, graphql_sync, QueryType, load_schema_from_path
import resolvers as r

app = Flask(__name__)

# Charger le schema GraphQL
type_defs = load_schema_from_path("movie.graphql")
query = QueryType()

# Lier les queries aux résolveurs 
query.set_field("all_movies", r.resolve_all_movies)
query.set_field("movie_with_id", r.resolve_movie_with_id)
query.set_field("all_actors", r.resolve_all_actors)
query.set_field("actor_with_id", r.resolve_actor_with_id)

schema = make_executable_schema(type_defs, query)

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
