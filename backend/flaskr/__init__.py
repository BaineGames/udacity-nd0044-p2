import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def questions_pager(req, sel):
  get_page = req.args.get("page",type=int)
  start_sel = (get_page - 1) * QUESTIONS_PER_PAGE
  end_sel = start_sel + QUESTIONS_PER_PAGE

  format_questions = [question.format() for question in sel]
  return format_questions[start_sel:end_sel]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  #from lesson - enable cors * origin
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  #add the proper headers and methods for request response settings
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods','GET, PUT, POST, PATCH, DELETE, OPTIONS')
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/api/categories")
  def get_categories():
    #get all categories from db and return
    categories = Category.query.all()
    return jsonify({'success': True, 'categories': [db_category.type for db_category in categories]})


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route("/api/questions")
  def get_questions():
    #get all questions first form db
    get_all_questions = Question.query.all() 
    #paginate the questions using utility function
    questions = questions_pager(request, get_all_questions)
    #get all categories first form db
    categories = Category.query.all()
    #start an empty dict to build categories out with keys
    categories_listings = {}

    #fill new dict with proper data for categories
    for individual_category in categories:
      categories_listings[individual_category.id] = individual_category.type
    
    return jsonify({'success': True, 'questions': questions, 'total_questions': len(get_all_questions), 'categories': categories_listings})

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route("/api/questions/<int:q_id>", methods=["DELETE"])
  def del_question(q_id):
    #get the question id from the url and query questions table to get the question wanting to be deleted
    question = Question.query.get(q_id)

    #if the question doesnt exist, 404
    if not question: 
      return abort(404, 'Question does not exist')
    
    #issue the delete of the question and return the deleted ID
    question.delete()
    return jsonify({'deleted':q_id})

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route("/api/questions", methods=["POST"])
  def add_question():
    # get json body of request based on the front end sending it to you with predefined names
    answer = request.json.get("answer")
    category = request.json.get("category")
    difficulty = request.json.get("difficulty")
    question = request.json.get("question")

    # assemble new question with the passed in data
    new_question = Question(question,answer,category,difficulty)
    # insert the new question
    new_question.insert()
    return jsonify(request.json)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route("/api/categories/<int:cate_id>/questions")
  def get_questions_based_on_category(cate_id):

    questions = Question.query.filter_by(Question.category=cate_id).all()

    paginated_questions = questions_pager(request, questions)

    return jsonify({'questions': paginated_questions})



  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    