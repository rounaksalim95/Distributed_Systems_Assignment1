'''
Middleware that sits on top of zmq and provides thin wrapper
functions for the publisher, subscriber, and broker to use
'''

import zmq
import socket
import collections
import threading
import time
from sortedcontainers import SortedListWithKey


default_broker_pub_address = "tcp://*:7778"
default_broker_rep_address = "tcp://*:7777"
client_connect_req_address = "tcp://localhost:7777"
client_connect_sub_address = "tcp://localhost:7778"

heartbeat_interval_ms = 1000


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

        # Dictionary for keeping track of clients that are still alive
        self.hb_mutex = threading.Lock()
        self.hb_dict = {}

        # Send first heartbeat
        self.send_hb()


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
    def send_hb(self):
        topic = "BROKER_CMD"
        hb_msg = {'type': 'heartbeat'}
        self.pub_socket.send_string(topic, zmq.SNDMORE)
        self.pub_socket.send_pyobj(hb_msg)

        # Entries in hb_dict are sorted by ip address.
        # Each entry is another dict containing 'count' (hb timeout count) and 'topics' (list of published topics)
        #print(self.hb_dict)
        pub_removal_list = []
        addr_removal_list = []
        self.hb_mutex.acquire()
        for addr, value in self.hb_dict.items():
            #print(value)
            value['count'] = value['count'] - 1

            # If node has responded before count hits 0, done
            if value['count'] > 0:
                continue

            # Else, assume node has died. Find all published topics and mark for removal
            addr_removal_list.append(addr)
            for topic in value['topics']:
                for publisher in self.topics_dict[topic]:
                    if publisher['addr'] == addr:
                        pub_removal_list.append(publisher)
        # Don't like holding a mutex (or mutexes in general) this long, but should always be released.
        self.hb_mutex.release()

        # Remove associated publisher(s) from topics_dict and remove client node from registered list (HB list)
        # NOTE: This is done here to prevent changing the size of topics_dict and hb_dict while iterating over them
        for pub in pub_removal_list:
            self.topics_dict[topic].remove(pub)
        for addr in addr_removal_list:
            self.hb_dict.pop(addr, None)
            print("removed ",addr," from hb_dict")

        # Start next HB timer. Python doesn't seem to offer a reoccuring timer, so this ugly solution is what we get
        self.hb_timer = threading.Timer(heartbeat_interval_ms / 1000, self.send_hb)
        self.hb_timer.start()


    '''
    Funtion that destroys the provided socket
    socket: Socket to destroy
    '''
    def stop_listening(self):
        self.pub_socket.close()
        self.rep_socket.close()
        # print("Sockets closed")
        self.context.destroy()
        # print("Context destroyed")
        self.hb_timer.cancel()

    '''
    Function that adds the provided publisher to topics_dict
    publisher_info: Information on the publisher
    Publisher is of the form : (address, ownership_strength, history count, history list)
    '''
    def add_publisher(self, publisher_info):
        # print(publisher_info)
        # Verify publisher is part of a registered client
        publisher_entry = self.hb_dict.get(publisher_info['addr'])
        print("Publisher entry is :", publisher_entry)
        if publisher_entry is None:
            return False

        topic = publisher_info['topic']
        publisher_entry['topics'].append(topic) # Add topic to heartbeat dict
        publisher = {'addr': publisher_info['addr'],
                     'ownStr': int(publisher_info['ownStr']),
                     'history_cnt': int(publisher_info['history_cnt']),
                     'history_deque': collections.deque(maxlen=publisher_info['history_cnt'])}
        if topic in self.topics_dict:
            self.topics_dict[topic].add(publisher)
        else:
            # Created new sorted list sorted by -x['ownStr'] (negative of ownership strength)
            self.topics_dict[topic] = SortedListWithKey(key=lambda x: -x['ownStr'])
            self.topics_dict[topic].add(publisher)

        return True

    '''
    Function that searches for the best available publisher based on the requirements of the subscriber
    topic: Topic that the subscriber wants to subscribe to
    history_cnt (Optional): Minimum history that the subscriber is looking for
    addr (Optional): Unique publisher address desired
    '''
    def find_publisher(self, topic, history_cnt=None, addr=None):
        # print("topics_dict is: ",self.topics_dict)
        # print("Hist count and topic are: ", history_cnt,topic)
        if topic in self.topics_dict and len(self.topics_dict[topic]) > 0:
            for publisher in self.topics_dict[topic]:
                if history_cnt is not None:
                    if publisher['history_cnt'] >= history_cnt:
                        history_satisfied = True
                    else:
                        history_satisfied = False
                else:
                    history_satisfied = True

                if addr is not None:
                    if publisher['addr'] == addr:
                        addr_satisfied = True
                    else:
                        addr_satisfied = False
                else:
                    addr_satisfied = True

                if history_satisfied and addr_satisfied:
                    return publisher

        # Return None if no publishers for the topic, not enough history maintained, or incorrect address
        return None

    '''
    Function that removes a disconnected publisher from the list of publishers
    publisher_addr: Address of the publisher that got disconnected
    topic: Topic that the publisher was serving content for
    '''
    def remove_publisher(self, publisher_addr, topic):
        if topic in self.topics_dict and len(self.topics_dict[topic]) > 0:
            lists = self.topics_dict[topic]
            for i in range(len(lists)):
                # Address should be unique, so this check is sufficient
                if lists[i]['addr'] == publisher_addr:
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
                result = self.add_publisher(msg_dict)
                response = {'type': 'pub_reg', 'result': result}
                self.rep_socket.send_pyobj(response)
                # print(self.topics_dict)

            elif msg_dict['type'] == 'sub_reg':
                publisher = self.find_publisher(msg_dict['topic'], history_cnt=msg_dict['history_cnt'])
                #print("Matched publisher is: ",publisher)
                if publisher is not None:
                    response = {'type': 'sub_reg', 'result': True, 'history': publisher['history_deque']}
                    self.rep_socket.send_pyobj(response)  # encode() uses utf-8 encoding by default
                else:
                    response = {'type': 'sub_reg', 'result': False}
                    self.rep_socket.send_pyobj(response)

            elif msg_dict['type'] == 'pub':
                publisher = self.find_publisher(msg_dict['topic'], addr=msg_dict['addr'])
                if publisher is not None:
                    # Add to history regardless of ownership strength
                    publisher['history_deque'].append(msg_dict['content'])
                    # print(self.topics_dict)

                    # Only send publication to subs if this is the highest ownership publisher
                    highestPub = (self.topics_dict.get(msg_dict['topic']))[0]
                    # print("Highest pub: ",highestPub)
                    if publisher['ownStr'] >= highestPub['ownStr']:
                        self.pub_socket.send_string(msg_dict['topic'], zmq.SNDMORE)
                        self.pub_socket.send_pyobj(msg_dict['content'])


                    response = {'type': 'pub', 'result': True}
                else:
                    response = {'type': 'pub', 'result': False}
                self.rep_socket.send_pyobj(response)
                pass

            # No one actually sends this at the moment
            elif msg_dict['type'] == 'shutdown':
                response = {'type': 'shutdown', 'result': True}
                self.rep_socket.send_pyobj(response)
                break

            elif msg_dict['type'] == 'disconnect':
                self.remove_publisher(msg_dict['addr'], msg_dict['topic'])
                self.rep_socket.send(b"ACK")

            elif msg_dict['type'] == 'client_reg':
                response = {'type': 'client_reg', 'result': True}
                self.hb_dict[ msg_dict['addr'] ] = {'count': 2, 'topics': []}
                self.rep_socket.send_pyobj(response)

            elif msg_dict['type'] == 'ping':
                hb_entry = self.hb_dict.get(msg_dict['addr'])
                if hb_entry is not None:
                    self.hb_mutex.acquire()
                    hb_entry['count'] = 2
                    self.hb_mutex.release()
                    response = {'type': 'ping', 'result': True}
                else:
                    response = {'type': 'ping', 'result': False}
                self.rep_socket.send_pyobj(response)

            else:
                response = {'type': 'unknown', 'result': False}
                self.rep_socket.send_pyobj(response)

        # End while. Shutdown broker.
        self.stop_listening()


