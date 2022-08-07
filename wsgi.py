from flask_app.app import create_app

if __name__ == "__main__":
  app = create_app('test_settings.cfg')
  app.run()