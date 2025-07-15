from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from flask_restful import Api
# from flask_cors import CORS
from datetime import datetime
from functools import wraps

from config import db
from models import User, Item, Claim, Comment, Reward, Image

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moringa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.secret_key = 'shhh-very-secret'

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)



def admin_only(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if user.role != "admin":
            return jsonify({"error": "Admin access only"}), 403
        return fn(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return "I just wanted to let you know the routes work now 💃 Let's test them 💋 ..sincerely, Cristina."



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password needed"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400
    
    user = User(username=username, email=email)
    user.password_hash = password

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({"user": user.to_dict(), "token": token}), 201



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.authenticate(password):
        token = create_access_token(identity=user.id)
        return jsonify({"user": user.to_dict(), "token": token}), 200
    return jsonify({"error": "Invalid username or password"}), 401



@app.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify(user.to_dict()), 200



@app.route('/users', methods=['GET'])
@admin_only
def get_users():
    return jsonify([u.to_dict() for u in User.query.all()]), 200



@app.route('/items', methods=['GET'])
def get_items():
    return jsonify([item.to_dict() for item in Item.query.all()]), 200

@app.route('/items', methods=['POST'])
@jwt_required()
def report_item():
    data = request.get_json()
    user_id = get_jwt_identity()
    item = Item(
        name=data['name'],
        description=data.get('description'),
        status='lost',
        location=data.get('location'),
        reporter_id=user_id
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@app.route('/items/<int:id>', methods=['PATCH'])
@jwt_required()
def update_item(id):
    item = Item.query.get_or_404(id)
    data = request.get_json()
    for field in ['name', 'description', 'status', 'location']:
        if field in data:
            setattr(item, field, data[field])
    db.session.commit()
    return jsonify(item.to_dict()), 200

@app.route('/items/<int:id>', methods=['DELETE'])
@admin_only
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"}), 204



@app.route('/claims', methods=['POST'])
@admin_only
def claim_item():
    data = request.get_json()
    admin_id = get_jwt_identity()
    claim = Claim(item_id=data['item_id'], claimant_id=admin_id)
    db.session.add(claim)
    db.session.commit()
    return jsonify(claim.to_dict()), 201

@app.route('/claims/<int:id>/approve', methods=['PATCH'])
@admin_only
def approve_claim(id):
    claim = Claim.query.get_or_404(id)
    claim.status = "approved"
    claim.approved_by = get_jwt_identity()
    db.session.commit()
    return jsonify(claim.to_dict()), 200



@app.route('/comments', methods=['POST'])
@jwt_required()
def create_comment():
    data = request.get_json()
    comment = Comment(
        content=data['content'],
        user_id=get_jwt_identity(),
        item_id=data['item_id']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201

@app.route('/comments/<int:id>', methods=['PATCH'])
@jwt_required()
def edit_comment(id):
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    comment = Comment.query.get_or_404(id)

    if comment.user_id != user_id and user.role != "admin":
        return jsonify({"error": "Not authorized to edit this comment"}), 403

    if 'content' in data:
        comment.content = data['content']
        db.session.commit()

    return jsonify(comment.to_dict()), 200


@app.route('/comments', methods=['GET'])
def get_comments():
    return jsonify([c.to_dict() for c in Comment.query.all()]), 200

@app.route('/comments/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_comment(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    comment = Comment.query.get_or_404(id)

    if comment.user_id != user_id and user.role != "admin":
        return jsonify({"error": "Not authorized to delete this comment"}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted"}), 204



@app.route('/rewards', methods=['POST'])
@jwt_required()
def offer_reward():
    data = request.get_json()
    reward = Reward(
        item_id=data['item_id'],
        amount=data['amount'],
        offered_by_id=get_jwt_identity()
    )
    db.session.add(reward)
    db.session.commit()
    return jsonify(reward.to_dict()), 201

@app.route('/rewards/<int:id>/pay', methods=['PATCH'])
@jwt_required()
def pay_reward(id):
    reward = Reward.query.get_or_404(id)
    reward.status = "paid"
    reward.received_by_id = get_jwt_identity()
    reward.paid_at = datetime.utcnow()
    db.session.commit()
    return jsonify(reward.to_dict()), 200

@app.route('/rewards/history', methods=['GET'])
@jwt_required()
def reward_history():
    user_id = get_jwt_identity()
    offered = [r.to_dict() for r in Reward.query.filter_by(offered_by_id=user_id)]
    received = [r.to_dict() for r in Reward.query.filter_by(received_by_id=user_id)]
    return jsonify({"offered": offered, "received": received}), 200



@app.route('/images', methods=['POST'])
@jwt_required()
def upload_image():
    data = request.get_json()
    image = Image(
        item_id=data['item_id'],
        image_url=data['image_url'],
        uploaded_by=get_jwt_identity()
    )
    db.session.add(image)
    db.session.commit()
    return jsonify(image.to_dict()), 201

@app.route('/images/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_image(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    image = Image.query.get_or_404(id)

    if image.uploaded_by != user_id and user.role != "admin":
        return jsonify({"error": "Not authorized to delete this image"}), 403

    db.session.delete(image)
    db.session.commit()
    return jsonify({"message": "Image deleted"}), 204



if __name__ == '__main__':
    app.run(port=5555, debug=True)
