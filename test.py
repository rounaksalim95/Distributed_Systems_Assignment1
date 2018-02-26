# Our test scripts support the following commands, with their expected formats
# - Register Publisher:
#     ["rp",<topic string>,<optional: strength>,<optional: history>]
#     NOTE: To save the user from writing dicts, we require that a strength
#     be given if a history is to be given
#
# - Register Subscriber:
#     ["rs",<topic string>,<optional: history>]
#
# - Publish:
#     ["p",<topic string>,<content>]
#
# - Notify:
#     ["n",<topic string>,<optional: value(not used)>]
#
# - Wait:
#     ["w",<value(float or int)>]
#     Used to let time elapse in test script, just a time.sleep()
#

# Each test script must be named "test<node number>.py", where the node number is the last digit of the mininet node's IP (right now only supports 1-9)
# A test script must also have the following key-value pair:
#
#     "middlewareType":<"client" | "broker">
#
# with the appropriate middleware you are trying to start on that node.

from middleware import Client, Broker
import sys
import json
import time

if len(sys.argv) != 2:
    print("ERROR: test.py wasn\'t given exactly 1 argument")
    sys.exit(-1)

myIP = sys.argv[1]

print("Test.py started, my IP is %s" % myIP)

testScript = json.load(open('./tests/test'+myIP[-1]+'.json'))

if testScript['middlewareType'] == 'broker':
    broker = Broker(pub_addr = 'tcp://'+myIP+':7778',rep_addr = 'tcp://'+myIP+':7777')
    print("Starting Broker...")
    broker.run()

elif testScript['middlewareType'] == 'client':
    client = Client(req_addr = 'tcp://'+myIP+':7777',sub_addr = 'tcp://'+myIP+':7778')
    print('Starting Client...')

    for command in testScript['commands']:

        # register publisher
        if command[0] == 'rp':

            topic =    command[1]
            strength = command[2] if len(command) >= 3 else 0
            hist =     command[3] if len(command) >= 4 else 0

            results = client.register_pub(topic,strength,hist)
            print(results)

        # register subscriber
        elif command[0] == 'rs':

            topic = command[1]
            hist  = command[2] if len(command) >= 3 else 0

            results = client.register_sub(topic,hist)
            print(results)

        # publish
        elif command[0] == 'p':

            topic = command[1]
            content = command[2]

            results = client.publish(topic,content)
            print(results)

        # notify
        elif command[0] == 'n':

            topic = command[1]
            val = command[2] if len(command) >= 3 else 0

            results = client.notify(topic,val)
            print(results)

        # pause, in seconds
        elif command[0] == 'w':
            if len(command) == 2:
                time.sleep(command[1])
sys.exit(0)
