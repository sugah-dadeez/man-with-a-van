import web_api
import test_basic
import argparse
import os

def cli():
    p = argparse.ArgumentParser()

    p.add_argument('-d', help='debug mode', dest='debug', action='store_true')
    p.add_argument('-c', help='set config environment', dest='config')
    p.add_argument('-p', help='port', dest='port', default=8080)
    p.add_argument('--raise', help='raise errors', dest='raise_errors', action='store_true')
    p.add_argument('--reset', help='reset db', dest='reset', action='store_true')
    p.add_argument('--test', help='run tests', dest='test', action='store_true')

    args = p.parse_args()

    if args.config:
        assert os.path.exists(args.config), 'bad config fp "{}"'.format(args.config)
        os.environ['FLASK_CONFIG'] = os.path.abspath(args.config)

    if args.reset:
        web_api.reset_db()
    elif args.test:
        app = web_api.create_app(debug=args.debug, raise_errors=args.raise_errors)
        test_basic.run()
    else:
        app = web_api.create_app(debug=args.debug, raise_errors=args.raise_errors)
        app.run(port=int(args.port))

if __name__ == '__main__':
    cli()
