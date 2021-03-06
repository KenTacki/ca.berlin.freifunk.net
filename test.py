import os
import unittest
import tempfile
from ca import app, db
from ca.models import Request
from flask.ext.sqlalchemy import SQLAlchemy


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.temp_filepath = tempfile.mkstemp()
        database_path = 'sqlite:///{}'.format(self.temp_filepath)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_path
        app.config['TESTING'] = True
        self.app = app.test_client()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        os.close(self.db_fd)
        os.remove(self.temp_filepath)

    def test_empty_db(self):
        entries = db.session.query(Request).all()
        assert len(entries) == 0

    def test_get_index(self):
        response = self.app.get("/")
        assert response.status_code == 200

    def test_make_request(self):
        example_data = dict(id='foobar',
                            email='email@provider.com',
                            email_confirm='email@provider.com',
                            captcha='Berlin'
                            )
        response = self.app.post('/',
                                 data=example_data,
                                 follow_redirects=True)

        assert response.status_code == 200
        entries = db.session.query(Request).all()
        assert len(entries) == 1

    def test_duplicate_id(self):
        example_data = dict(id='foobar',
                            email='email@provider.com',
                            email_confirm='email@provider.com',
                            captcha='Berlin'
                            )
        response = self.app.post('/',
                                 data=example_data,
                                 follow_redirects=True)
        assert response.status_code == 200
        entries = db.session.query(Request).all()
        assert len(entries) == 1

        response = self.app.post('/',
                                 data=example_data,
                                 follow_redirects=True)

        assert 'Id already exists.' in str(response.data)

        # The new entry should not have been added so we should
        # still only have on entry
        entries = db.session.query(Request).all()
        assert len(entries) == 1

    def test_invalid_request_too_short(self):
        example_data = dict(id='a',
                            email='email@provider.com',
                            email_confirm='email@provider.com',
                            captcha='Berlin'
                            )
        response = self.app.post('/',
                                 data=example_data,
                                 follow_redirects=True)

        entries = db.session.query(Request).all()
        assert len(entries) == 0

    def test_invalid_request_underscore(self):
        example_data = dict(id='underscores_not_allowed',
                            email='email@provider.com',
                            email_confirm='email@provider.com',
                            captcha='Berlin'
                            )
        response = self.app.post('/',
                                 data=example_data,
                                 follow_redirects=True)

        entries = db.session.query(Request).all()
        assert len(entries) == 0


if __name__ == '__main__':
    unittest.main()
