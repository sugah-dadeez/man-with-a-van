import web_api
import argparse
import os

def cli():
    p = argparse.ArgumentParser()

    p.add_argument('-d', help='debug mode', dest='debug', action='store_true')
    p.add_argument('--raise', help='raise errors', dest='raise_errors', action='store_true')
    p.add_argument('--reset', help='reset db', dest='reset', action='store_true')
    p.add_argument('--config', help='set config environment', dest='config')

    args = p.parse_args()

    if args.config:
        assert os.path.exists(args.config), 'bad config fp "{}"'.format(args.config)
        os.environ['FLASK_CONFIG'] = os.path.abspath(args.config)

    if args.reset:
        web_api.reset_db()
    else:
        app = web_api.create_app(debug=args.debug, raise_errors=args.raise_errors)
        app.run()

if __name__ == '__main__':
    cli()
