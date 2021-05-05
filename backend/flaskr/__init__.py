import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from model.models import setup_db, Question, Category
from utils.paginators import paginate_questions


#----------------------------------------------------------------------------#
# APP settings
#----------------------------------------------------------------------------#

def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"/api/*": {"origins": "*"}})

#----------------------------------------------------------------------------#
# APIs
#----------------------------------------------------------------------------#

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
      return response

  @app.route('/')
  def get_greeting():
      return jsonify({'message':'Hello, World!'})
  
  
  @app.route('/categories')
  def categories():
      data = []
      categories = Category.query.all()
      if len(categories) > 0:
        for category in categories:
            data.append({"id": category.id, "type": category.type, "success": True})
        return jsonify(data)
      else:
        abort(404)


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
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    questions = Question.query.all()
    categories = Category.query.order_by(Category.type).all()
    if len(questions) == 0:
      abort(404)
    if page > (len(questions) // 10) +1:
      abort(404)
    else:
      questions_list = paginate_questions(request, questions)
      questions_categories = {}
      categories_list = {category.id: category.type for category in categories}
      return jsonify({
          'success': True,
          'questions': questions_list,
          'total_questions':len(questions),
          'categories': categories_list,
          'current_category': None,
      })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  #TODO test
  @app.route('/questions/<question_id>', methods=['POST'])
  def delete_question(question_id):
    
      try:
          question = Question.query.filter_by(id=question_id).first_or_404()
          question.delete()
          return jsonify({
            'success': True,
            'deleted': question_id,
          })
      except BaseException:
            abort(422)    

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/create', methods=['POST'])
  def create_question():
    error = False
    payload = request.get_json()
    question = Question()
    try:
        question.question = body.get('question', None)
        question.answer = body.get('answer', None)
        question.category = body.get('category', None)
        question.difficulty = body.get('difficulty', None)
        question.insert()
        return jsonify(
          {
            "success": True,
            "body": question
          }
        )
    except BaseException:
              abort(422) 

  '''   
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
      search = request.form.get('search_term', '')
      if search is not None:
        questions = Question.query.filter(Question.question.ilike("%" + search + "%")).all()
        return {
            "success": True,
            "count": len(questions),
            "questions": paginate_questions(request, questions),
        }
      else:
        abort(404)
  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    category = Category.query.filter_by(id=category_id).first_or_404()
    filtered_questions = Question.query.filter_by(category=category_id).all()
    print(category)
    if category is None:
      abort(422)
    elif len(filtered_questions) <= 0:
      abort(404)
    questions = paginate_questions(request, filtered_questions)
    return jsonify({
      "success": True,
      "questions": questions,
      "total_questions": len(questions),
      "current_category": category.type
    })
    

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
  @app.route("/play", methods=['POST'])
  def post_quizzes():
    body = request.get_json()
    previous_questions = body.get("previous_questions", [])
    quiz_category = body.get('quiz_category', None)
    try:
      if quiz_category:
          if quiz_category['id']:
            quiz = Question.query.all()
          else:
            quiz = Question.query.filter(Question.category == quiz_category['id']).all()
      if not quiz:
        return abort(422)
      selected = []
      for question in quiz:
        if len(previous_questions) == 0:
            abort(404)
        else:
            if question.id not in previous_questions:
                selected.append(question.format())
      if len(selected) != 0:
        result = random.choice(selected)
        return jsonify({
          "success": True,
          "question": result
        })
      else:
        return jsonify({
          "success": False
        })
    except BaseException:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "resource not found"
          }), 404
  
  @app.errorhandler(422)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 422,
          "message": "unprocessable"
          }), 422

  @app.errorhandler(405)
  def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

  @app.errorhandler(500)
  def not_allowed(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "server error"
      }), 405

  return app

    