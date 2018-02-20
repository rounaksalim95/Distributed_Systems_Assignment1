''' 
Middleware that sits on top of zmq and provides thin wrapper 
functions for the publisher, subscriber, and broker to use 
'''

import zmq
from sortedcontainers import SortedListWithKey

default_broker_pub_address = "tcp://*:7778"
default_broker_rep_address = "tcp://*:7777"
client_connect_req_address = "tcp://localhost:7777"
client_connect_sub_address = "tcp://localhost:7778"


class Broker:
    def __init__(self,
                 pub_addr = default_broker_pub_address,
                 rep_addr = default_broker_rep_address):
        self.pub_addr = pub_addr
        self.rep_addr = rep_addr
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.rep_socket = self.context.socket(zmq.REP)

        # Dictionary that topics to sorted lists that keep track of the avaialable publishers
        # (sorted on ownership strength)
        self.topics_dict = {}

        '''
        Funtion that binds a socket for the broker to receive messages from the publishers and subscribers 
        Returns the bound socket 
        address: Address to bind the socket to (include protocol)
        '''
        print('Broker binding pub socket to ', self.pub_addr)
        self.pub_socket.bind(self.pub_addr)
        print('Broker binding rep socket to ', self.rep_addr)
        self.rep_socket.bind(self.rep_addr)

    # Some helper functions
    '''
    Funtion that destroys the provided socket  
    socket: Socket to destroy 
    '''
    def stop_listening(self):
        self.pub_socket.destroy()
        self.rep_socket.destroy()
        print("Sockets destroyed")

    '''
    Function that adds the provided publisher to topics_dict
    publisher_info: Information on the publisher 
    Publisher is of the form : (address, ownership_strength, history)
    '''
    def add_publisher(self, publisher_info):
        # print(publisher_info)
        topic = publisher_info['topic']
        publisher = (publisher_info['addr'], int(publisher_info['ownStr']), int(publisher_info['history']))
        if topic in self.topics_dict:
            self.topics_dict[topic].add(publisher)
        else:
            # Created new sorted list sorted by -x[1] (negative of ownership strength)
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
            msg_dict = self.rep_socket.recv_pyobj()
            print(msg_dict)

            # If publisher makes request then add them to topics_dict appropriately
            if msg_dict['type'] == 'pub_reg':
                self.add_publisher(msg_dict)
                response = {'type': 'pub_reg', 'result': 1}
                self.rep_socket.send_pyobj(response)
                print(self.topics_dict)

            # No one actually sends this at the moment
            elif msg_dict['type'] == 'shutdown':
                response = {'type': 'shutdown', 'result': 1}
                self.rep_socket.send_pyobj(response)
                break

            elif msg_dict['type'] == 'sub':
                address = self.find_publisher(msg_dict['topic'], msg_dict['history'])
                if address is not None:
                    self.rep_socket.send(address.encode())  # encode() uses utf-8 encoding by default
                else:
                    self.rep_socket.send(b"None")

            elif msg_dict['type'] == 'disconnect':
                self.remove_publisher(msg_dict['addr'], msg_dict['topic'], msg_dict['history'])
                self.rep_socket.send(b"ACK")

            elif msg_dict['type'] == 'ping':
                response = {'type': 'ping', 'result': 1}
                self.rep_socket.send_pyobj(response)

            else:
                response = {'type': 'unknown', 'result': 0}
                self.rep_socket.send_pyobj(response)

        # End while. Shutdown broker.
        self.stop_listening()


class Client:
    def __init__(self,
                 req_addr = client_connect_req_address,
                 sub_addr = client_connect_sub_address):
        self.sub_addr = sub_addr
        self.req_addr = req_addr
        self.context = zmq.Context()
        self.req_socket = self.context.socket(zmq.REQ)
        self.sub_socket = self.context.socket(zmq.SUB)

        # Connect sockets to broker
        print('Client connecting pub socket to ', self.req_addr)
        self.req_socket.connect(self.req_addr)
        print('Client connecting sub socket to ', self.sub_addr)
        self.sub_socket.connect(self.sub_addr)

        # Subscribe to standard messages
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "BROKER_CMD")

        # Send ping to broker
        ping = {'type': 'ping'}
        self.req_socket.send_pyobj(ping)

        # Wait for broker response
        ping_response = self.req_socket.recv_pyobj()
        if ping_response['type'] == 'ping' and ping_response['result'] == 1:
            print('Client init successful')
        else:
            print('Client init failed')

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
    def register_pub(self, address, topic, ownership_strength = 0, history = 0):
        print("Registering publisher with broker")
        values = {'type': 'pub_reg', 'addr': address, 'topic': topic, 'ownStr': ownership_strength, 'history': history}
        self.req_socket.send_pyobj(values)
        response = self.req_socket.recv_pyobj()
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
    def register_sub(self, topic, history = 0):
        # FIXME: Really dont have to register with broker under current architecture. Just use zmq_setsockopt
        print("Registering subscriber with broker")
        values = {'type': 'sub', 'topic': topic, 'history': history}
        self.req_socket.send_pyobj(values)
        response = self.req_socket.recv_pyobj()
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
