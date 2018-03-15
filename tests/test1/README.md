### Test Objective 
Test 1 shows history being returned and a publisher with lower ownership strength taking over when a publisher with higher ownership strength times out.

### Expected Output
Node 3 is the only subscriber in this test. 
log3.txt should show that Node 3 registers a subscriber and receives the history list: 
    
    Subscriber registration received history:  deque([4, 5, 6], maxlen=3)
    
Node 3 should then receive the following series of messages:

    Notify received:  8
    Notify received:  9
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  10
    Notify received:  -1
    Notify received:  -1
    Notify received:  -1 

Nodes 2 and 4 should each publish a series of approximately 10 messages.
Node 2 is the higher priority publisher, but stops publishing before Node 4.
Once Node 2 stops, Node 3 will begin receiving '-1' messages from Node 4.

Node 1 is the broker.

All log files should be error-free.  
