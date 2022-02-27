#!/usr/bin/env python3

from importlib import import_module
import unittest
import pathlib
import json

import httpretty

import sys
import os
PROJECT_ROOT = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir
            )
        )
sys.path.append(PROJECT_ROOT)

import restcall

class TestRestcall(unittest.TestCase):

    def setUp(self):
        self.files_to_remove = []

    def test_generate_template(self):
        filepath = '/tmp/get-test-generate-template.json'
        self.files_to_remove.append(filepath)

        restcall.main(['-t', filepath])

        self.assertTrue(pathlib.Path(filepath).is_file())

        with open(filepath, 'r') as f:
            actual = ''.join(f.readlines())
        with open(os.path.dirname(__file__) + '/fixtures/generate-expected-result.json', 'r') as f:
            expected = ''.join(f.readlines())

        self.assertEqual(expected, actual)

    @httpretty.activate(allow_net_connect=False)
    def test_get(self):
        response_body = '{"description": "A small command line script to invoke REST APIs"}'
        httpretty.register_uri(httpretty.GET, "http://restcall.org/",
                           body=response_body,
                           content_type="application/json")

        restcall.main([os.path.dirname(__file__) + '/fixtures/get-simple-rest.json'])


        response_filepath = os.path.dirname(__file__) + '/fixtures/get-simple-rest-res.json'
        self.files_to_remove.append(response_filepath)
        self.assertTrue(pathlib.Path(response_filepath).is_file())
        with open(response_filepath) as f:
            actual_response = json.load(f)

        self.assertEquals(200, actual_response["resStatus"])
        self.assertEquals(response_body, json.dumps(actual_response["resBody"]))

    def tearDown(self):
        for f in self.files_to_remove:
            if os.path.exists(f):
                os.remove(f)

if __name__=='__main__':
    unittest.main()
