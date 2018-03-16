### Test Objective
Test 4 shows the one-to-two situation. Node 2 and Node 4 are a subscribers and Node 3 is the publisher.
log2.txt and log4.txt should show the history list:

Node 2 should then receive the following series of messages:


Node 4 should then receive the following series of messages:
Notify received:  9
Notify received:  10
Notify received:  10





Nodes 3  should each publish a series of approximately 10 messages.

Node 1 is the broker.

All log files should be error-free.
