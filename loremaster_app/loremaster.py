import os

from flask import Flask
from pathlib import Path



UPLOAD_FOLDER = (Path(__file__) / "../instance/images").resolve()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER = UPLOAD_FOLDER
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # import and register blueprints
    from .blueprints import navigation, auth, api

    app.register_blueprint(navigation.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)

    app.add_url_rule('/', endpoint='index')

    return app