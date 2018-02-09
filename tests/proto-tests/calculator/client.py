# import the generated classes
import time

import calculator_pb2
import calculator_pb2_grpc
import grpc

clients = []

# open a gRPC channel
channel = grpc.insecure_channel('localhost:50051')

for i in range(500):
    # create a stub (client)
    clients.append(calculator_pb2_grpc.CalculatorStub(channel))

# create a valid request message
number = calculator_pb2.Number(value=16)

begintime = time.time()
for client in clients:
    # make the call
    response = client.SquareRoot(number)
    # et voilà
    # print(response.value)
duration = time.time() - begintime
print("took: %s sec." % duration)
