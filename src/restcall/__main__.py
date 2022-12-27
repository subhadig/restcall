from restcall import restcall
import sys
import argparse

def _main(argv: list):
    parser=argparse.ArgumentParser(description='Make restcalls!', usage=restcall.usage())
    parser.add_argument('filepath', help='Path to the restcall template')
    parser.add_argument('-t', '--template', action='store_true',
            help='Generate restcall template')
    parser.add_argument('-c', '--curlify', action='store_true',
            help='Generate curl command for the REST call')

    args = parser.parse_args(argv)
    filepath = args.filepath
    if args.template:
        restcall.generate_template(filepath)
    else:
        try:
            restcall.callrest(filepath, args.curlify)
        except KeyboardInterrupt:
            print("\nWARN: KeyboardInterrupt caught. Exiting restcall.")
        except ConnectionError as ce:
            print("\nWARN: Restcall failed due to ConnectionError:" + str(ce))
        except Exception as e:
            print("\nERROR: Restcall failed due to unknown errors. Here are the error details.")
            traceback.print_exc()

def main():
    _main(sys.argv[1:])

if __name__=='__main__':
    main()
