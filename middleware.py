''' 
Middleware that sits on top of zmq and provides thin wrapper 
functions for the publisher, subscriber, and broker to use 
'''

import zmq
from sortedcontainers import SortedListWithKey

default_address = "tcp://*:7777"


class Broker:
    def __init__(self, addr = default_address):
        self.addr = addr
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

        # Dictionary that topics to sorted lists that keep track of the avaialable publishers (sorted on ownership strength)
        self.topics_dict = {}

        '''
        Funtion that binds a socket for the broker to receive messages from the publishers and subscribers 
        Returns the bound socket 
        address: Address to bind the socket to (include protocol)
        '''
        print('Binding socket to ', self.addr)
        self.socket.bind(self.addr)

    # Some helper functions
    '''
    Funtion that destroys the provided socket  
    socket: Socket to destroy 
    '''
    def stop_listening(self):
        self.socket.destroy()
        print("Socket destroyed")

    '''
    Function that adds the provided publisher to topics_dict
    publisher_info: Information on the publisher 
    Publisher is of the form : (address, ownership_strength, history)
    '''
    def add_publisher(self, publisher_info):
        print(publisher_info)
        topic = publisher_info['topic']
        publisher = (publisher_info['addr'], int(publisher_info['ownStr']), int(publisher_info['history']))
        if topic in self.topics_dict:
            self.topics_dict[topic].add(publisher)
        else:
            self.topics_dict[topic] = SortedListWithKey(key=lambda x: -x[1])
            self.topics_dict[topic].add(publisher)

    '''
    Function that searches for the best available publisher based on the requirements of the subscriber 
    topic: Topic that the subscriber wants to subscribe to 
    history: Minimum history that the subscriber is looking for 
    '''
    def find_publisher(self, topic, history):
        if topic in self.topics_dict and len(self.topics_dict[topic]) > 0:
            for lst in self.topics_dict[topic]:
                if lst[2] >= history:
                    return lst[0]

        # Return None if no publishers for the topic or not enough history maintained
        return None

    '''
    Function that removes a disconnected publisher from the list of publishers 
    publisher: Address of the publisher that got disconnected 
    topic: Topic that the publisher was serving content for  
    '''
    def remove_publisher(self, publisher, topic, history):
        if topic in self.topics_dict and len(self.topics_dict[topic]) > 0:
            lists = self.topics_dict[topic]
            for i in range(len(lists)):
                if lists[i][0] == publisher and lists[i][2] == history:
                    lists.pop(i)
                    break

    def run(self):
        # TODO: How to terminate loop?
        # Listen to incoming publisher and subscriber requests
        while True:
            msg_dict = self.socket.recv_pyobj()

            # If publisher makes request then add them to topics_dict appropriately
            if msg_dict['type'] == 'pub':
                self.add_publisher(msg_dict)
                self.socket.send(b"Added publisher")
                print(self.topics_dict)

            if msg_dict['type'] == 'shutdown:':
                break

            elif msg_dict['type'] == 'sub':
                address = self.find_publisher(msg_dict['topic'], msg_dict['history'])
                if address != None:
                    self.socket.send(address.encode())  # encode() uses utf-8 encoding by default
                else:
                    self.socket.send(b"None")

            elif msg_dict['type'] == 'disconnect':
                self.remove_publisher(msg_dict['addr'], msg_dict['topic'], msg_dict['history'])
                self.socket.send(b"ACK")
        # End while. Shutdown broker.
        self.stop_listening()


# Wrapper functions that are useful for the publishers
'''
Function that can be called to register the publisher with the broker 
Returns the response received by the broker 
address: Address that the publisher is pushing content from 
broker_address: Address of the broker that the request needs to be sent to (include protocol)
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
    values = {'type': 'pub', 'addr': address, 'topic': topic, 'own_str': ownership_strength, 'history': history}
    socket.send_pyobj(values)
    response = socket.recv()
    context.destroy()
    return response

# This function is not required if we directly connect the publishers to the subscribers 
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
Returns the address of the best publisher available 
broker_address: Address of the broker that the request needs to be sent to (include protocol)
topic: Topic that the subscriber wants to subscribe to 
history: The amount of history that the subscriber wants the publisher to maintain (default value is 0)
Returns publisher that the subscriber should subscribe to 
'''
def register_sub(broker_address, topic, history = 0):
    context = zmq.Context()
    print("Registering subscriber with broker") 
    socket = context.socket(zmq.REQ)
    socket.connect(broker_address)
    values = {'type': 'sub', 'topic': topic, 'history': history}
    socket.send_pyobj(values)
    response = socket.recv()
    context.destroy()
    return response

'''
Function that the subscriber can use to inform the broker that it has lost the publisher it was connected to;
broker responds by providing next best publisher 
Returns the address of the next best publisher available 
broker_address: Address of the broker that the request needs to be sent to (include protocol)
publisher: The publisher that the subscriber was subscribed to (this can be used by the broker to remove the inactive publisher)
topic: Topic that the subscriber wants to subscribe to 
history: The amount of history that the subscriber wants the publisher to maintain (default value is 0)
'''
def notify(broker_address, publisher, topic, history = 0):
    context = zmq.Context()
    print("Notifying broker that the publisher got disconnected")
    socket = context.socket(zmq.REQ)
    socket.connect(broker_address)
    values = {'type': 'disconnect', 'addr': publisher, 'topic': topic, 'history': history}
    socket.send_pyobj(values)
    response = socket.recv()
    context.destroy()
    return response