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

            self.new_question = {
                'question': 'Test Question',
                'answer': 'Test Answer',
                'category': 'history',
                'difficulty': 1,
                'difficulty2': 1
            }
            self.new_question2 = {
                "question": "dsd",
                "answer": "sdsd",
                "difficulty": "3",
                "category": "3"
            }
            self.search_term = {'searchTerm': 'fantasy'}
            self.pagination = {'totalQuestions': 0}
        
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_given_behavior(self):
        """Test _____________ """
        res = self.client().get('/')

        self.assertEqual(res.status_code, 200)
    
    def test__get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue('current_categories', None)
        self.assertTrue(data['categories'])

    
    def test__delete_question(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
    
    def test__get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
    def test__wrong_categories(self):
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found')

    def test__404_question_not_exist(self):
        res = self.client().delete('/question/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
    
    def test__404_exceed_max_page(self):
        res = self.client().get('/questions?page=1000',
                                json=self.pagination)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test__create_new_question(self):
        res = self.client().post('/questions', json=self.new_question2)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test__422_if_question_creation_unprocessable(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test__get_question_search_term_OK_200(self):
        res = self.client().post('/questions/search',
                                 json=self.search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()