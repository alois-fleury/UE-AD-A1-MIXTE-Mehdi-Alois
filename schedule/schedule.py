import grpc
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import json
import os 

PORT = 3002

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_PATH = os.path.join(BASE_DIR, "data", "times.json")

class ScheduleServicer(schedule_pb2_grpc.ScheduleServicer):

    def __init__(self):
        with open(DB_PATH, "r") as jsf:
            self.db = json.load(jsf)["schedule"]
    
    def GetScheduleByDate(self, request, context):
        print(f"Called GetScheduleByDate with {request}")
        for day in self.db : 
            if day["date"] == request.date :
                return schedule_pb2.ScheduleData(date=day["date"], movies=day["movies"])
        return schedule_pb2.ScheduleData(date="", movies=[])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    print("Server running in port %s"%(PORT))
    print("* Serving gRPC app 'schedule'")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
