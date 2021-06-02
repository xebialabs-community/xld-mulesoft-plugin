# Copyright 2020 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import json
import requests
import requests.utils
from com.xebialabs.deployit.plugin.api.reflect import Type
# Fixes some issues with TLS
import os

def get_env(url, id, name):
    global token
    envUrl = "/accounts/api/organizations/%s/environments" % id
    envUrl = url + envUrl
    authHeader = {"Authorization":"Bearer " + token};
    profileResponse = requests.get(envUrl, headers=authHeader);
    logger.info("-------------------------")
    logger.info(str(envUrl))
    profileResponseJson = profileResponse.json();
    for envItem in profileResponseJson['data']:

        print 'Name: ' + envItem['name'] + '\r\n' # Debugging
        print 'ID: ' + envItem['id'] + '\r\n' # Debugging
        newCiId = name + '/' + envItem['name'];
        print 'Adding: ' + newCiId;

        if repositoryService.exists(newCiId) :
            print '   ' + envItem['name'] + ' already exists, skipping.';
        else :
            newTeCi =metadataService.findDescriptor(Type.valueOf('mule.Mulesoft.Domain.TargetEnvironment')).newInstance(newCiId);
            newTeCi.envName = envItem['name'];
            newTeCi.envId = envItem['id'];
            repositoryService.create(newCiId, newTeCi);

# os.environ['REQUESTS_CA_BUNDLE'] = 'ca.pem';

cert = thisCi.caCert

# path = str(path)
# path = '/opt/xebialabs/xl-deploy-server/'
# file = path + "ca.pem"
# file = "ca.pem"
# file = str(file)
# text_file = open(file, "w")
# text_file.write(cert)
# text_file.close()
# global os.environ['REQUESTS_CA_BUNDLE']
os.environ['REQUESTS_CA_BUNDLE'] = "ca.pem"
# os.environ['REQUESTS_CA_BUNDLE'] = file

login_uri = thisCi.url + '/accounts/login';
profile_uri = thisCi.url + '/accounts/api/profile';

# thisCi should be in our context

print "Login URI: " + login_uri + '\r\n';
print "Username: " + thisCi.username + '\r\n';

# Hit the login endpoint to get a bearer token

authText = '{ "username" : "' + thisCi.username + '", "password" : "' + thisCi.password + '" }';
jsonHeader = {"Content-Type":"application/json"}; # Optional with this API, but good practice
authResponse = requests.post(login_uri, headers=jsonHeader, data=authText);
authResposeJson = authResponse.json();
token = str(authResposeJson['access_token']);

if authResponse.status_code != 200 :
    print('Status:', authResponse.status_code, 'Content: ', authResponse.content);
    raise exception;

# Debugging data
# print authResponse.content;
# print 'Got token: ' + token + '\r\n';

# Download the user/org profile and find out what environments we have

authHeader = {"Authorization":"Bearer " + token};
profileResponse = requests.get(profile_uri, headers=authHeader);
profileResponseJson = profileResponse.json();

if profileResponse.status_code != 200 :
    print('Status:', profileResponse.status_code, 'Content: ', profileResponse.content);
    raise exception;

# Debug
# print 'response >> ';
# print profileResponse.content;
# print '\r\n';

# We don't actually need the Org ID right now, but it's needed for some other API requests
# so we'll save it for later use, while we have it.
try :
    thisCi.MasterOrgId = profileResponseJson['organizationId']; # these keys are case sensitive
    thisCi.MasterOrgDomain = profileResponseJson['organization']['domain']; # we're assuming we only have one org
    repositoryService.update(thisCi.id, thisCi);
except :
    print "Warning: Problem retrieving or saving the organizationId.";

for envItem in profileResponseJson['contributorOfOrganizations']:
    # To do: build CIs
    print 'Name: ' + envItem['name'] + '\r\n' # Debugging
    print 'ID: ' + envItem['id'] + '\r\n' # Debugging
    newCiId = thisCi.id + '/' + envItem['name'];
    print 'Adding: ' + newCiId;
    if repositoryService.exists(newCiId) :
        print '   ' + envItem['name'] + ' already exists, skipping.';
        get_env(str(envItem['id']), str(newCiId))
    else :
        newTeCi = metadataService.findDescriptor(Type.valueOf('mule.Mulesoft.Domain')).newInstance(newCiId);
        newTeCi.OrgDomain = envItem['name'];
        newTeCi.OrgId = envItem['id'];
        repositoryService.create(newCiId, newTeCi);
        get_env(thisCi.url, str(envItem['id']), str(newCiId))

print 'Done.'
