"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        self.testpwd = "HASHED_PASSWORD"

    def tearDown(self):
        """reset the database"""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

    def test_user_model(self):
        """Does basic model work?"""

        db.session.add(self.user)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.user.messages), 0)
        self.assertEqual(len(self.user.followers), 0)

    def test_user_following(self):
        """this test is this user following the other user"""

        db.session.add(self.user)
        db.session.add(self.user2)
        db.session.commit()

        self.assertEqual(self.user.is_following(self.user2), False)

        self.user.following.append(self.user2)
        db.session.commit()
        self.assertEqual(self.user.is_following(self.user2), True)

    def test_user_followed_by(self):
        """this test is this user followed by another user"""

        db.session.add(self.user)
        db.session.add(self.user2)
        db.session.commit()

        self.assertEqual(self.user.is_followed_by(self.user2), False)

        self.user.following.append(self.user2)
        db.session.commit()
        self.assertEqual(self.user2.is_followed_by(self.user), True)

    def test_signup(self):
        """this test the signup functionality"""

        user = User.signup(self.user.username,
                           self.user.email,
                           self.user.password,
                           self.user.image_url)
        self.assertIsInstance(user, User)

        db.session.commit()
        self.assertEqual(User.query.get(user.id), user)

        with self.assertRaises(Exception) as context:
            User.signup()
        self.assertIsInstance(context.exception, TypeError)

    def test_authenticate(self):
        """this test the user's credentials"""

        user = User.signup(self.user.username,
                           self.user.email,
                           self.user.password,
                           self.user.image_url)
        db.session.commit()
        User.authenticate(user.username, "HASHED_PASSWORD")
        self.assertEqual(User.authenticate(self.user.username, "HASHED_PASSWORD"), user)
        self.assertEqual(User.authenticate(self.user.username, "1HASHED_PASSWORD"), False)
        self.assertEqual(User.authenticate('BAD_USERNAME', "HASHED_PASSWORD"), False)

    