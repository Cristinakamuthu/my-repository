from app import app
from config import db
from models import User, Item, Claim, Comment, Reward, Image
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def seed():
    with app.app_context():
        # db.create_all()
        print(" Clearing old data...")
        db.session.query(Image).delete()
        db.session.query(Reward).delete()
        db.session.query(Comment).delete()
        db.session.query(Claim).delete()
        db.session.query(Item).delete()
        db.session.query(User).delete()
        db.session.commit()

        print(" Creating users...")
        users = []
        for _ in range(10):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                role=random.choice(["user", "admin"]),
            )
            user.password_hash = "password123"
            users.append(user)
            db.session.add(user)

        db.session.commit()

        print(" Creating items...")
        items = []
        for _ in range(15):
            item = Item(
                name=fake.word().capitalize() + " " + fake.word().capitalize(),
                description=fake.sentence(),
                status=random.choice(["lost", "found"]),
                location=fake.city(),
                date_reported=fake.date_time_between(start_date='-30d', end_date='now'),
                reporter_id=random.choice(users).id,
                inventory_admin_id=random.choice(users).id
            )
            items.append(item)
            db.session.add(item)

        db.session.commit()

        print("Creating comments...")
        for _ in range(20):
            comment = Comment(
                content=fake.sentence(),
                user_id=random.choice(users).id,
                item_id=random.choice(items).id,
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            db.session.add(comment)

        db.session.commit()

        print(" Creating claims...")
        for _ in range(10):
            claim = Claim(
                item_id=random.choice(items).id,
                claimant_id=random.choice(users).id,
                status=random.choice(["pending", "approved", "rejected"]),
                claimed_at=fake.date_time_between(start_date='-20d', end_date='now'),
                approved_by=random.choice(users).id
            )
            db.session.add(claim)

        db.session.commit()

        print(" Creating rewards...")
        for _ in range(8):
            item = random.choice(items)
            reward = Reward(
                item_id=item.id,
                offered_by_id=random.choice(users).id,
                received_by_id=random.choice(users).id,
                amount=round(random.uniform(10, 100), 2),
                status=random.choice(["offered", "paid"]),
                paid_at=fake.date_time_between(start_date='-15d', end_date='now')
                if random.random() > 0.5 else None
            )
            db.session.add(reward)

        db.session.commit()

        print("Creating images...")
        for _ in range(15):
            image = Image(
                item_id=random.choice(items).id,
                image_url=fake.image_url(),
                uploaded_by=random.choice(users).id,
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            db.session.add(image)

        db.session.commit()

        print(" Done seeding the database!")

if __name__ == "__main__":
    seed()
