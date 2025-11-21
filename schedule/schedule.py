import grpc
from grpc import StatusCode
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import json
import os 
import requests
import sys 
from dotenv import load_dotenv
import logging

grpc_logger = logging.getLogger('grpc_server')
grpc_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s][gRPC] %(levelname)s: %(message)s')
handler.setFormatter(formatter)
grpc_logger.addHandler(handler)

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from checkAdmin import checkAdmin
load_dotenv()

MOVIE_SERVICE_URL=os.getenv("MOVIE_SERVICE_URL") + "/graphql"
BOOKING_SERVICE_URL=os.getenv("BOOKING_SERVICE_URL") + "/graphql"

PORT = 3202

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_PATH = os.path.join(BASE_DIR, "data", "times.json")

from db import get_schedule_db

class ScheduleServicer(schedule_pb2_grpc.ScheduleServicer):

    def __init__(self):
        self.db_manager = get_schedule_db()
        self.db = self.db_manager.load()

    def _extract_uid(self, context):
        for key, value in context.invocation_metadata() or []:
            if key == "uid":
                return value
        return None
    
    def write(self, schedule):
        self.db_manager.write(schedule)
    
    def GetScheduleByDate(self, request, context):
        grpc_logger.info(f"Called GetScheduleByDate with {request}")
        self.db_manager = get_schedule_db()
        self.db = self.db_manager.load()
        for day in self.db : 
            if day["date"] == request.date :
                return schedule_pb2.ScheduleData(date=day["date"], movies=day["movies"])
        return schedule_pb2.ScheduleData(date="", movies=[])
    
    def GetAllScheduleDays(self, request, context):
        grpc_logger.info(f"Called GetAllScheduleDays\n")
        self.db_manager = get_schedule_db()
        self.db = self.db_manager.load()
        dates = []
        for day in self.db:
            dates.append(schedule_pb2.ScheduleData(date=day["date"], movies=day["movies"]))
        return schedule_pb2.Planning(planning=dates)
    
    def AddScheduleDay(self, request, context):
        grpc_logger.info(f"Called AddScheduleDay with {request}")
        self.db_manager = get_schedule_db()
        self.db = self.db_manager.load()
        uid = self._extract_uid(context)
        if not checkAdmin(uid):
            context.abort(StatusCode.PERMISSION_DENIED, "Unauthorized")

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
        grpc_logger.info(f"Called DeleteScheduleDay with {request}")
        self.db_manager = get_schedule_db()
        self.db = self.db_manager.load()
        uid = self._extract_uid(context)
        if not checkAdmin(uid):
            context.abort(StatusCode.PERMISSION_DENIED, "Unauthorized")

        for day in self.db:
            if day["date"] == request.date:
                self.db.remove(day)
                self.write(self.db)
                return schedule_pb2.ScheduleData(date=day["date"], movies=day["movies"])
        context.abort(StatusCode.NOT_FOUND, "Cette date n'existe pas")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3202')
    server.start()
    grpc_logger.info("Server running in port %s"%(PORT))
    grpc_logger.info("* Serving gRPC app 'schedule'\n")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
