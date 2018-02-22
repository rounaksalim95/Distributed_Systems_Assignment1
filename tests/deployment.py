import os

import zopkio.adhoc_deployer as adhoc_deployer
import zopkio.runtime as runtime

# runs at the very beginning
def setup_suite():
    # path to client executable
    client_exec = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../client.py")

    global client_deployer
    client_deployer = adhoc_deployer.SSHDeployer()

# runs before each individual test
def setup():

# runs after each individual test, for cleaining up
def teardown():

# runs at the very end
def teardown_suite():
