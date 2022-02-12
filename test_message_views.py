"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, Message, User, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


# Disables DebugToolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        testuser = User.signup(username="testuser",
                               email="test@test.com",
                               password="testuser",
                               image_url=None)

        testuser2 = User.signup(username="testuser2",
                                email="test2@test.com",
                                password="testuser",
                                image_url=None)

        self.msg = Message(text="Test Text")
        db.session.commit()
        self.testuser_id = testuser.id
        self.testuser2_id = testuser2.id

    def tearDown(self):
        """reset the database"""

        User.query.delete()
        Message.query.delete()
        Like.query.delete()

    def test_add_message(self):
        """Can use add a message?"""

        # test authorization
        with self.client as c:
            resp = c.post("/messages/new",
                          data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        # test redirect and valid data
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

        # test bad data
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/messages/new")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("This field is required", html)

    def test_show_message(self):
        """this test for display message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            testuser = User.query.get(self.testuser_id)
            testuser.messages.append(self.msg)
            db.session.commit()

            resp = c.get(f"/messages/{self.msg.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Text", html)

    def test_delete_message(self):
        """test messages_delete()"""

        testuser = User.query.get(self.testuser_id)
        testuser.messages.append(self.msg)
        db.session.commit()

        # test authorization
        with self.client as c:
            resp = c.post(
                f"/messages/{self.msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

        # test delete with msg owner
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(
                f"/messages/{self.msg.id}/delete")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter_by(id=self.msg.id).one_or_none()
            self.assertIsNone(msg)
