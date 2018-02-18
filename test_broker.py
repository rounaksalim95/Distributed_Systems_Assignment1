import zmq

context = zmq.Context()

socket = context.socket(zmq.REP)

socket.bind("tcp://*:7777")

while True: 
    message = socket.recv()
    print("message is ", message) 
    socket.send(b"OK")