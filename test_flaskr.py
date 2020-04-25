import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

import app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app.create_app()
        self.client = self.app.test_client
        self.database_path = os.getenv("DATABASE_URL")
        self.quizmaster_token = "Bearer " + os.getenv("QUIZMASTER_TOKEN")
        self.admin_token = "Bearer " + os.getenv("ADMIN_TOKEN")
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        # Remove any test questions added by test cases
        test_entries = Question.query.filter_by(question='Test question')
        for test_entry in test_entries:
            self.client().delete('/questions/' + str(test_entry.id))

    def test_get_paginated_questions(self):
        # test public (unauthenticated) access
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)

        # test quizmaster access
        res = self.client().get('/questions', headers={'Authorization': self.quizmaster_token})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

        # test admin access
        res = self.client().get('/questions', headers={'Authorization': self.admin_token})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_get_categories(self):
        # test public (unauthenticated) access
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['categories']['1'], 'Science')

        # test unallowed method
        mock_data = json.dumps({'category': 'Engineering'})
        res = self.client().post('/categories', data=mock_data,
                                      content_type='application/json')
        self.assertEqual(res.status_code, 405)

    def test_post_new_question(self):
        # Test question, which is deleted by the teardown() function
        mock_data = json.dumps({
            'question': 'Test question',
            'answer': 'Test answer',
            'category': 1,
            'difficulty': 1
        })
        # test public (unauthenticated) access
        num_questions_before = Question.query.count()
        res = self.client().post('/questions', data=mock_data,
                                      content_type='application/json')
        num_questions_after = Question.query.count()

        self.assertEqual(res.status_code, 401)
        self.assertEqual(num_questions_before, num_questions_after)

        # test quizmaster access
        num_questions_before = Question.query.count()
        res = self.client().post('/questions', data=mock_data,
                                      content_type='application/json',
                                      headers={'Authorization': self.quizmaster_token})
        num_questions_after = Question.query.count()

        self.assertEqual(res.status_code, 401)
        self.assertEqual(num_questions_before, num_questions_after)

        # test admin access
        num_questions_before = Question.query.count()
        res = self.client().post('/questions', data=mock_data,
                                      content_type='application/json',
                                      headers={'Authorization': self.admin_token})
        num_questions_after = Question.query.count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(num_questions_before + 1, num_questions_after)

    def test_search(self):
        # Add test question to search for
        test_question = Question(
            question='Test question', answer='Test answer', category=1, difficulty=1)
        test_question.insert()
        # Search term
        mock_data = json.dumps({
            'searchTerm': 'Test'
        })

        # test public (unauthenticated) access
        res = self.client().post('/questions', data=mock_data,
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)

        # test quizmaster access
        res = self.client().post('/questions', data=mock_data,
                                 content_type='application/json',
                                 headers={'Authorization': self.quizmaster_token})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)

        # test admin access
        res = self.client().post('/questions', data=mock_data,
                                 content_type='application/json',
                                 headers={'Authorization': self.admin_token})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        

    def test_categorized_questions(self):
        # test public (unauthenticated) access
        res = self.client().get('/categories/1/questions')
        self.assertEqual(res.status_code, 401)

        # test quizmaster access
        res = self.client().get('/categories/1/questions',
                                headers={'Authorization': self.quizmaster_token})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

        # test admin access
        res = self.client().get('/categories/1/questions',
                                headers={'Authorization': self.admin_token})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])


# Make the tests conveniently executable
if __name__ == "__main__":
    print("Running test cases...")
    unittest.main()
