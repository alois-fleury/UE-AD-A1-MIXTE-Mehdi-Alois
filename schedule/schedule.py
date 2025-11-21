import grpc
from grpc import StatusCode
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import json
import os 
import requests

MOVIE_SERVICE_URL="http://127.0.0.1:3200/graphql"
BOOKING_SERVICE_URL="http://127.0.0.1:3201/graphql"

PORT = 3002

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_PATH = os.path.join(BASE_DIR, "data", "times.json")

class ScheduleServicer(schedule_pb2_grpc.ScheduleServicer):

    def __init__(self):
        with open(DB_PATH, "r") as jsf:
            self.db = json.load(jsf)["schedule"]
    
    def write(self, schedule):
        with open(DB_PATH, 'w') as f:
            full = {}
            full['schedule']=schedule
            json.dump(full, f)
    
    def GetScheduleByDate(self, request, context):
        print(f"Called GetScheduleByDate with {request}")
        for day in self.db : 
            if day["date"] == request.date :
                return schedule_pb2.ScheduleData(date=day["date"], movies=day["movies"])
        return schedule_pb2.ScheduleData(date="", movies=[])
    
    def GetAllScheduleDays(self, request, context):
        print(f"Called GetAllScheduleDays\n")
        dates = []
        for day in self.db:
            dates.append(schedule_pb2.ScheduleData(date=day["date"], movies=day["movies"]))
        return schedule_pb2.Planning(planning=dates)
    
    def AddScheduleDay(self, request, context):
        print(f"Called AddScheduleDay with {request}")
        # TODO : auth
        # if not (checkAdmin(request.args.get("uid"))):
        #     return jsonify({"error": "Unauthorized"}), 403

        for day in self.db:
            if day["date"] == request.date:
                context.abort(StatusCode.ALREADY_EXISTS, "Cette date existe déjà")
    
        query = """
        query {
            all_movies {
                id
            }
        }
        """

        payload = {
            "query": query
        }

        response = requests.post(MOVIE_SERVICE_URL, json=payload)
        data = response.json()          
        existing_movie_ids = [movie["id"] for movie in data["data"]["all_movies"]]

        for mid in request.movies:
            if mid not in existing_movie_ids:
                context.abort(StatusCode.INVALID_ARGUMENT, "Un film inexistant a été précisé")
        daytoadd = {
            'date': request.date,
            'movies': list(request.movies)
        }
        self.db.append(daytoadd)
        self.write(self.db)
        return schedule_pb2.ScheduleData(date=daytoadd["date"], movies=daytoadd["movies"])
    
    def DeleteScheduleDay(self, request, context):
        print(f"Called DeleteScheduleDay with {request}")
        # if not (checkAdmin(request.args.get("uid"))):
        #     return jsonify({"error": "Unauthorized"}), 403

        for day in self.db:
            if day["date"] == request.date:
                self.db.remove(day)
                self.write(self.db)
                return schedule_pb2.ScheduleData(date=day["date"], movies=day["movies"])
        context.abort(StatusCode.NOT_FOUND, "Cette date n'existe pas")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    print("Server running in port %s"%(PORT))
    print("* Serving gRPC app 'schedule'\n")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
