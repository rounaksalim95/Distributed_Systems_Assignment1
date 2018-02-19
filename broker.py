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
    topic = publisher_info[2]
    publisher = (publisher_info[1], int(publisher_info[3]), int(publisher_info[4]))
    if topic in topics_dict:
        topics_dict[topic].add(publisher)
    else: 
        topics_dict[topic] = SortedListWithKey(key=lambda x: -x[1])
        topics_dict[topic].add(publisher)


# Listen to incoming publisher and subscriber requests 
while True: 
    message = socket.recv().decode()    # decode uses utf-8 encoding by default 
    parts = message.split(',')
    # If publisher makes request then add them to topics_dict appropriately 
    if (parts[0] == 'pub'): 
        add_publisher(parts)
        socket.send(b"Added publisher")
        print(topics_dict)