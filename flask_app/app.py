from flask import Flask, g
import sqlite3

def create_app(config_filename):
  app = Flask(__name__)
  app.config.from_pyfile(config_filename)

  @app.teardown_appcontext
  def close_connection(exception):
      db = getattr(g, '_database', None)
      if db is not None:
          db.close()

  try:
    from flask_app.blueprint_routes import page_bp
  except:
    from ..flask_app.blueprint_routes import page_bp

  app.register_blueprint(page_bp)

  return app