import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from flaskr import create_app
from model.models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the ___ test case"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format("postgres", "postgres", 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
        

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_given_behavior(self):
        """Test _____________ """
        res = self.client().get('/')

        self.assertEqual(res.status_code, 200)
    
    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue('current_categories', None)
        self.assertTrue(data['categories'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()