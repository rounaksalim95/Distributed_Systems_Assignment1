### Test Objective
Test 4 shows the one-to-two situation. Node 2 and Node 4 are a subscribers and Node 3 is the publisher.
log2.txt and log4.txt should show the history list:

### Expected output

Node 2 should receive the following series of messages:

    Notify received:  7
    Notify received:  8
    Notify received:  9
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10

Node 4 should receive the following series of messages:

    Notify received:  8
    Notify received:  9
    Notify received:  10

Nodes 3 should publish a series of approximately 10 messages.

Node 1 is the broker.

All log files should be error-free.
