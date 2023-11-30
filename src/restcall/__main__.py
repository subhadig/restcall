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
from restcall import restcall
import sys
import argparse
import traceback
from requests.exceptions import ConnectionError

def _main(argv: list):
    parser=argparse.ArgumentParser(description='Make restcalls!',
                                   usage=restcall.usage())
    parser.add_argument('filepath', help='path to the restcall template')
    parser.add_argument('-v', '--version', action='version', version=restcall.print_version())
    parser.add_argument('-t', '--template', action='store_true',
            help='generate restcall template')
    parser.add_argument('-c', '--curlify', action='store_true',
            help='generate curl command for the REST call')
    parser.add_argument('-u', '--uncurlify', type=str, dest='curl_command_filepath',
                        help='generate restcall template from a curl command. Pass the file path containing the curl command.')

    args = parser.parse_args(argv)
    filepath = args.filepath
    if args.template:
        restcall.generate_template(filepath)
    elif args.curl_command_filepath:
        restcall.uncurlify(args.curl_command_filepath, filepath)
    else:
        try:
            restcall.callrest(filepath, args.curlify)
        except KeyboardInterrupt:
            print("\nWARN: KeyboardInterrupt caught. Exiting restcall.")
            sys.exit(1)
        except ConnectionError as ce:
            print("\nWARN: Restcall failed due to ConnectionError:" + str(ce))
            sys.exit(1)
        except Exception as e:
            print("\nERROR: Restcall failed due to unknown errors. Here are the error details.")
            traceback.print_exc()
            sys.exit(1)

def main():
    _main(sys.argv[1:])

if __name__=='__main__':
    main()
