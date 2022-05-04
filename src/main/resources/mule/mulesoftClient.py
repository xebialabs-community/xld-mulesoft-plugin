# Copyright 2022 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



import time
import json
import requests
import mule.mulesoftUtils as mulesoftUtils
import os

os.environ['REQUESTS_CA_BUNDLE'] = 'ca.pem'

import org.slf4j.LoggerFactory as LoggerFactory

logger = LoggerFactory.getLogger("Mulesoft")

class mulesoftClient(object):
    def __init__(self, username, password, orgId, envId, serviceType):
        self.username = username
        self.password = password
        self.serviceType = serviceType
        self.token = self.get_token()   # '20db92f1-36f7-4ae6-b4ce-5ecbca7f1798'
        self.OrgId = orgId
        self.EnvId = envId
        

    @staticmethod
    def create_client_from_deployed(deployed):
        mmc = deployed.container
        return mulesoftClient(mmc.orgLevelDomain.masterDomain.username, mmc.orgLevelDomain.masterDomain.password, mmc.orgLevelDomain.OrgId, mmc.envId, mmc.orgLevelDomain.masterDomain.serviceType)

###### DEPLOY ##########
    
    def deploy_package(self, domain, workers, Enabled, muleVersion, numWorkers, region, appProperties, file_path):
        httpMethod = "POST"
        # Handle properties obj
        prop = {}
        for (k,v) in appProperties.items() :
            prop[k] = v
        # Handle workers obj
        try:
            workers = json.loads(workers)
        except:
            raise Exception("Configuration error in Deploy for mule application RTF Deploy JSON. Value must be in JSON format.")

        if (workers.get('name') is None) or (workers.get('weight') is None) or (workers.get('cpu') is None) or (workers.get('memory') is None):
            print("This app is to be deployed to Cloudhub. Cloudhub Works JSON must contain values for name, weight, cpu and memory.")
            print("current object: %s" % json.dumps(workers))
            # example {"name":"Micro","weight":"0.1","cpu":"0.1 vCores", "memory":"500 MB memory"}
            raise Exception("Configuration error in Deploy for mule application Cloudhub Deploy JSON.") 
        url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"
        # get payload
        payload = mulesoftUtils.create_deploy_payload_cloudhub(domain, muleVersion, region, Enabled, numWorkers, workers, prop)
        headers = {
        'x-anypnt-env-id': str(self.EnvId),
        'x-anypnt-org-id': str(self.OrgId),
        'Authorization': 'Bearer %s' % self.token
        }
        files = [
        ('file', open(file_path,'rb'))
        ]
        # Deploy
        print("About to deploy, payload = %s" % json.dumps(payload))
        response = requests.request( httpMethod, url, headers=headers, data = payload, files = files)
    
        if response.status_code != 200: #  or response.raise_for_status()
            print (response.status_code)
            print (response.text)
            raise Exception("Failed to deploy. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            try :
                responseJson = response.json()
            except :
                print("Could not decode JSON")
        print (response.status_code)
        print (response.text)


    def deploy_or_modify_packageRTF(self, deployed):
        httpMethod = "POST"

        deploymentIdObj = mulesoftUtils.get_deployment_id_obj(self.token, self.OrgId, self.EnvId, deployed.domain)
        if deploymentIdObj["name"] != "":
            # We found a deployment entry, we should use PATCH rather than POST
            httpMethod = "PATCH"
            url = "https://anypoint.mulesoft.com/hybrid/api/v2/organizations/%s/environments/%s/deployments/%s" % (self.OrgId, self.EnvId, deploymentIdObj["id"])
        else:
            url = "https://anypoint.mulesoft.com/hybrid/api/v2/organizations/%s/environments/%s/deployments" % (self.OrgId, self.EnvId)
        print("deploymentIdObj for domain %s - %s" % (deployed.domain, str(deploymentIdObj)))
        # get payload
        payload = mulesoftUtils.create_deploy_payload_rtf(deployed, deploymentIdObj, self.OrgId)
        headers = {
        'Authorization': 'Bearer %s' % self.token,
        'Content-Type': 'application/json'
        }
        # Deploy
        print("About to deploy, payload = %s" % json.dumps(payload))
        print("method - %s, url - %s" % (httpMethod, url) )
        response = requests.request( httpMethod, url, headers=headers, data=payload)
        if response.raise_for_status():
            print (response.text)
            raise Exception("Failed to deploy. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            try :
                responseJson = response.json()
            except :
                print("Could not decode JSON")
        print (response.status_code)
        print (response.text)


###### UNDEPLOY ##########
    def undeploy_package(self, domain):
        url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"
        #url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"
        headers = {
          'x-anypnt-env-id': str(self.EnvId),
          'Authorization': 'Bearer %s' % self.token,
          'Content-Type': 'application/json'
        }
        # data = {
        # "action": "DELETE",
        # "domains": [domain]
        # }
        data = {
        "action": "STOP",
        "domains": [domain]
        }
        data = json.dumps(data)
        response = requests.request("PUT", url, headers=headers, data = data)
        if response.raise_for_status():
                 raise Exception("Failed to undeploy. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            print ("Application successfully deleted")

        
    def undeploy_packageRTF(self, domain):
        headers = {
          'Authorization': 'Bearer %s' % self.token,
          'Content-Type': 'application/json'
        }
        deploymentIdObj = mulesoftUtils.get_deployment_id_obj(self.token, self.OrgId, self.EnvId, domain)
        if deploymentIdObj["id"] == "":
            raise Exception("Unable to retrieve deployment id for %s" % domain)

        url = "https://anypoint.mulesoft.com/hybrid/api/v2/organizations/%s/environments/%s/deployments/%s" % (self.OrgId, self.EnvId, deploymentIdObj["id"])
        response = requests.request("DELETE", url, headers=headers)
        if response.raise_for_status():
                 raise Exception("Failed to undeploy. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            print ("Application successfully deleted")

###### MODIFY ##########    
    def modify_package(self, file_path, domain, workers, Enabled, muleVersion, numWorkers, region, appProperties):
        #url = self._url + "/cloudhub/api/v2/applications/%s/files" % domain
        url = ("https://anypoint.mulesoft.com/cloudhub/api/v2/applications/%s" % domain)
        # url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications/%s/files" % domain
        headers = {
          'x-anypnt-env-id': str(self.EnvId),
          'Authorization': 'Bearer %s' % self.token
        }

        workers = json.loads(workers)
        prop = {}
        for (k,v) in appProperties.items() :
            prop[k] = v

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
        payload['appInfoJson']= json.dumps(payload['appInfoJson'])

        files = [
          ('file', open(file_path,'rb'))
        ]
        response = requests.request("PUT", url, headers=headers, data = payload, files = files)
        if response.raise_for_status():
                 raise Exception("Failed to modify package. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            print ("Application successfully updated")

###### CHECK STATUS #####
    def check_is_deployed(self, domain):
        # print("In check_is_deployed")
        url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"
        headers = {
          'x-anypnt-env-id': str(self.EnvId),
          'Authorization': 'Bearer %s' % self.token
        }
        response = requests.request("GET", url, headers=headers)
        # print("response status code = %s" % str(response.status_code))
        if response.raise_for_status():
                 raise Exception("Failed to check app status. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            response = response.json()
            for r in response:
                if r['domain'] == domain:
                    if r['status'] == "STARTED":
                        return True
                    else:
                        return False
            return False


    def check_is_deployedRTF(self, domain):
        url = "https://anypoint.mulesoft.com/hybrid/api/v2/organizations/%s/environments/%s/deployments" % (self.OrgId, self.EnvId)
        headers = {
          'Authorization': 'Bearer %s' % self.token
        }
        response = requests.request("GET", url, headers=headers)
        # print("response status code = %s" % str(response.status_code))
        if response.raise_for_status():
                 raise Exception("Failed to check app status. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            response = response.json()
            if response["items"]:
                for i in response['items']:
                    if i["name"] == domain:
                        if i["application"]["status"] == "RUNNING":
                            return True
                        else:
                            return False
            return False

###### UTILS ##########
    def get_token(self):
        if self.serviceType == "Runtime Fabric" or self.serviceType == "CloudHub - Use OAuth 2.0":
            print("In  OAuth block")
            # Hit the login endpoint to get a bearer token
            token = mulesoftUtils.get_token_conn_app(self.username, self.password)
            print('Got OAuth token')
        else:
            # Hit the login endpoint to get a bearer token
            print("In Cloudhub Auth block")
            token = mulesoftUtils.get_token_user(self.username, self.password)
            print('Got Cloudhub token')   
        return token


    
    
