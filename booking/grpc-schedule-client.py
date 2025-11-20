import grpc

import schedule_pb2, schedule_pb2_grpc
from google.protobuf.json_format import MessageToJson


def run():
    # FIXME : utiliser envvar
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = schedule_pb2_grpc.ScheduleStub(channel)

        print("-------------- GetScheduleByDate --------------")
        scheduleday = schedule_pb2.Day(date="20151130")
        schedule = stub.GetScheduleByDate(scheduleday)
        print(schedule)
        print("en JSON :")
        print(MessageToJson(schedule))

    channel.close()

if __name__ == '__main__':
    run()