# Copyright 2022 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import json
import requests
from com.xebialabs.deployit.plugin.api.reflect import Type
# Fixes some issues with TLS
import mule.mulesoftUtils as mulesoftUtils 

# Get Token
if thisCi.serviceType == "Runtime Fabric" or thisCi.serviceType == "CloudHub - Use OAuth 2.0":
    print("In OAuth block")
    token = mulesoftUtils.get_token_conn_app(thisCi.username, thisCi.password)
    print('Got OAuth token')
else:
    print("In Cloudhub Auth block")
    token = mulesoftUtils.get_token_user(thisCi.username, thisCi.password)
    print ('Got Cloudhub token')

# Download the user/org profile and find out what environments we have

authHeader = {"Authorization":"Bearer " + token}
profile_uri = 'https://anypoint.mulesoft.com/accounts/api/profile'
profileResponse = requests.get(profile_uri, headers=authHeader)
profileResponseJson = profileResponse.json()

if profileResponse.status_code != 200 :
    print('Status:', profileResponse.status_code, 'Content: ', profileResponse.content)
    raise Exception("Failed to get profile. Server returned %s.\n%s" % (profileResponse.status_code, profileResponse.reason))

# We don't actually need the Org ID right now, but it's needed for some other API requests
# so we'll save it for later use, while we have it.
try :
    thisCi.MasterOrgId = profileResponseJson['organizationId']; # these keys are case sensitive
    thisCi.MasterOrgDomain = profileResponseJson['organization']['domain']; # we're assuming we only have one org
    #Update the mule.Mulesoft base container
    repositoryService.update(thisCi.id, thisCi)
except :
    print ("Warning: Problem retrieving or saving the organizationId.")

# Create the domains
for domainItem in profileResponseJson['contributorOfOrganizations']:
    print ('Name: ' + domainItem['name'] + '\r\n') # Debugging
    print ('ID: ' + domainItem['id'] + '\r\n')# Debugging
    newCiId = thisCi.id + '/' + domainItem['name']
    print ('Adding: ' + newCiId)
    if repositoryService.exists(newCiId) :
        print ('   ' + domainItem['name'] + ' already exists, skipping.')
        mulesoftUtils.create_env(str(domainItem['id']), str(newCiId), token, repositoryService, metadataService, thisCi.serviceType)
    else :
        newTeCi = metadataService.findDescriptor(Type.valueOf('mule.Mulesoft.Domain')).newInstance(newCiId)
        newTeCi.OrgDomain = domainItem['name']
        newTeCi.OrgId = domainItem['id']
        repositoryService.create(newCiId, newTeCi)
        try:
            mulesoftUtils.create_env(str(domainItem['id']), str(newCiId), token, repositoryService, metadataService, thisCi.serviceType)
        except Exception as e:
            print("Unable to retrieve envionments for this domain - %s, will delete this domain and continue" % str(newCiId))
            print("Exeception = %s" % e)
            repositoryService.delete(newCiId)
        

print ('Done.')
