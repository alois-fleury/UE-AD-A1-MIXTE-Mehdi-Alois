import grpc
import json
import schedule_pb2, schedule_pb2_grpc
from google.protobuf.json_format import MessageToJson
from dotenv import load_dotenv
import os 

load_dotenv()
SCHEDULE_SERVICE_URL = os.getenv("SCHEDULE_SERVICE_URL", "localhost:3202")

def get_schedule_by_date(requestDate):
    with grpc.insecure_channel(SCHEDULE_SERVICE_URL) as channel:
        print("channel : ")
        stub = schedule_pb2_grpc.ScheduleStub(channel)
        scheduleday = schedule_pb2.Date(date=requestDate)
        scheduleByDate = stub.GetScheduleByDate(scheduleday)
    channel.close()
    return json.loads(MessageToJson(scheduleByDate))

def run():
    with grpc.insecure_channel(SCHEDULE_SERVICE_URL) as channel:
        stub = schedule_pb2_grpc.ScheduleStub(channel)

        print("-------------- GetScheduleByDate --------------")
        scheduleday = schedule_pb2.Date(date="20151130")
        scheduleByDate = stub.GetScheduleByDate(scheduleday)
        print(MessageToJson(scheduleByDate))

        print("-------------- GetAllScheduleDays --------------")
        alldays = stub.GetAllScheduleDays(schedule_pb2.Empty())
        print(MessageToJson(alldays))

        print("-------------- AddScheduleDay --------------")
        try: 
            new_day = schedule_pb2.ScheduleData(
                date="20251121",
                movies=["Movie 1", "Movie 2", "Movie 3"]
            )
            added_day = stub.AddScheduleDay(new_day)
            print(MessageToJson(added_day))
        except grpc.RpcError as e:
            print(f"Erreur gRPC : {e.code()} - {e.details()}")


        print("-------------- DeleteScheduleDay --------------")
        try:
            dateDayToDelete = schedule_pb2.Date(date="20251121")
            deleted_day = stub.DeleteScheduleDay(dateDayToDelete)
            print(MessageToJson(deleted_day))
        except grpc.RpcError as e:
            print(f"Erreur gRPC : {e.code()} - {e.details()}")

    channel.close()

if __name__ == '__main__':
    run()