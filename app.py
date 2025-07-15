from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from flask_restful import Api
from flask_cors import CORS

from config import db
# from models import User, Item, Claim, Comment, Reward, Image
import os

app = Flask(__name__)
# CORS(app, 
#      origins=[
#          "http://localhost:3000", 
#          "https://safe-space-frontend.onrender.com"
#      ],
#      supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moringa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.secret_key = 'shhh-very-secret'

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
