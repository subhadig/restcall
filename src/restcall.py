#!/usr/bin/env python3

import argparse
import json
from os import path
import requests
import traceback
from requests.exceptions import ConnectionError
import base64
import urllib3
from curlify import to_curl


def get_httpmethod(filepath):
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


def write_template(filepath, template):
    with open(filepath, 'w') as f:
        json.dump(template, f, indent=4)


def write_content(filepath, content):
    with open(filepath, 'w+b') as f:
        f.write(content)


def generate_template(filepath):
    template = {
            'url':'',
            'httpMethod': get_httpmethod(filepath),
            'reqAuthType': 'none',
            'reqAuthToken': '',
            'reqContentType': '',
            'reqHeaders': {},
            'reqPayload': "",
            'resFile': "",
            }
    write_template(filepath, template)


def get_payload(template):
    if template['reqContentType'] == 'application/json':
        payload = json.dumps(template['reqPayload'])

    elif template['reqContentType'] == 'application/zip':
        payload = open(template['reqPayload'], 'rb')

    else:
        payload = template['reqPayload']
    return payload


def get_reqheaders(template):
    req_headers=template['reqHeaders']

    if template['reqAuthType'] == 'bearer':
        req_headers['Authorization'] = 'Bearer ' + template['reqAuthToken']
    elif template['reqAuthType'] == 'basic':
        req_headers['Authorization'] = 'Basic ' + str(base64.b64encode(bytes(template['reqAuthToken'], 'utf-8')), 'utf-8')

    if template['reqContentType']:
        req_headers['Content-Type'] = template['reqContentType']

    return req_headers


def handle_binary_response(template, filepath, file_ext, content):
    if template['resFile']:
        resfile = template['resFile']
    else:
        resfile = filepath[:-5] + file_ext
        template['resFile'] = resfile
    write_content(resfile, content)
    return "Binary response has been written to " + resfile


def get_responsedata(res, template, filepath):
    res_data = {
            'resStatus': res.status_code,
            'resHeaders': dict(res.headers),
            }

    content_type = res.headers['Content-Type'] if 'Content-Type' in res.headers else ""

    if ';' in content_type:
        content_type = content_type[:content_type.index(';')]

    if content_type == 'application/json':
        res_data['resBody'] = res.json()

    elif content_type == 'application/pdf':
        res_data['resBody'] = handle_binary_response(template,
                filepath, '.pdf', res.content)

    elif content_type == 'application/zip':
        res_data['resBody'] = handle_binary_response(template,
                filepath, '.zip', res.content)

    else:
        res_data['resBody'] = res.text

    return res_data


def do_call(template, filepath):
    # Disabling warnings for unverified HTTPS requests
    # https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    urllib3.disable_warnings()

    return requests.request(template['httpMethod'],
            template['url'],
            headers=get_reqheaders(template),
            data=get_payload(template),
            verify=False)


def callrest(filepath, curlify):
    with open(filepath) as f:
        template = json.load(f)

    if template['httpMethod'] == 'GET':
        res = do_call(template, filepath)
    elif template['httpMethod'] == 'POST':
        res = do_call(template, filepath)
    elif template['httpMethod'] == 'PUT':
        res = do_call(template, filepath)
    else:
        raise NotImplementedError('HTTP method not supported')

    res_data = get_responsedata(res, template, filepath)

    template = { **template, **res_data }

    res_filepath = filepath[:-5] + '-res.json'

    write_template(res_filepath, template)

    print('Response status: {}. Output stored in {}'.format(template['resStatus'],
        res_filepath))

    if curlify:
        print(to_curl(res.request, verify=False))


def usage():
    return '''
    restcall.py [-h] [-t] [-c] filepath

    Generate a template:
        restcall -t get-service-name.json
        restcall -t post-service-name.json

    Edit the template and populate the required values:
        - url - the REST URL
        - httpMethod - GET, POST, PUT, PATCH, DELETE
        - reqAuthType - none, bearer
        - reqAuthToken - the actual token if the reqAuthType is `bearer`
        - reqContentType - the request content type. eg. `application/json`
        - reqHeaders - the request headers
        - reqPayload - the request body. If binary, provide the file path.
        - resFile - the file path for storing binary response

    Make the REST call:
        restcall get-service-name.json

    Output equivalent curl command:
        restcall -c get-service-name.json

    The response will be stored in get-service-name-res.json.
    '''


def main():
    parser=argparse.ArgumentParser(description='Make restcalls!', usage=usage())
    parser.add_argument('filepath', help='Path to the restcall template')
    parser.add_argument('-t', '--template', action='store_true',
            help='Generate restcall template')
    parser.add_argument('-c', '--curlify', action='store_true',
            help='Generate curl command for the REST call')

    args = parser.parse_args()
    filepath = args.filepath
    if args.template:
        generate_template(filepath)
    else:
        try:
            callrest(filepath, args.curlify)
        except KeyboardInterrupt:
            print("\nWARN: KeyboardInterrupt caught. Exiting restcall.")
        except ConnectionError as ce:
            print("\nWARN: Restcall failed due to ConnectionError:" + str(ce))
        except Exception as e:
            print("\nERROR: Restcall failed due to unknown errors. Here are the error details.")
            traceback.print_exc()

if __name__=='__main__':
    main()
