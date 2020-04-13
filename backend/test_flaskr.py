import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://postgres:password@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.add_new_question_data = {
            "question":"Test Question",
            "answer":"Test Answer",
            "difficulty":"1",
            "category":"1"
        }

        self.category_id_for_testing = 1

        self.search_term = {
            "searchTerm":"title"
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get("/api/categories") #test getting categories
        self.assertEqual(res.status_code,200)
        response = json.loads(res.data)
        self.assertTrue(response['success'])
        self.assertGreater(len(response['categories']), 0)
        pass
    
    def test_get_questions_from_category(self): #test getting questions in a specific category
        res = self.client().get("/api/categories/{}/questions".format(self.category_id_for_testing))
        self.assertEqual(res.status_code,200)
        response = json.loads(res.data)
        self.assertTrue(response['success'])
        self.assertGreater(len(response['questions']), 0)
        pass

    def test_get_questions(self):
        res = self.client().get("/api/questions") #test getting questions
        self.assertEqual(res.status_code,200)
        response = json.loads(res.data)
        self.assertTrue(response['success'])
        self.assertGreater(len(response['questions']), 0)
        pass

    def test_add_question(self):
        res = self.client().post("/api/questions", json=self.add_new_question_data) #test adding a question
        self.assertEqual(res.status_code,200)
        response = json.loads(res.data)
        self.assertTrue(response["success"])
        pass

    def test_delete_question(self):
        get_last_question = Question.query.order_by(Question.id.desc()).limit(1).all()
        question_id = get_last_question[0].id
        res = self.client().delete("/api/questions/{}".format(question_id)) #test deleting a question
        self.assertEqual(res.status_code,200)
        response = json.loads(res.data)
        self.assertTrue(response["success"])
        pass

    def test_search_questions(self):
        res = self.client().post("/api/search-questions", json=self.search_term) #test searching
        self.assertEqual(res.status_code,200)
        response = json.loads(res.data)
        self.assertTrue(response["success"])
        self.assertGreater(len(response['questions']), 0)
        pass

    def test_400(self):
        res = self.client().post("/api/quizzes", content_type='application/json', data="abc") #test malformed data to an endpoint
        self.assertEqual(res.status_code,400)
        pass

    def test_404(self):
        res = self.client().get("/api/cateogriesspelledwrong") #test invalid endpoint
        self.assertEqual(res.status_code,404)
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()