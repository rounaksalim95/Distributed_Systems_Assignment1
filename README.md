# Distributed Systems Assignment 1
Publish/Subscribe event service that uses a central Broker as a middleman for all messaging between Clients (publishers and subscribers).

The library is implemented entirely in the middleware.py file. 
The API consists of the two classes "Broker" and "Client".

A single Broker accepts incoming messages on port 7777 and sends messages out to subscribers on port 7778.
All messages sent by a publisher are directed to the Broker.
The Broker maintains active publishers, topics, ownership strengths, and histories.
When the Broker receives a message from a publisher, it routes this message to all subscribers of the message topic as appropraite.

When an instance of "Client" is created, the client automatically identifies itself to the broker.
The Client constructor will block until this identification is complete (typically <1 second on mininet).
Once this completes, the Client may register as many publishers and subscribers with the Broker as desired.
Each publisher registration should include the topic, ownership strength, and history of that publisher.
Each subscriber registration should include the topic and desired amount of history.
If the desired history is available, the Broker will respond with a list containing the history.

To use the library: 
1) Spawn one instance of "Broker" on any node.
2) Spawn as many instances of "Client" as desired on other nodes in the network, and specify the IP address of the Broker to each Client.
3) Each Client node may then register as many publishers and subscribers as desired and begin publishing/receiving messages.
4) See comments in middleware.py for a more detailed description of each available function.
 

## Requirements
* python3
* pyzmq
* sortedcontainers
* Mininet
* python2 (for testing)

## Testing
We use a script-based testing framework to support testing a variety of functions/scenarios. 
Test cases are contained in the "tests" folder.

The command "sudo ./run_tests" will run all tests and store the result of each test into log files in the directory of that test.

More information about the test scripts is given in the "tests" directory readme.