from flask import Flask
from .mongodb_util import init_mongo

def create_app():
    app = Flask(__name__)
    app.collection = init_mongo()

    from .routes import main
    app.register_blueprint(main)

    return app