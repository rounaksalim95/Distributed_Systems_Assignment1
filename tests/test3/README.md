### Test Objective 
Test 3 shows the one-to-one situation. Node 2 is a subscriber and Node 3 is the publisher.

### Expected Output
Node 2 should receive the following series of messages:

    Notify received:  6
    Notify received:  7
    Notify received:  8
    Notify received:  9
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10

Nodes 3 should publish a series of approximately 10 messages.

Node 1 is the broker.

All log files should be error-free.  
