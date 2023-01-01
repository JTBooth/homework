from flask_app.app import create_app

app = create_app('default_settings.cfg')
if __name__ == "__main__":
  app.run()