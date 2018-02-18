''' 
Middleware that sits on top of zmq and provides thin wrapper 
functions for the publisher, subscriber, and broker to use 
'''

import zmq

# Wrapper functions that are useful for the publishers 
'''
Function that can be called to register the publisher with the broker 
Returns the response received by the broker 
address: Address that the publisher is pushing content from 
broker_address: Address of the broker that the request needs to be sent to (including protocol)
topic: Topic that the publisher is pushing content for
ownership_strength: The ownership strength of the publisher (default value is 0)
history: The amount of history that the publisher maintains (default value is 0)
Broker receives values in the following form: address,topic,ownership_strength,history (csv)
'''
def register_pub(address, broker_address, topic, ownership_strength = 0, history = 0):
    context = zmq.Context()
    print("Registering publisher with broker") 
    socket = context.socket(zmq.REQ)
    socket.connect(broker_address)
    values = address + "," + topic + "," + ownership_strength + "," + history
    socket.send(address.encode())   # encode() uses utf-8 encoding by default 
    
    response = socket.recv()
    return response

'''
Function that the publisher can use to publish data through this middleware/wrapper
topic: Topic for which content is being published 
content: The content that is being published 
'''
def publish(topic, content):
    pass


# Wrapper functions that are useful for the subscribers 
'''
Function that can be called to register the subscriber with the broker 
topic: Topic that the subscriber wants to subscribe to 
history: The amount of history that the subscriber wants the publisher to maintain (default value is 0)
Returns publisher that the subscriber should subscribe to 
'''
def register_sub(topic, history = 0):
    pass

'''
Function that the subscriber can use to inform the broker that it has lost the publisher it was connected to 
publisher: The publisher that the subscriber was subscribed to (this can be used by the broker to remove the inactive publisher)
topic: Topic that the subscriber wants to subscribe to 
history: The amount of history that the subscriber wants the publisher to maintain (default value is 0)
'''
def notify(publisher, topic, history = 0):
    pass