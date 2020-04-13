import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_the_questions(request, selection):
    get_user_requested_page = request.args.get("page", type=int)
    if not get_user_requested_page:
        get_user_requested_page = 1
    starting_question_number = (
        get_user_requested_page - 1) * QUESTIONS_PER_PAGE
    ending_question_number = starting_question_number + QUESTIONS_PER_PAGE

    format_questions = [question.format() for question in selection]
    return format_questions[starting_question_number:ending_question_number]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # from lesson - enable cors * origin
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    # add the proper headers and methods for request response settings
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, PUT, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route("/api/categories")
    def get_categories():
        # get all categories from db and return
        categories = Category.query.all()
        return jsonify({'success': True, 'categories': {
                       db_category.id: db_category.type for db_category in categories}})

    @app.route("/api/questions")
    def get_questions():
        # get all questions first form db
        get_all_questions = Question.query.all()
        # paginate the questions using utility function
        questions = paginate_the_questions(request, get_all_questions)
        # get all categories first form db
        categories = Category.query.all()
        # start an empty dict to build categories out with keys
        categories_listings = {}

        # fill new dict with proper data for categories
        for individual_category in categories:
            categories_listings[individual_category.id] = individual_category.type

        return jsonify({'success': True, 'questions': questions, 'total_questions': len(
            get_all_questions), 'categories': categories_listings})

    @app.route("/api/questions/<int:q_id>", methods=["DELETE"])
    def del_question(q_id):
        # get the question id from the url and query questions table to get the
        # question wanting to be deleted
        question = Question.query.get(q_id)

        # if the question doesnt exist, 404
        if not question:
            return abort(404, 'Question does not exist')

        # issue the delete of the question and return the deleted ID
        question.delete()
        return jsonify({'success': True, 'deleted': q_id})

    @app.route("/api/questions", methods=["POST"])
    def add_question():
        # get json body of request based on the front end sending it to you
        # with predefined names
        ans = request.json.get("answer")
        cate = request.json.get("category")
        diff = request.json.get("difficulty")
        q = request.json.get("question")
        # assemble new question with the passed in data
        new_question = Question(q, ans, cate, diff)
        # insert the new question
        new_question.insert()
        return jsonify(
            {"success": True, "last_inserted_id": new_question.format()["id"]})

    @app.route("/api/search-questions", methods=["POST"])
    def search_questions():
        # grab term to be searched from request
        get_search_term = request.json.get("searchTerm")
        # format search term to be wild card based
        search_term = "%{}%".format(get_search_term)
        # return paginated results of the search term
        return jsonify({'success': True, 'questions': paginate_the_questions(
            request, Question.query.filter(Question.question.ilike(search_term)).all())})

    @app.route("/api/categories/<int:requested_category_id>/questions")
    def get_questions_based_on_category(requested_category_id):

        return jsonify({'success': True, 'questions': paginate_the_questions(
            request, Question.query.filter_by(category=requested_category_id).all())})

    @app.route("/api/quizzes", methods=["POST"])
    def build_quiz():
        # get category to use from args
        quiz_category = request.json.get("quiz_category")["id"]
        answered_questions = request.json.get("previous_questions")

        if quiz_category != 0:
            quiz_question_bank = Question.query.filter(
                Question.id.notin_(answered_questions)).filter_by(
                category=quiz_category).order_by(
                func.random()).limit(1).all()

        if quiz_category == 0:
            quiz_question_bank = Question.query.filter(
                Question.id.notin_(answered_questions)).order_by(
                func.random()).limit(1).all()

        if len(quiz_question_bank) > 0:
            formatted_question = quiz_question_bank[0].format()

        if len(quiz_question_bank) == 0:
            formatted_question = ""

        return jsonify({"question": formatted_question})

    @app.errorhandler(404)
    def throw_not_found(error):
        return jsonify({
            "error": 404
        }), 404

    @app.errorhandler(400)
    def throw_not_found(error):
        return jsonify({
            "error": 400
        }), 400

    @app.errorhandler(504)
    def throw_not_found(error):
        return jsonify({
            "error": "Gateway Timeout"
        }), 504

    return app
