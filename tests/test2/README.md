### Test Objective
Test 2 shows the response of subscriber, when two publisher, which have same strength, publish topic at same time.
### Expected Output
Node 3 and Node 5 are subscriber in this test.
log3.txt and log4.txt should show the history list:


Node 3 should then receive the following series of messages:

Notify received:  6
Notify received:  7
Notify received:  8
Notify received:  9
Notify received:  10
Notify received:  10
Notify received:  10
Notify received:  10
Notify received:  10
Notify received:  -1

Node 5 should then receive the following series of messages:
Notify received:  7
Notify received:  8
Notify received:  9
Notify received:  10
Notify received:  10
Notify received:  10
Notify received:  10
Notify received:  10
Notify received:  -1
Notify received:  -1



Nodes 2 and 4 should each publish a series of approximately 10 messages.

Node 1 is the broker.

All log files should be error-free.
