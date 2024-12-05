from app.models import db, User, environment, SCHEMA
from sqlalchemy.sql import text


def seed_users():
    """
    Seeds initial users into the database with first and last names.
    Prevents duplicates by checking if the email already exists.
    """
    users = [
        User(username='Demo', email='demo@aa.io', password='password', firstname='Demo', lastname='User'),
        User(username='marnie', email='marnie@aa.io', password='password', firstname='Marnie', lastname='Smith'),
        User(username='bobbie', email='bobbie@aa.io', password='password', firstname='Bobbie', lastname='Brown'),
        User(username='alice', email='alice@aa.io', password='password', firstname='Alice', lastname='Johnson'),
        User(username='charlie', email='charlie@aa.io', password='password', firstname='Charlie', lastname='Williams'),
    ]

    for user in users:
        # Check if a user with the same email already exists
        existing_user = User.query.filter_by(email=user.email).first()
        if existing_user:
            print(f"User with email {user.email} already exists. Skipping...")
        else:
            print(f"Adding user: {user.email}")
            db.session.add(user)

    db.session.commit()
    print("User seeding complete!")


def undo_users():
    """
    Removes all user data from the database and resets primary keys.
    """
    if environment == "production":
        db.session.execute(f"TRUNCATE TABLE {SCHEMA}.users RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM users"))
    db.session.commit()
