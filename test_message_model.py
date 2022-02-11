"""Message model tests."""

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


class MessageModelTestCase(TestCase):
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

        self.message = Message(text="Test Text")
        self.message2 = Message(text="Test Two Text")

    def tearDown(self):
        """reset the database"""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

    def test_message_model(self):
        """Test basic message model"""
        db.session.add(self.user, self.message)
        self.user.messages.append(self.message)
        db.session.commit()

        self.assertEqual(self.message.user_id, self.user.id)
        self.assertEqual(self.message.text, "Test Text")

    def test_is_liked_by(self):
        """Test is_liked_by method of Message"""

        db.session.add(self.user)
        db.session.add(self.user2)
        db.session.add(self.message)
        self.user.messages.append(self.message)
        db.session.commit()

        self.assertEqual(self.message.is_liked_by(self.user2), False)

        self.message.liked_by.append(self.user2)
        db.session.commit()

        self.assertEqual(self.message.is_liked_by(self.user2), True)

