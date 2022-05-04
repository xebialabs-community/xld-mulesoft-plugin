# Copyright 2022 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import requests
import time

import mule.mulesoftClient
reload(mule.mulesoftClient)
from mule.mulesoftClient import mulesoftClient

client = mulesoftClient.create_client_from_deployed(previousDeployed)
print ("undeploying application")
domain = str(previousDeployed.domain)
client.undeploy_packageRTF(domain)
print("Checking undeploy status")
stillDeployed = True
i = 0
while(stillDeployed):
    time.sleep(previousDeployed.wait_time)
    stillDeployed = client.check_is_deployedRTF(domain)
    if i == int(previousDeployed.attempts):
        # Timeout Error
        stillDeployed = False
        print("TIME OUT CHECKING STATUS - UNDEPLOY IS NOT CONFIRMED")
    i += 1

print ("Done.")
