# Distributed_Systems_Assignment1
PUB SUB Event Service

## Requirements
* python3
* pyzmq
* sortedcontainers
* Mininet

## Testing
Create a test script for each node, see notes in tests/test.py
Once your scripts are created, run "sudo ./run_test"

Our supplied scripts show history being returned and a publisher with lower ownership strength taking over when a publisher with higher ownership strength times out.

This file has to be modified to fit your test a little bit. Near the top are two macros, "NUM_NODES" and "MAX_RUNTIME".

"NUM_NODES" is the number of nodes in your test, and you should have a matching number of test<node number>.json's in the "/tests" directory.

"MAX_RUNTIME" should be an integer, a couple seconds longer than the largest sum of "wait" and "notify" statements in any test json. This gives your test ample time to run before we tear down the mininet setup.

IMPORTANT: This longest json should also end with a command "sb", which stops the broker gracefully, otherwise you may not be able to view the broker log.

Test scripts are json files named "test<node number>.json". We only support at most 9 nodes right now. They have two dict-like entries, "middlewareType" and "commands". "middlewareType" can hold value either "client" or "broker". "commands" holds a list of sublists, where each sublist is a command to be run by a client. A "broker" test script doesn't need a "command" list, the broker just starts and blocks.

Each command "sublist" format is specified in test.py.

Each node produces a log called "log<node number>.txt", in this directory.
