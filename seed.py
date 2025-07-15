from faker import Faker
from random import choice, randint, sample, uniform
from datetime import datetime, timedelta
from config import  db
from models import User, Item, Comment, Claim, Reward, Image
from app import app
 

fake = Faker()

with app.app_context():
    print(" Clearing db...")
    db.drop_all()
    db.create_all()

    print(" Seeding users...")
    users = []
    for i in range(20):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            role="admin" if i < 3 else "user"
        )
        user.password_hash = "password123"
        users.append(user)
        db.session.add(user)

    db.session.commit()

    print("Seeding items...")
    items = []
    for _ in range(20):
        reporter = choice(users)
        item = Item(
            name=fake.word().capitalize(),
            description=fake.sentence(),
            status=choice(["lost", "found"]),
            location=fake.city(),
            date_reported=fake.date_time_between(start_date="-60d", end_date="now"),
            reporter_id=reporter.id,
            inventory_admin_id=choice(users[:3]).id  # pick an admin
        )
        items.append(item)
        db.session.add(item)

    db.session.commit()

    print(" Seeding comments...")
    for _ in range(20):
        db.session.add(Comment(
            content=fake.sentence(),
            user_id=choice(users).id,
            item_id=choice(items).id,
            created_at=fake.date_time_between(start_date="-30d", end_date="now")
        ))

    print(" Seeding images...")
    for _ in range(20):
        db.session.add(Image(
            item_id=choice(items).id,
            image_url=fake.image_url(),
            uploaded_by=choice(users).id,
            created_at=fake.date_time_between(start_date="-45d", end_date="now")
        ))

    print(" Seeding claims...")
    for _ in range(20):
        item = choice(items)
        claimant = choice(users)
        claim = Claim(
            item_id=item.id,
            claimant_id=claimant.id,
            status=choice(["pending", "approved", "rejected"]),
            claimed_at=fake.date_time_between(start_date="-30d", end_date="now"),
            approved_by=choice(users[:3]).id 
        )
        db.session.add(claim)

    print(" Seeding rewards...")
    for _ in range(20):
        item = choice(items)
        offerer = choice(users)
        receiver = choice(users)
        reward = Reward(
            item_id=item.id,
            offered_by_id=offerer.id,
            received_by_id=receiver.id if randint(0, 1) else None,
            amount=round(uniform(10.0, 100.0), 2),
            status=choice(["offered", "claimed", "paid"]),
            paid_at=fake.date_time_between(start_date="-10d", end_date="now") if randint(0, 1) else None
        )
        db.session.add(reward)

    db.session.commit()

    print(" Done seeding!")
