# MIT License
# 
# Copyright © 2022 Subhadip Ghosh
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import json
from os import path
import requests
import base64
import urllib3
from restcall.curlify import to_curl
from uncurl import api


def usage():
    return '''
    restcall.py [-h] [-t] [-c] filepath

    Generate a template:
        restcall -t get-service-name.json
        restcall -t post-service-name.json

    Import template from curl command
        restcall -u curl-command.txt get-service-name.json

    The `curl-command.txt` file contains the curl command.

    Edit the template and populate the required values:
        - url - the REST URL
        - httpMethod - GET, POST, PUT, PATCH, DELETE
        - reqAuthType - `none`, `bearer`, `bearer_generate`, `basic`
        - reqAuthToken
            - the actual token if the reqAuthType is `bearer`
            - filepath to the restcall template to generate the token if the reqAuthType is `bearer_generate`
            - `username:password` if the reqAuthType is `basic`
        - reqContentType - the request content type. eg. `application/json`
        - reqHeaders - the request headers
        - reqPayload - the request body. If binary, provide the file path.
        - resFile - the file path for storing binary response

    Make the REST call:
        restcall get-service-name.json
    
    The response will be stored in get-service-name-res.json.

    Output equivalent curl command:
        restcall -c get-service-name.json
    '''


def _get_httpmethod(filepath:str):
    filename = path.basename(filepath)
    if filename.startswith('get'):
        return 'GET'
    elif filename.startswith('post'):
        return 'POST'
    elif filename.startswith('put'):
        return 'PUT'
    elif filename.startswith('delete'):
        return 'DELETE'
    elif filename.startswith('patch'):
        return 'PATCH'


def _write_template(res_filepath:str, template:dict):
    with open(res_filepath, 'w') as f:
        json.dump(template, f, indent=4)


def _write_content(filepath:str, content:dict):
    with open(filepath, 'w+b') as f:
        f.write(content)


def generate_template(filepath:str,
        url = '',
        httpMethod = '',
        reqAuthType = 'none',
        reqAuthToken = '',
        reqContentType = '',
        reqHeaders = {},
        reqPayload = "",
        resFile = ""):
    template = {
            'url': url,
            'httpMethod': httpMethod if httpMethod else _get_httpmethod(filepath),
            'reqAuthType': reqAuthType,
            'reqAuthToken': reqAuthToken,
            'reqContentType': reqContentType,
            'reqHeaders': reqHeaders,
            'reqPayload': reqPayload,
            'resFile': resFile,
            }
    _write_template(filepath, template)


def uncurlify(inputfilepath:str, outputfilepath:str):
    with open(inputfilepath) as f:
        curl_command = ''.join(map(lambda l: l.removesuffix(" \\\n"),f.readlines()))
        curl_command = curl_command.replace('--location', '')
        curl_command = curl_command.replace('--request', '-X')
    
    parse_context = api.parse_context(curl_command)
    authType, authToken = _extract_authorization(parse_context.headers)
    generate_template(outputfilepath,
            parse_context.url,
            parse_context.method.upper(),
            authType,
            authToken,
            parse_context.headers.pop('Content-Type',''),
            parse_context.headers,
            json.loads(parse_context.data) if parse_context.data else "",
            "")


def _extract_authorization(headers: dict) -> tuple:
    authType = 'none'
    authToken = ''
    if 'Authorization' in headers:
        authorization = headers.pop('Authorization')
        if authorization.startswith('Basic '):
            authType = 'basic'
            authToken = str(base64.b64decode(authorization.removeprefix('Basic '), 'utf-8'))
        elif authorization.startswith('Bearer '):
            authType = 'bearer'
            authToken = authorization.removeprefix('Bearer ')

    return (authType, authToken)


def _get_payload(template:dict):
    if template['reqContentType'] == 'application/json':
        payload = json.dumps(template['reqPayload'])

    elif template['reqContentType'] == 'application/zip':
        payload = open(template['reqPayload'], 'rb')

    else:
        payload = template['reqPayload']
    return payload


def _get_reqheaders(template:dict) -> dict:
    req_headers=template['reqHeaders']

    if template['reqAuthType'] == 'bearer':
        req_headers['Authorization'] = 'Bearer ' + template['reqAuthToken']
    elif template['reqAuthType'] == 'bearer_generate':
        token_response = callrest(template['reqAuthToken'])
        req_headers['Authorization'] = 'Bearer ' + token_response['resBody']['access_token']
    elif template['reqAuthType'] == 'basic':
        req_headers['Authorization'] = 'Basic ' + str(base64.b64encode(bytes(template['reqAuthToken'], 'utf-8')), 'utf-8')

    if template['reqContentType']:
        req_headers['Content-Type'] = template['reqContentType']

    return req_headers


def _handle_binary_response(template:dict, filepath:str, file_ext:str, content):
    if template['resFile']:
        resfile = template['resFile']
    else:
        resfile = filepath[:-5] + file_ext
        template['resFile'] = resfile
    _write_content(resfile, content)
    return "Binary response has been written to " + resfile


def _get_responsedata(res, template, filepath) -> dict:
    res_data = {
            'resStatus': res.status_code,
            'resHeaders': dict(res.headers),
            'resSize': f'{len(res.content)/1024:.3f}K'
            }

    content_type = res.headers['Content-Type'] if 'Content-Type' in res.headers else ""

    if ';' in content_type:
        content_type = content_type[:content_type.index(';')]

    # application/x-www-form-urlencoded' is added to handle a server side bug
    if content_type == 'application/json' or content_type == 'application/x-www-form-urlencoded':
        # Don't try to convert to json if the response body is empty
        try:
            res_data['resBody'] = res.json()
        except Exception as e:
            print("\nWARN: error while converting response to JSON. Using as test.")
            res_data['resBody'] = res.text

    elif content_type == 'application/pdf':
        res_data['resBody'] = _handle_binary_response(template,
                filepath, '.pdf', res.content)

    elif content_type == 'application/zip':
        res_data['resBody'] = _handle_binary_response(template,
                filepath, '.zip', res.content)

    else:
        res_data['resBody'] = res.text

    return res_data


def _do_call(template:dict, filepath:str) -> requests.Response:
    # Disabling warnings for unverified HTTPS requests
    # https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    urllib3.disable_warnings()

    return requests.request(template['httpMethod'],
            template['url'],
            headers=_get_reqheaders(template),
            data=_get_payload(template),
            verify=False)


def callrest(filepath:str, curlify:bool=False) -> dict[str,object]:
    with open(filepath) as f:
        template = json.load(f)

    if template['httpMethod'] in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
        res = _do_call(template, filepath)
    else:
        raise NotImplementedError('HTTP method not supported')

    res_data = _get_responsedata(res, template, filepath)

    template = { **template, **res_data }
    res_filepath = filepath[:-5] + '-res.json'
    _write_template(res_filepath, template)
    print('Response status: {}, size: {}. Output stored in {}'.format(template['resStatus'],
        template['resSize'], res_filepath))

    if curlify:
        print(to_curl(res.request, verify=False))

    return template
