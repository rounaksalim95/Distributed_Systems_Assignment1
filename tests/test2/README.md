### Test Objective
Test 2 shows the response of subscriber, when two publisher, which have same strength, publish topic at same time.
### Expected Output
Node 3 and Node 5 are subscriber in this test.
log3.txt and log4.txt should show the history list:


Node 3 should then receive a mixed set of values (containing either values from 6 - 10 or -1). Example output:

    Notify received:  -1
    Notify received:  7
    Notify received:  -1
    Notify received:  8
    Notify received:  9
    Notify received:  10
    Notify received:  10
    Notify received:  -1
    Notify received:  -1
    Notify received:  10

Similarly for Node 5:
    
    Notify received:  7
    Notify received:  -1
    Notify received:  8
    Notify received:  9
    Notify received:  10
    Notify received:  10
    Notify received:  -1
    Notify received:  -1
    Notify received:  10
    Notify received:  -1
    
Small delays in the mininet network may change the exact sequence of values received.
However, any value received at Node 3 should also be received at Node 5 with an offset of 1.
This is because Node 5 starts 1 time slot after Node 3.
Both 3 and 5 are subscribed to the same topic, so anything one node receives the other must also receive

Nodes 2 and 4 should each publish a series of approximately 10 messages.

Node 1 is the broker.

All log files should be error-free.
