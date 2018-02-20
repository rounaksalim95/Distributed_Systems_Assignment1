''' 
Middleware that sits on top of zmq and provides thin wrapper 
functions for the publisher, subscriber, and broker to use 
'''

import zmq
from sortedcontainers import SortedListWithKey

default_broker_control_address = "tcp://*:7777"
default_broker_sub_address = "tcp://*:7777"
default_client_address = "tcp://localhost:7777"


class Broker:
    def __init__(self,
                 control_addr = default_broker_control_address,
                 sub_addr = default_broker_sub_address):
        self.control_addr = control_addr
        self.sub_addr = sub_addr
        self.context = zmq.Context()
        self.control_socket = self.context.socket(zmq.REP)
        self.sub_socket = self.context.socket(zmq.SUB)

        # Dictionary that topics to sorted lists that keep track of the avaialable publishers
        # (sorted on ownership strength)
        self.topics_dict = {}

        '''
        Funtion that binds a socket for the broker to receive messages from the publishers and subscribers 
        Returns the bound socket 
        address: Address to bind the socket to (include protocol)
        '''
        print('Broker binding control socket to ', self.control_addr)
        self.control_socket.bind(self.control_addr)
        print('broker binding subscriber socket to ', self.sub_addr)
        self.sub_socket.bind(self.sub_addr)

    # Some helper functions
    '''
    Funtion that destroys the provided socket  
    socket: Socket to destroy 
    '''
    def stop_listening(self):
        self.control_socket.destroy()
        self.sub_socket.destroy()
        print("Sockets destroyed")

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
        # End while. Shutdown broker.
        self.stop_listening()


class Client:
    def __init__(self, addr = default_client_address, broker_addr = default_broker_address):
        self.addr = addr
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)

        # Connect sockets to broker
        self.pub_socket.connect(broker_addr)
        # TODO: Connect sub socket to broker pub socket

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
    def register_pub(self, address, broker_address, topic, ownership_strength = 0, history = 0):
        print("Registering publisher with broker")
        values = {'type': 'pub', 'addr': address, 'topic': topic, 'ownStr': ownership_strength, 'history': history}
        self.pub_socket.send_pyobj(values)
        response = self.pub_socket.recv()
        context.destroy()
        return response

    # This function is not required if we directly connect the publishers to the subscribers
    '''
    Function that the publisher can use to publish data through this middleware/wrapper
    topic: Topic for which content is being published 
    content: The content that is being published 
    '''
    def publish(self, topic, content):
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
    def register_sub(self, broker_address, topic, history = 0):
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
    def notify(self, broker_address, publisher, topic, history = 0):
        context = zmq.Context()
        print("Notifying broker that the publisher got disconnected")
        socket = context.socket(zmq.REQ)
        socket.connect(broker_address)
        values = "disconnect" + "," + publisher + "," + topic + str(history)
        socket.send(values.encode())    # encode() uses utf-8 encoding by defualt
        response = socket.recv()
        context.destroy()
        return response