# I don't like this, but it works. Other methods only reported 127.0.0.1 (IPv4) or ::1 (IPv6).
# Found on stack overflow https://stackoverflow.com/a/28950776/9221126
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class Client:
    def __init__(self,
                 req_addr = client_connect_req_address,
                 sub_addr = client_connect_sub_address,
                 ip = get_ip()):
        self.sub_addr = sub_addr
        self.req_addr = req_addr
        self.ip = ip
        self.context = zmq.Context()
        self.req_socket = self.context.socket(zmq.REQ)
        self.sub_socket = self.context.socket(zmq.SUB)

        # Connect sockets to broker
        print('Client connecting req socket to ', self.req_addr)
        self.req_socket.connect(self.req_addr)
        print('Client connecting sub socket to ', self.sub_addr)
        self.sub_socket.connect(self.sub_addr)

        # Subscribe to standard messages
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "BROKER_CMD")

        # Send ping to broker
        reg_msg = {'type': 'client_reg', 'addr': self.ip}
        self.req_socket.send_pyobj(reg_msg)

        # Wait for broker response
        reg_response = self.req_socket.recv_pyobj()
        if reg_response['type'] == 'client_reg' and reg_response['result'] is True:
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
    def register_pub(self, topic, ownership_strength = 0, history = 0):
        print("Registering publisher with broker")
        values = {'type': 'pub_reg', 'addr': self.ip, 'topic': topic, 'ownStr': ownership_strength, 'history_cnt': history}
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
        pub_msg = {'type': 'pub', 'addr': self.ip, 'topic': topic, 'content': content}
        self.req_socket.send_pyobj(pub_msg)
        response = self.req_socket.recv_pyobj()
        return response


    # Wrapper functions that are useful for the subscribers
    '''
    Function that can be called to register the subscriber with the broker
    Returns the address of the best publisher available
    topic: Topic that the subscriber wants to subscribe to
    history: The amount of history that the subscriber wants the publisher to maintain (default value is 0)
    Returns publication history if available, or None otherwise
    '''
    def register_sub(self, topic, history = 0):
        print("Registering subscriber with broker")
        values = {'type': 'sub_reg', 'topic': topic, 'history_cnt': history}
        self.req_socket.send_pyobj(values)
        response = self.req_socket.recv_pyobj()

        # Check for success. Subscribe to topic regardless
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        if response['type'] == 'sub_reg' and response['result'] is True:
            return response['history']
        else:
            return None

    '''
    Function that the subscriber can use to wait on next available message (Blocking recv essentially)
    topic: Topic that the subscriber wants to wait for
    value: ???
    '''
    def notify(self, topic, value, timeout_ms=0):
        # print("Client waiting for message")

        # Set absolute time limits for timeout (pyzmq uses relative timeouts)
        start_time = int(round(time.time() * 1000))
        end_time = start_time + timeout_ms

        # Loop until desired message topic arrives
        while True:
            # If timeout specified, determine remaining time. Otherwise, block indefinitely
            if timeout_ms > 0:
                remaining_time = end_time - int(round(time.time() * 1000))
                if remaining_time <= 0:
                    return None
            else:
                remaining_time = -1
            self.sub_socket.RCVTIMEO = remaining_time

            # Try to recv message. Catch timeout
            try:
                recved_topic = self.sub_socket.recv_string()
            except zmq.error.Again:
                return None

            # Desired topic arrived. Read message and return.
            if recved_topic == topic:
                msg = self.sub_socket.recv_pyobj(zmq.NOBLOCK)
                # print(msg)
                return msg

            # Handle special broker topic regardless of desired topic
            elif recved_topic == "BROKER_CMD":
                msg = self.sub_socket.recv_pyobj()

                # Send back ping in response to heartbeat
                if msg['type'] == 'heartbeat':
                    ping = {'type': 'ping', 'addr': self.ip}
                    self.req_socket.send_pyobj(ping)
                    response = self.req_socket.recv_pyobj()

            # Discard all other messages
            else:
                self.sub_socket.recv_pyobj()

    def shutdown_broker(self):
        print("Sending broker shutdown command")

        values = {'type':'shutdown'}
        self.req_socket.send_pyobj(values)
        response = self.req_socket.recv_pyobj()

        if response['result'] == True:
             print("Shutdown successful")
        else:
            print("Shutdown FAILED")

        return response['result']
