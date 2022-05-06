# Copyright 2022 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import json
import requests
from com.xebialabs.deployit.plugin.api.reflect import Type
# Fixes some issues with TLS
import mule.mulesoftUtils as mulesoftUtils
import os


# Get Bearer Token
if thisCi.masterDomain.serviceType == "Runtime Fabric" or thisCi.masterDomain.serviceType == "CloudHub - Use OAuth 2.0":
    # Hit the login endpoint to get a bearer token
    token = mulesoftUtils.get_token_conn_app(thisCi.masterDomain.username, thisCi.masterDomain.password)
    print('Got OAuth token')
else:
    print("In Cloudhub Auth block")
    token = mulesoftUtils.get_token_user(thisCi.masterDomain.username, thisCi.masterDomain.password)
    print ('Got Cloudhub token')


mulesoftUtils.create_env(thisCi.OrgId, thisCi.id, token, repositoryService, metadataService, thisCi.masterDomain.serviceType)

print('Done')
