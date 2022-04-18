# Copyright 2022 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import json
import requests
import requests.utils
from com.xebialabs.deployit.plugin.api.reflect import Type
# Fixes some issues with TLS
import os

os.environ['REQUESTS_CA_BUNDLE'] = 'ca.pem'


def get_token_user(username, password, ciUrl):
    print("In mulesoftUtils.get_token_user")
    content = {
    "username": username,
    "password": password
    }
    content = json.dumps(content)
    url = ciUrl + "/accounts/login"
    headers = {'content-type': 'application/json'}
    response = requests.request("POST", url , data = content, headers = headers)
    if response.raise_for_status():
        raise Exception("Failed to get token for user. Server returned %s.\n%s" % (response.status_code, response.reason))
    else:
        response = response.json()
        return response['access_token']

def get_token_conn_app(username, password, ciUrl):
    print("In mulesoftUtils.get_token_conn_app")
    content = {
    "client_id": username,
    "client_secret": password,
    "grant_type" : "client_credentials"
    }
    content = json.dumps(content)
    url = ciUrl + '/accounts/api/v2/oauth2/token'
    headers = {'content-type': 'application/json'}
    response = requests.request("POST", url , data = content, headers = headers)
    if response.raise_for_status():
        raise Exception("Failed to get token for connected app. Server returned %s.\n%s" % (response.status_code, response.reason))
    else:
        response = response.json()
        return response['access_token']

def create_env(id, name, token, repositoryService, metadataService):
    print("Debug - id = %s, name = %s, " % (id, name))
    envUrl = "https://anypoint.mulesoft.com/accounts/api/organizations/%s/environments" % id
    authHeader = {"Authorization":"Bearer " + token}
    envResponse = requests.get(envUrl, headers=authHeader)
    envResponseJson = envResponse.json()
    for envItem in envResponseJson['data']:
        print('Name: ' + envItem['name'] + '\r\n') # Debugging
        print('ID: ' + envItem['id'] + '\r\n') # Debugging
        newCiId = name + '/' + envItem['name']
        print('Adding: ' + newCiId)

        if repositoryService.exists(newCiId) :
            print('   ' + envItem['name'] + ' already exists, skipping.')
        else :
            newTeCi =metadataService.findDescriptor(Type.valueOf('mule.Mulesoft.Domain.TargetEnvironment')).newInstance(newCiId)
            newTeCi.envName = envItem['name']
            newTeCi.envId = envItem['id']
            repositoryService.create(newCiId, newTeCi)

def create_deploy_payload_cloudhub():
    print("in create_deploy_payload_cloudhub")

def create_deploy_payload_rtf():
    print("in create_deploy_payload_rtf")

    payload = {
            "name": "{{name}}",
            "labels": [
                "beta"
            ],
            "target": {
                "provider": "MC",
                "targetId": "{{targetId}}",
                "deploymentSettings": {
                "resources": {
                    "cpu": {
                    "reserved": "{{cpuReserved}}",
                    "limit": "{{cpuLimit}}"
                    },
                    "memory": {
                    "reserved": "{{memReserved}}",
                    "limit": "{{memLimit}}"
                    }
                },
                "clustered": "{{clusteredBoolean}}",
                "runtimeVersion": "{{runtimeVersion}}"
                }
            },
            "application": {
                "desiredState": "STARTED",
                "configuration": {
                    "mule.agent.application.properties.service": {
                        "applicationName": "{{name}}",
                        "properties": {
                        "https.port": "8081"
                        }
                    }
                }
            }
            }

