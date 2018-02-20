# Requires sortedcontainers for maintaining sorted list efficiently (pip install sortedcontainers)

import middleware
from sortedcontainers import SortedListWithKey

# Dictionary that topics to sorted lists that keep track of the avaialable publishers (sorted on ownership strength)
topics_dict = {}

test_address = "tcp://*:7777"
# Start listening for publishers and subscribers 
socket = middleware.start_listening(test_address)

# Some helper functions 
'''
Function that adds the provided publisher to topics_dict
publisher_info: Information on the publisher 
Publisher is of the form : (address, ownership_strength, history)
'''
def add_publisher(publisher_info):
    print(publisher_info)
    topic = publisher_info['topic']
    publisher = (publisher_info['addr'], int(publisher_info['ownStr']), int(publisher_info['history']))
    if topic in topics_dict:
        topics_dict[topic].add(publisher)
    else: 
        topics_dict[topic] = SortedListWithKey(key=lambda x: -x[1])
        topics_dict[topic].add(publisher)

'''
Function that searches for the best available publisher based on the requirements of the subscriber 
topic: Topic that the subscriber wants to subscribe to 
history: Minimum history that the subscriber is looking for 
'''
def find_publisher(topic, history): 
    if (topic in topics_dict and len(topics_dict[topic]) > 0):
        for lst in topics_dict[topic]: 
            if lst[2] >= history:
                return lst[0]
    
    # Return None if no publishers for the topic or not enough history maintained 
    return None

# Listen to incoming publisher and subscriber requests 
while True: 
    msg_dict = socket.recv_pyobj()

    # If publisher makes request then add them to topics_dict appropriately 
    if msg_dict['type'] == 'pub':
        add_publisher(msg_dict)
        socket.send(b"Added publisher")
    elif msg_dict['type'] == 'sub':
        address = find_publisher(msg_dict['topic'], msg_dict['history'])
        if address != None: 
            socket.send(address.encode())   # encode() uses utf-8 encoding by default 
        else:
            socket.send(b"None")