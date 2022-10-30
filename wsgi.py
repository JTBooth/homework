from flask_app.app import create_app

app = create_app('test_settings.cfg')
if __name__ == "__main__":
  app.run()