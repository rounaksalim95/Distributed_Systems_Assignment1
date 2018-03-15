# Test Cases
Each test case should be contained in a subdirectory of this directory named "test<test_number>".
Each test case directory should contain a configuration file "config.json" as well as a brief "README.md" describing the purpose and expected results of the test case.
Test results will be stored in one log file for each node, "log<node_number>.txt", within the subdirectory of the particular test case when "run_tests" is executed.

The number of nodes involved in each test case is configurable.
Each node should have a corresponding script file named "node<node_number>.json".
Currently, the Broker must be run on node1 so the "node1.json" should always contain just the following command:

    { 
        "middlewareType":"broker"
    }

## config.json

config.json needs to define two values:
1) NUM_NODES
2) MAX_RUNTIME

"NUM_NODES" is the number of nodes in your test, and you should have a matching number of test<node number>.json's in the "/tests" directory.

"MAX_RUNTIME" should be an integer, a couple seconds longer than the largest sum of "wait" and "notify" statements in any test json. This gives your test ample time to run before we tear down the mininet setup.

Currently, the topology of the mininet network used for testing is NOT configurable.
The topology is a tree of depth 1 with NUM_NODES nodes (ie. All nodes connected by a single switch).

Example config.json:

    {
      "NUM_NODES":4,
      "MAX_RUNTIME":25
    }


## node.json

Each node should have its own script containing the commands to be executed. 
This script should be named "node<node_number>.json" 

The provided test case 1 shows history being returned and a publisher with lower ownership strength taking over when a publisher with higher ownership strength times out.

Node command scripts are json files named "node<node number>.json". 
We only support at most 9 nodes right now. 

They have two dict-like entries:
 1) "middlewareType"
 2) "commands"
  
"middlewareType" can hold value either "client" or "broker". 

"commands" holds a list of sublists, where each sublist is a command to be run by a client. 
A "broker" test script doesn't need a "command" list, the broker just starts and blocks. Possible commands are:
1) wait - "w"
2) register publisher - "rp"
3) register subscriber - "rs"
4) publish - "p"
5) notify/receive - "n"
6) shutdown broker - "sb"

Each command "sublist" format (ie. command arguments) is specified in test.py.

***IMPORTANT***: This longest json should also end with a command "sb", which stops the broker gracefully, otherwise you may not be able to view the broker log.

Each node produces a log called "log<node number>.txt", in this directory.

Example nodeX.json:

    {
        "middlewareType":"client",
        "commands": [
            ["w",8],
            ["rp","topic1",4],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["p","topic1",-1],
            ["w",1],
            ["sb"]
        ]
    }

