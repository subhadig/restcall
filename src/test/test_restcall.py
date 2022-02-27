#!/usr/bin/env python3

from importlib import import_module
import unittest
import pathlib

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

    def test_restcall(self):
        print('testing')

    def test_generate_template(self):
        filepath = '/tmp/get-test-generate-template.json'
        if os.path.exists(filepath):
            os.remove(filepath)

        restcall.main(['-t', filepath])

        self.assertTrue(pathlib.Path(filepath).is_file())

        with open(filepath, 'r') as f:
            actual = ''.join(f.readlines())
        with open(os.path.dirname(__file__) + '/fixtures/generate-expected-result.json', 'r') as f:
            expected = ''.join(f.readlines())

        self.assertEqual(expected, actual)

if __name__=='__main__':
    unittest.main()
