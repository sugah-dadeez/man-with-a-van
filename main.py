import web_api
import config

app = web_api.create_app(config)

if __name__ == '__main__':
  app.run()
