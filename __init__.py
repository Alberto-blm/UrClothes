import os
import sys
from flask import Flask
from . import config

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        # app.config.from_pyfile('config.py', silent=True)
        app.config.from_object(config.DevelopmentConfig)
        
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register the BluePrints
    from . import user
    from . import clothes
    from . import carts
    app.register_blueprint(user.bp)
    app.register_blueprint(clothes.bp)
    app.register_blueprint(carts.bp)

    return app
