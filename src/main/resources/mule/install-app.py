# Copyright 2022 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import mule.mulesoftClient
reload(mule.mulesoftClient)
from mule.mulesoftClient import mulesoftClient
import time

client = mulesoftClient.create_client_from_deployed(deployed)
print("Deploying application...")
print("servertype = %s" % client.serviceType)
domain = str(deployed.domain)
workers = str(deployed.workers)
Enabled = deployed.monitoringAutoRestart
muleVersion = deployed.MulesoftVersion
numWorkers = deployed.numWorkers
region = deployed.region
appProperties = deployed.appProperties
client.deploy_package(domain, workers, Enabled, muleVersion, numWorkers, region, appProperties, deployed.file.path)
print("Checking deploy status")
isDeployed = False
i = 0
while(not isDeployed):
    time.sleep(deployed.wait_time)
    isDeployed = client.check_is_deployed(domain)
    if i == int(deployed.attempts):
        # Timeout Error
        isDeployed = True
        print("TIME OUT CHECKING STATUS - DEPLOY IS NOT CONFIRMED")
    i += 1
print("Finished deploying application.") 

