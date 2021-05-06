import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from model.models import setup_db, Question, Category
from utils.paginators import paginate_questions

# APP settings


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,DELETE,OPTIONS')
        return response

# APIs

    @app.route('/')
    def get_greeting():
        return jsonify({'message': 'Hello, World!'})

    @app.route('/categories', methods=['GET'])
    def categories():
        data = {}
        categories = Category.query.all()
        if len(categories) > 0:
            for category in categories:
                data[category.id] = category.type
            return jsonify({
                'categories': data,
                'success': True
            })
        else:
            abort(404)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        questions = Question.query.all()
        categories = Category.query.order_by(Category.type).all()
        if len(questions) == 0:
            abort(404)
        if page > (len(questions) // 10) + 1:
            abort(404)
        else:
            questions_list = paginate_questions(request, questions)
            questions_categories = {}
            categories_list = {
                category.id: category.type for category in categories}

            return jsonify({
                'success': True,
                'questions': questions_list,
                'total_questions': len(questions),
                'categories': categories_list,
                'current_category': None,
            })

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

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        question = Question(
            question=body['question'],
            answer=body['answer'],
            difficulty=int(new_difficulty),
            category=int(new_category)
        )
        question.insert()
        return jsonify({
            "success": True
        })

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get('searchTerm', None)
        if search is not None:
            questions = Question.query.\
                filter(Question.question.ilike("%" + search + "%")).all()
            return jsonify({
                "success": True,
                "count": len(questions),
                "questions": paginate_questions(request, questions),
            })
        else:
            abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        category = Category.query.filter_by(id=category_id).first_or_404()
        filtered_questions = Question.query.\
            filter_by(category=category_id).all()
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

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        body = request.get_json()
        category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)
        exist = False
        if category['id'] != 0:
            questions = Question.query.filter_by(category=category['id']).all()
        else:
            questions = Question.query.all()
        random_question = random.choice(questions).format()
        if random_question['id'] in previous_questions:
            exist = True
        while exist:
            if (len(previous_questions) == len(questions)):
                return jsonify({
                    'success': True
                }), 200
        return jsonify({
            'success': True,
            'question': random_question
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
            }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server error"
        }), 500

    return app
