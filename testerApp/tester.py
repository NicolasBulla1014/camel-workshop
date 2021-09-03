#!/usr/bin/python
import sys
import requests
import subprocess
import time
from random import seed
from random import randint
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import openshift as oc

app = FastAPI(title="Camel Workshop tester App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    baseUrl: str
    openshiftUrl: str
    accountToken: str
    deployment: str
    appType: str
    openshiftProject: str

    class Config:
        schema_extra = {
            "example": {
                "baseUrl": "https://camel-workshop-cmap-camel.apps.shared-na46.openshift.opentlc.com",
                "openshiftUrl": "https://api.shared-na46.openshift.opentlc.com:6443/",
                "accountToken": "eyJhbGciOiJSUzI1NiIsImtpZCI6IllJVzRHTGUxUVhENDZLRWxYUlBrWkpXTGdBQ3F6Tm9xMHpWSjMxMVVENTQifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJjbWFwLWNhbWVsIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InJvYm90LXRva2VuLWwydnJwIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6InJvYm90Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiYzY2ZTZiOTEtMGJiNy00MTUwLTlmMDYtZmEyNTFlYjU0NDc0Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmNtYXAtY2FtZWw6cm9ib3QifQ.K_L_9p3yU9OT8IrwGJ4fOHvxW9bOowTGtY5Y3yWw_lV27-kCIoPEKi5EqbMWPvt_E8bqNZDJJWI4HZmmqmgKlcEZOSdDpojFI67ZK06XBd0Tp0KM9JL99GvCMiixHdFNSJNPF30EQQBcSu0u_6TkjeJd256i5ZxrESBs-L1jc7uX-3BxZZ6swjEQcqgDFHeJ7xqQ79yqSqMKFmjWXC96v3eUA-YwjEkKW-unQ_E3lWSjpOAuxgRx-aX6RG5x5ztQr0AiqgBo11IK1HGmP7PbF-9lwjFbOgCt8WN73H-CAfLULvrUXMQnfXtZ68jFzhUmmekXKf9_n2O8xexSIz_60A",
                "deployment": "camel-workshop",
                "appType": "deployment",
                "openshiftProject": "camel-asdf",
            }
        }

@app.get("/", include_in_schema=False)
async def redirect():
    response = RedirectResponse(url='/docs')
    return response

@app.post("/testApp")
def test_app(request: Request):
    response = {}
    response['test_create_drug'] = test_1_create(request)
    response['test_update_drug'] = test_2_update(request)
    response['test_disable_drug'] = test_3_disable(request)
    response['test_upload_file'] = test_4_uploadfile(request)
    response['test_persistent_data'] = test_5_persistent_database(request)
    response['test_download_file'] = test_6_downloadFile(request)
    return response

def test_1_create(request: Request):
    url = request.baseUrl
    pload = '{"productNdc":"69618-010","price":561121,"existences":20,"status":"ACTIVE"}'
    r = requests.post(url + "/store/drug/create", data=pload)
    print("create response: ", r.text)
    if r.status_code != 200:
        return 'the service create should respond with 200 success code, response: ' + str(r.status_code)
    response = r.json()
    if 'productNdc' not in response:
        return 'there should be the identifier'
    if 'genericName' not in response:
        return 'there should be the generic name field'
    if 'packageDescription' not in response:
        return 'there should be the package description'
    if 'labelerName' not in response:
        return 'there should be the labelerName'
    return 'ok'

# set parameters from dto and update the entity
def test_2_update(request: Request):
        url = request.baseUrl
        pload = '{"productNdc":"69618-010","price":512,"existences":10,"status":"ACTIVE"}'
        r = requests.put(url + "/store/drug/update", data=pload)
        print("update response: ", r.text)
        if r.status_code != 200:
            return 'the service update should respond with 200 success code, response: ' + str(r.status_code)
        r = requests.get(url + "/store/drug/69618-010")
        print("response get updated ", r.text)
        if r.status_code != 200: 
            return 'the service get drug should respond with 200 success code, response: ' + str(r.status_code)
        response = r.json()
        if response == []:
            return 'the response must contain one element'
        if response[0]['price'] != 512:
            return 'the price must be updated'
        if response[0]['existences'] != 10:
            return 'the existence must be updated'
        return 'ok'

# Update the drug with INACTIVE status
def test_3_disable(request: Request):
        url = request.baseUrl
        r = requests.delete(url + "/store/drug/69618-010")
        print("disable response, ", r.text)
        if r.status_code != 200:
            return 'the service disable should respond with 200 success code, response: ' + str(r.status_code)
        r = requests.get(url + "/store/drug/69618-010")
        print("get disabled response: ", r.text)
        if r.status_code != 200: 
            return 'the service get drug should respond with 200 success code, response: ' + str(r.status_code)
        response = r.json()
        if response[0]['status'] != 'INACTIVE':
            return 'the status should be updated to INACTIVE'
        return 'ok'

def test_4_uploadfile(request: Request):
    url = request.baseUrl
    seed(1)
    filename = randint(100000, 900000)
    print("file to be uploaded", str(filename) + ".pdf")
    with open('example.pdf', 'rb') as f:
        data = f.read()
        files = {'upload_file': (str(filename) + ".pdf", data)}
        r = requests.post(url + "/store/drug/uploadPdf", files=files)
        print("uploaded response", r.text)
        if r.status_code != 200:
         return 'the service upload file should respond with 200 success code, response: ' + str(r.status_code)
    return 'ok'

def rc_is_ready(rc):
    return rc.model.spec.replicas == rc.model.status.readyReplicas

def dc_is_ready(dc):
    return 1 == dc.model.status.readyReplicas

# Use a Database for persistent storage
def test_5_persistent_database(request: Request):
    appType = request.appType
    accountToken = request.accountToken
    deployment = request.deployment
    openshiftUrl = request.openshiftUrl
    project = request.openshiftProject

    try:
        with oc.api_server(openshiftUrl):
            with oc.token(accountToken):
                with oc.tls_verify(enable=False):
                    with oc.project(project), oc.timeout(5*60):
                        print("Using openshift server", openshiftUrl, "project", project)
                        dc = oc.selector(appType + "/" + deployment).object()
                        envs = dc.model.spec.template.spec.containers[0].env
                        envNames = []
                        for env in envs:
                            envNames.append(env['name'])
                        print("enviroment variables:",envNames)
                        if 'DATABASE_DRIVER' not in envNames:
                            return 'there should be the DATABASE_DRIVER env in application'
                        if 'DATABASE_URL' not in envNames:
                            return 'there should be the DATABASE_URL env in application'
                        if 'DATABASE_USERNAME' not in envNames:
                            return 'there should be the DATABASE_USERNAME env in application'
                        if 'DATABASE_PASSWORD' not in envNames:
                            return 'there should be the DATABASE_PASSWORD env in application'
                        print("checking pvc")
                        pvc = dc.model.spec.template.spec.volumes[0]
                        print("pvc", pvc)
                        if 'persistentVolumeClaim' not in pvc:
                            return 'there should be a persistent volume claim of type persistentVolumeClaim in application'
                    
    except oc.model.OpenShiftPythonException as e:
        return 'there was an connection error to Openshift ' +  str(e)
    return 'ok'

# Use a Database for persistent storage
# def test_5_persistent_database(request: Request):
#     appType = request.appType
#     accountToken = request.accountToken
#     deployment = request.deployment
#     openshiftUrl = request.openshiftUrl
#     # seconds
#     timeout=90

#     try:
#         with oc.api_server(openshiftUrl):
#             with oc.token(accountToken):
#                 with oc.tls_verify(enable=False):
#                     print("Using openshift server", openshiftUrl)
#                     dc = oc.selector(appType + "/" + deployment).object()
#                     print("Scaling to zero", dc.name())
#                     oc.invoke('scale', ['--replicas=0', 'dc/' + dc.name()])
#                     print("Scaling to one", dc.name())
#                     oc.invoke('scale', ['--replicas=1', 'dc/' + dc.name()])
#                     dc.refresh() #get updated dc with latest version
#                     print("Waiting for up to", timeout, "seconds for application", dc.name(), "to be ready")
#                     with oc.timeout(timeout):
#                         dc = oc.selector(appType + "/" + deployment)
#                         dc.until_all(1, success_func=dc_is_ready)
#                     print("finished rollout for", deployment)
#     except oc.model.OpenShiftPythonException as e:
#         return 'there was an connection error to Openshift ' +  str(e)

#     url = request.baseUrl
#     r = requests.get(url + "/store/drug/69618-010")
#     print("database get response: ", r.text)
#     if r.status_code != 200:
#         return 'the service get drug should respond with 200 success code, response: ' + str(r.status_code)
#     response = r.json()
#     if response == "":
#         return "the response must not be empty"
#     if response[0]['productNdc'] != '69618-010': 
#         return 'the identifier should be the same from request'
#     if 'genericName' not in response[0]:
#         return 'there should be the generic name field'
#     if 'packageDescription' not in response[0]:
#         return 'there should be the package description'
#     if 'labelerName' not in response[0]:
#         return 'there should be the labelerName'
#     return 'ok'


def test_6_downloadFile(request: Request):
    url = request.baseUrl
    seed(1)
    filename = randint(100000, 900000)
    print("file to be downloaded", str(filename) + ".pdf")
    r = requests.get(url + "/store/drug/getPdf/"+ str(filename) + ".pdf")
    if r.status_code != 200:
        return 'the service download pdf should respond with 200 success code, response: ' + str(r.status_code)
    if r == "":
        return "the response must not be empty"
    return 'ok'
