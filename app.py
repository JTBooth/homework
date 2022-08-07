from flask import Flask, g

app = Flask(__name__)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

from blueprint_routes import page_bp

app.register_blueprint(page_bp)