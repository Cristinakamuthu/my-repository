from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt
from datetime import datetime


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-items_reported.user', '-claims.claimant', '-comments.user', '-images.uploader',
                       '-rewards_offered.offered_by_user', '-rewards_received.received_by_user')

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String, unique=True, nullable=True)
    _password_hash = db.Column(db.String, nullable=True)
    role = db.Column(db.String, default="user") # "admin" or "user"

    items_reported = db.relationship('Item', backref='reporter', lazy=True)
    claims = db.relationship('Claim', backref='claimant', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    images = db.relationship('Image', backref='uploader', lazy=True)
    rewards_offered = db.relationship('Reward', foreign_keys='Reward.offered_by_id', backref='offered_by_user')
    rewards_received = db.relationship('Reward', foreign_keys='Reward.received_by_id', backref='received_by_user')

    def __repr__(self):
        return f"<User #{self.id} - {self.username} ({self.role})>"

    @validates('email')
    def validate_email(self, key, email):
        if email:
            if '@' not in email or '.' not in email:
                raise ValueError("Please provide a suitable email address")
            return email

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes are write-only.")
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password.encode()).decode()
    
    def Authenticate(self, password):
        return self._password_hash and bcrypt.check_password_hash(self._password_hash, password.encode())


class Item(db.Model, SerializerMixin):
    __tablename__ = "items"

    serialize_rules = ('-comments.item', '-claims.item', '-reward.item', '-images.item', '-reporter.items_reported')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String, default='lost') # "lost","found","claimed"
    location = db.Column(db.String)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)

    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    inventory_admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    comments = db.relationship('Comment', backref='item', lazy=True)
    claims = db.relationship('Claim', backref='item', lazy=True)
    reward = db.relationship('Reward', uselist=False, backref='item')  # One reward per item
    images = db.relationship('Image', backref='item', lazy=True)


class Claim(db.Model, SerializerMixin):
    __tablename__ = "claims"

    serialize_rules = ('-item.claims', '-claimant.claims',)

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String, default="pending")  # "pending", "approved", "rejected"
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Comment(db.Model, SerializerMixin):
    __tablename__ = "comments"

    serialize_rules = ('-item.comments', '-user.comments',)

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reward(db.Model, SerializerMixin):
    __tablename__ = "rewards"

    serialize_rules = ('-item.reward', '-offered_by_user.rewards_offered', '-received_by_user.rewards_received')

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    offered_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    received_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, default="offered")  # "offered", "paid", "received"
    paid_at = db.Column(db.DateTime, nullable=True)


class Image(db.Model, SerializerMixin):
    __tablename__ = "images"

    serialize_rules = ('-item.images', '-uploader.images')

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    image_url = db.Column(db.String, nullable=False) 
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
