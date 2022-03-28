# Copyright 2022 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



import time
import json
from shutil import copyfile

import requests

import os
os.environ['REQUESTS_CA_BUNDLE'] = 'ca.pem';

import org.slf4j.LoggerFactory as LoggerFactory

logger = LoggerFactory.getLogger("Mulesoft")

class mulesoftClient(object):
    def __init__(self, url, username, password, orgId, envId, cert, serviceType):
        self._url = url
        if url.endswith('/'):
            self._url = url[:-1]
        self.username = username
        self.password = password
        self.token = self.get_token()   # '20db92f1-36f7-4ae6-b4ce-5ecbca7f1798'
        self.OrgId = orgId
        self.EnvId = envId
        self.serviceType = serviceType

    @staticmethod
    def create_client_from_deployed(deployed):
        mmc = deployed.container
        return mulesoftClient(mmc.orgLevelDomain.masterDomain.url, mmc.orgLevelDomain.masterDomain.username, mmc.orgLevelDomain.masterDomain.password, mmc.orgLevelDomain.OrgId, mmc.envId,  mmc.orgLevelDomain.masterDomain.caCert, mmc.orgLevelDomain.masterDomain.serviceType)

    def get_token(self):
        content = {
        "username": self.username,
        "password": self.password
        }
        content = json.dumps(content)
        url = self._url + "/accounts/login"
        headers = {'content-type': 'application/json'}
        response = requests.request("POST", url , data = content, headers = headers)
        if response.raise_for_status():
            raise Exception("Failed to get token. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            response = response.json()
            return response['access_token']

    def deploy_package(self, file_path, domain, workers, Enabled, muleVersion, numWorkers, region, appProperties):

        workers = json.loads(workers)
        url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"

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
        headers = {
          'x-anypnt-env-id': str(self.EnvId),
          'x-anypnt-org-id': str(self.OrgId),
          'Authorization': 'Bearer %s' % self.token
        }


        response = requests.request("POST", url, headers=headers, data = payload, files = files)
        # response = requests.request("POST", url, headers=headers, files=payload)
        if response.status_code != 200: #  or response.raise_for_status()
            print response.status_code
            print response.text
            raise Exception("Failed to deploy. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            try :
                responseJson = response.json()
            except :
                print "(Could not decode JSON)"
        print response.status_code
        print response.text;

    def undeploy_package(self, domain):
        url = self._url + "/cloudhub/api/v2/applications"
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
            print "Application successfully deleted"

    def modify_package(self, file_path, domain, workers, Enabled, muleVersion, numWorkers, region, appProperties):
        #url = self._url + "/cloudhub/api/v2/applications/%s/files" % domain
        url = self._url + ("/cloudhub/api/v2/applications/%s" % domain)
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
            print "Application successfully updated"

    def check_app_status(self, domain):
        url = self._url + "/cloudhub/api/v2/applications"
        #url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"
        headers = {
          'x-anypnt-env-id': str(self.EnvId),
          'Authorization': 'Bearer %s' % self.token
        }
        response = requests.request("GET", url, headers=headers)
        if response.raise_for_status():
                 raise Exception("Failed to check app status. Server returned %s.\n%s" % (response.status_code, response.reason))
        else:
            # print "Application successfully deleted"
            response = response.json()
            for r in response:
                if r['domain'] in domain:
                    return True
            return False
