from flask import Flask, request, jsonify, make_response
from ariadne import make_executable_schema, graphql_sync, QueryType, load_schema_from_path,MutationType
import resolvers as r

app = Flask(__name__)

# Charger le schema GraphQL
type_defs = load_schema_from_path("booking.graphql")

#Def du query et de la mutation
query = QueryType()
mutation = MutationType()

# Lier les queries aux résolveurs 
query.set_field("all_bookings", r.resolve_all_bookings)
query.set_field("booking_with_id", r.resolve_booking_with_id)

# Lier les mutations aux résolveurs 
mutation.set_field("delete_booking", r.resolve_delete_booking)
mutation.set_field("add_booking", r.resolve_add_booking)

schema = make_executable_schema(type_defs, [query,mutation])

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Booking service!</h1>",200)

# Endpoint GraphQL
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=True)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)