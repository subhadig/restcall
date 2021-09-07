#!/usr/bin/env python3

import argparse
import json
from os import path
import requests


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


def generate_template(filepath):
    template = {
            'url':'',
            'httpMethod': get_httpmethod(filepath),
            'reqAuthType': 'none',
            'reqAuthToken': '',
            'reqContentType': '',
            'reqHeaders': {},
            'reqPayload': {},
            }
    write_template(filepath, template)


def get_payload(template):
    if template['reqContentType'] == 'application/json':
        payload = json.dumps(template['reqPayload'])
    else:
        payload = template['reqPayload']
    return payload


def get_reqheaders(template):
    req_headers=template['reqHeaders']

    if template['reqAuthType'] == 'bearer':
        req_headers['Authorization'] = 'Bearer ' + template['reqAuthToken']

    if template['reqContentType']:
        req_headers['Content-Type'] = template['reqContentType']

    return req_headers


def get_responsedata(res):
    res_data = {
            'resStatus': res.status_code,
            'resHeaders': dict(res.headers),
            'resBody': res.json(),
            }

    if res.headers['Content-Type'] == 'application/json':
        res_data['resBody'] = res.json()
    else:
        res_data['resBody'] = res.text

    return res_data


def do_call(template):
    res = requests.request(template['httpMethod'],
            template['url'],
            headers=get_reqheaders(template),
            data=get_payload(template))
    return get_responsedata(res)


def callrest(filepath):
    with open(filepath) as f:
        template = json.load(f)

    if template['httpMethod'] == 'GET':
        res_data = do_call(template)
    elif template['httpMethod'] == 'POST':
        res_data = do_call(template)
    else:
        raise NotImplementedError('HTTP method not supported')

    template |= res_data
    res_filepath = path.dirname(filepath) + path.sep + path.basename(filepath)[:-5] + '-res.json'
    write_template(res_filepath, template)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to the restcall template')
    parser.add_argument('-g', '--generate', action='store_true',
            help='Generate restcall template')

    args = parser.parse_args()
    filepath = args.filepath
    if args.generate:
        generate_template(filepath)
    else:
        callrest(filepath)

if __name__=='__main__':
    main()
