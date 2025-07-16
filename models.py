from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String, unique=True, nullable=True)
    _password_hash = db.Column(db.String, nullable=True)
    role = db.Column(db.String, default="user")

    items_reported = relationship('Item', backref='reporter',
        foreign_keys='Item.reporter_id', cascade='all, delete-orphan')
    comments = relationship('Comment', backref='user', cascade='all, delete-orphan')
    images = relationship('Image', backref='uploader', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User #{self.id} - {self.username} ({self.role})>"

    @validates('email')
    def validate_email(self, key, email):
        if email and ('@' not in email or '.' not in email):
            raise ValueError("Please provide a suitable email address")
        return email

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes are write-only.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password.encode()).decode()

    def authenticate(self, password):
        return self._password_hash and bcrypt.check_password_hash(self._password_hash, password.encode())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role
        }


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String, default='lost')
    location = db.Column(db.String)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)

    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    inventory_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    comments = relationship('Comment', backref='item', cascade='all, delete-orphan')
    claims = relationship('Claim', backref='item', cascade='all, delete-orphan')
    reward = relationship('Reward', uselist=False, backref='item', cascade='all, delete-orphan')
    images = relationship('Image', backref='item', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "location": self.location,
            "date_reported": self.date_reported.isoformat() if self.date_reported else None,
            "reporter": self.reporter.to_dict() if self.reporter else None,
            "inventory_admin_id": self.inventory_admin_id,
            "comments": [c.to_dict() for c in self.comments],
            "claims": [c.to_dict() for c in self.claims],
            "reward": self.reward.to_dict() if self.reward else None,
            "images": [img.to_dict() for img in self.images]
        }


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String, default="pending")
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    claimant = relationship('User', foreign_keys=[claimant_id], backref='claims')
    approver = relationship('User', foreign_keys=[approved_by], backref='claims_approved')

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "claimant": self.claimant.to_dict() if self.claimant else None,
            "status": self.status,
            "claimed_at": self.claimed_at.isoformat() if self.claimed_at else None,
            "approved_by": self.approver.to_dict() if getattr(self, 'approver', None) else None
        }


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "user": self.user.to_dict() if self.user else None,
            "item_id": self.item_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Reward(db.Model):
    __tablename__ = "rewards"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    offered_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    received_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, default="offered")
    paid_at = db.Column(db.DateTime, nullable=True)

    offered_by_user = relationship('User', foreign_keys=[offered_by_id], backref='rewards_offered')
    received_by_user = relationship('User', foreign_keys=[received_by_id], backref='rewards_received')

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "offered_by": self.offered_by_user.to_dict() if self.offered_by_user else None,
            "received_by": self.received_by_user.to_dict() if self.received_by_user else None,
            "amount": self.amount,
            "status": self.status,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None
        }


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    image_url = db.Column(db.String, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "image_url": self.image_url,
            "uploaded_by": self.uploaded_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
