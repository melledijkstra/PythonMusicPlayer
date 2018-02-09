# import the generated classes
import datetime
import time

from mpserver.grpc import mmp_pb2
from mpserver.grpc import mmp_pb2_grpc
import grpc

# open a gRPC channel
channel = grpc.insecure_channel('localhost:11911')
client = mmp_pb2_grpc.MusicPlayerStub(channel)

sr = mmp_pb2.MMPStatusRequest()

# make the call
response = client.RegisterMMPNotify(sr)
begintime = time.time()
for status in response:
    duration = time.time() - begintime
    print("[{} - {:.2f} sec.] {}".format(datetime.datetime.now().strftime('%H:%M:%S'), duration, status.state))
    begintime = time.time()
