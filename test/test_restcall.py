#!/usr/bin/env python3

import unittest
import pathlib
import json
import io

import httpretty
from typing import Tuple
from httpretty.core import HTTPrettyRequest

import sys
import os
SRC_ROOT = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'src'
            )
        )
sys.path.append(SRC_ROOT)

from restcall.__main__ import _main as main

class TestRestcall(unittest.TestCase):

    def setUp(self):
        self.files_to_remove = []
        self.maxDiff = None

    def test_generate_template(self):
        filepath = '/tmp/get-test-generate-template.json'
        self.files_to_remove.append(filepath)

        main(['-t', filepath])

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

        main([os.path.dirname(__file__) + '/fixtures/get-simple-rest.json'])


        response_filepath = os.path.dirname(__file__) + '/fixtures/get-simple-rest-res.json'
        self.files_to_remove.append(response_filepath)
        self.assertTrue(pathlib.Path(response_filepath).is_file())
        with open(response_filepath) as f:
            actual_response = json.load(f)

        self.assertEqual(200, actual_response["resStatus"])
        self.assertEqual(response_body, json.dumps(actual_response["resBody"]))

    @httpretty.activate(allow_net_connect=False)
    def test_get_external_file(self):
        response_body = '{"description": "A small command line script to invoke REST APIs"}'
        httpretty.register_uri(httpretty.GET, "http://restcall.org/",
                           body=response_body,
                           content_type="application/json")

        main([os.path.dirname(__file__) + '/fixtures/get-simple-rest-external-file.json'])


        response_filepath = os.path.dirname(__file__) + '/fixtures/get-simple-rest-external-file-res.json'
        self.files_to_remove.append(response_filepath)
        self.assertTrue(pathlib.Path(response_filepath).is_file())
        with open(response_filepath) as f:
            actual_response = json.load(f)

        self.assertEqual(200, actual_response["resStatus"])
        self.assertEqual("Response has been saved to test/fixtures/external-response-file.json",
                actual_response["resBody"])

        external_response_filepath = os.path.dirname(__file__) + '/fixtures/external-response-file.json'
        self.files_to_remove.append(external_response_filepath)
        self.assertTrue(pathlib.Path(external_response_filepath).is_file())
        with open(external_response_filepath) as f:
            external_response = f.read()
        self.assertEqual('{"description": "A small command line script to invoke REST APIs"}',
                external_response)

    @httpretty.activate(allow_net_connect=False)
    def test_multipart_file_upload(self):
        def httpretty_callback(request: HTTPrettyRequest,
                url: str,
                headers: dict
                ) -> Tuple[int, dict, str]:
            self.assertTrue(request.headers['Content-Type'].startswith('multipart/form-data; boundary='))
            self.assertIsNotNone(request.body)
            return (200, {}, '')

        httpretty.register_uri(httpretty.POST, "http://restcall.org/multipart",
                           body=httpretty_callback,
                           content_type="multipart/form-data")

        main([os.path.dirname(__file__) + '/fixtures/post-multipart-file.json'])


        response_filepath = os.path.dirname(__file__) + '/fixtures/post-multipart-file-res.json'
        self.files_to_remove.append(response_filepath)
        self.assertTrue(pathlib.Path(response_filepath).is_file())
        with open(response_filepath) as f:
            actual_response = json.load(f)

        self.assertEqual(200, actual_response["resStatus"])
        self.assertEqual('', actual_response["resBody"])

    @httpretty.activate(allow_net_connect=False)
    def test_curlify(self):
        response_body = '{"description": "A small command line script to invoke REST APIs"}'

        httpretty.register_uri(httpretty.POST, "http://restcall.org/",
                           body=response_body,
                           adding_headers={},
                           content_type="application/json")

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

        main(['-c', os.path.dirname(__file__) + '/fixtures/post-simple-rest.json'])

        sys.stdout = sys.__stdout__

        response_filepath = os.path.dirname(__file__) + '/fixtures/post-simple-rest-res.json'
        self.files_to_remove.append(response_filepath)

        expected_output_filepath = os.path.dirname(__file__) + '/fixtures/curlify-response.txt'
        with open(expected_output_filepath) as f:
            actual = "\n".join(capturedOutput.getvalue().split("\n")[1:])
            self.assertEqual(f.read(), actual)

    def test_uncurlify(self):
        filepath = '/tmp/post-test-uncurlify.json'
        self.files_to_remove.append(filepath)

        main(['-u',
            os.path.dirname(__file__) + '/fixtures/curl-post.txt',
            filepath])

        self.assertTrue(pathlib.Path(filepath).is_file())

        with open(filepath, 'r') as f:
            actual = ''.join(f.readlines())
        with open(os.path.dirname(__file__) + '/fixtures/post-curl-expected.json', 'r') as f:
            expected = ''.join(f.readlines())

        self.assertEqual(expected, actual)

    @httpretty.activate(allow_net_connect=False)
    def test_curlify_uncurlify(self):
        response_body = '{"description": "A small command line script to invoke REST APIs"}'

        httpretty.register_uri(httpretty.POST, "http://restcall.org/",
                           body=response_body,
                           adding_headers={},
                           content_type="application/json")

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

        original_template_path = os.path.dirname(__file__) + '/fixtures/post-simple-rest.json'
        main(['-c', original_template_path])

        sys.stdout = sys.__stdout__

        response_filepath = os.path.dirname(__file__) + '/fixtures/post-simple-rest-res.json'
        self.files_to_remove.append(response_filepath)

        generated_template_path = '/tmp/post-test-curlify-uncurlify.json'
        self.files_to_remove.append(generated_template_path)

        curl_command_filepath = '/tmp/test-curlify-uncurlify-command.txt'
        with open(curl_command_filepath, 'w') as f:
            printed_command = "\n".join(capturedOutput.getvalue().split("\n")[1:])
            f.write(printed_command)

        main(['-u',
            curl_command_filepath,
            generated_template_path])

        self.assertTrue(pathlib.Path(generated_template_path).is_file())

        with open(generated_template_path, 'r') as f:
            actual = ''.join(f.readlines())
        with open(original_template_path, 'r') as f:
            expected = ''.join(f.readlines())

        self.assertEqual(expected, actual)

    def tearDown(self):
        for f in self.files_to_remove:
            if os.path.exists(f):
                os.remove(f)

if __name__=='__main__':
    unittest.main()
