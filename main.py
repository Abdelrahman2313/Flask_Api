# app.py

from flask import Flask
from flask_jwt_extended import JWTManager
from configration import Config
from database import init_db
from authentication import auth
from items import items

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)
init_db(app)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(items, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)