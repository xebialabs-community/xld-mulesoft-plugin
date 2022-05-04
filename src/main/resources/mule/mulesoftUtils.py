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


def get_token_user(username, password):
    print("In mulesoftUtils.get_token_user")
    content = {
    "username": username,
    "password": password
    }
    content = json.dumps(content)
    url = "https://anypoint.mulesoft.com/accounts/login"
    headers = {'content-type': 'application/json'}
    response = requests.request("POST", url , data = content, headers = headers)
    if response.raise_for_status():
        raise Exception("Failed to get token for user. Server returned %s.\n%s" % (response.status_code, response.reason))
    else:
        responseJson = response.json()
        return responseJson['access_token']

def get_token_conn_app(username, password):
    print("In mulesoftUtils.get_token_conn_app")
    content = {
    "client_id": username,
    "client_secret": password,
    "grant_type" : "client_credentials"
    }
    content = json.dumps(content)
    url = 'https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token'
    headers = {'content-type': 'application/json'}
    response = requests.request("POST", url , data = content, headers = headers)
    if response.raise_for_status():
        raise Exception("Failed to get token for connected app. Server returned %s.\n%s" % (response.status_code, response.reason))
    else:
        responseJson = response.json()
        return responseJson['access_token']

def create_env(id, name, token, repositoryService, metadataService):
    print("Debug - id = %s, name = %s, " % (id, name))
    envUrl = "https://anypoint.mulesoft.com/accounts/api/organizations/%s/environments" % id
    authHeader = {"Authorization":"Bearer " + token}
    envResponse = requests.get(envUrl, headers=authHeader)
    if envResponse.raise_for_status():
        raise Exception("Failed to get environments. Server returned %s.\n%s" % (envResponse.status_code, envResponse.reason))
    
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

def create_deploy_payload_cloudhub(domain, muleVersion, region, Enabled, numWorkers, workers, prop):
    print("in create_deploy_payload_cloudhub")
    payload = {
                'appInfoJson': {
                    "domain": domain,
                    "muleVersion" : {"version":muleVersion}, #infra
                    "region" : region, #infra"  ca-c1.cloudhub.io"#
                    "monitoringEnabled": True,
                    "monitoringAutoRestart" : Enabled,
                    "workers": {"amount": numWorkers, "type": workers},
                    "loggingNgEnabled": True,
                    "persistentQueues": False,
                    "properties": prop
                    },
                'autoStart': "true",
                }
    # Convert inner appInfojson to string
    # The following is done to keep Mulesoft happy. Otherwise you get 'invalid JSON' error
    payload['appInfoJson']= json.dumps(payload['appInfoJson'])
    return payload

def create_deploy_payload_rtf(deployed, deploymentIdObj, orgId):
    print("in create_deploy_payload_rtf")
    # gather variable values
    appName = deployed.name
    print("deployed.name = %s" % appName)
    muleEnv = deployed.container.envName
    print("muleEnv = %s" % muleEnv)
    domain = deployed.domain
    packaging = deployed.packaging
    applicationVersion = deployed.applicationVersion
    clusteringEnabled = deployed.clusteringEnabled == "true"
    clustered = deployed.clustered == "true"
    lastMileSecurity = deployed.lastMileSecurity ==  "true" 
    cpuMax = deployed.cpuMax
    cpuReserved  = deployed.cpuReserved
    memoryReserved = deployed.memoryReserved
    publicUrl = deployed.publicUrl
    replicationFactor = deployed.replicationFactor
    replicas = deployed.replicas
    MulesoftVersion = deployed.MulesoftVersion
    provider = deployed.provider
    targetId = deployed.targetId

    # If this is a modify operation, replace values with those discovered in 'get deployment ids'
    if deploymentIdObj["name"] != "":
        provider = deploymentIdObj["provider"]
        targetId = deploymentIdObj["targetId"]
        print("This is a modify operation")
        print("Replaced provider and targetId with values retrieved from getDeploymentIds. provider = %s, targetId = %s" % (provider, targetId))

    payload = {
            "application": {
                "configuration": {
                    "mule.agent.application.properties.service": {
                        "applicationName": appName,
                        "properties": {
                            "mule.env": muleEnv 
                        }
                    }
                },
                "desiredState": "STARTED", 
                "ref": {
                    "artifactId": domain,
                    "groupId": orgId, 
                    "packaging": packaging, 
                    "version": applicationVersion 
                }
            },
            "name": domain, 
            "target": {
                "deploymentSettings": {
                    "clusteringEnabled": clusteringEnabled,
                    "clustered": clustered, 
                    "cpuMax": cpuMax, 
                    "cpuReserved": cpuReserved, 
                    "lastMileSecurity": lastMileSecurity, 
                    "memoryReserved": memoryReserved, 
                    "publicUrl": publicUrl,
                    "replicationFactor": replicationFactor,
                    "runtimeVersion": MulesoftVersion
                },
                "provider": provider,
                "replicas": replicas,
                "targetId": targetId
            }
        }
    # The following is done to keep Mulesoft happy. Otherwise you get 'invalid JSON' error
    payload= json.dumps(payload)
    return payload


def get_deployment_id_obj(token, orgId, envId, domain):
    print("in get_deployment_ids")
    deployIdObj = {"name": "",
                    "id": "",
                    "provider": "",
                    "targetId": ""
                    }
    url = "https://anypoint.mulesoft.com/hybrid/api/v2/organizations/%s/environments/%s/deployments" % (orgId, envId)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    response = requests.request("GET", url, headers=headers)
    if response.raise_for_status():
                raise Exception("Failed to retrieve deployment ids. Server returned %s.\n%s" % (response.status_code, response.reason))
    else:
        response = response.json()
        if response["items"]:
            for i in response['items']:
                if i['name'] == domain:
                    print("FOUND Deployment ID %s" % str(i))
                    deployIdObj["name"] = i["name"]
                    deployIdObj["id"] = i["id"]
                    deployIdObj["provider"] = i["target"]["provider"]
                    deployIdObj["targetId"] = i["target"]["targetId"]
    print("Finished creating deployIdObj %s " % deployIdObj)
    return deployIdObj

