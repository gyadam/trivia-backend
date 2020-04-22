import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.exc import SQLAlchemyError

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/questions', methods=['GET', 'POST'])
    def get_post_search_question():
        error = False
        if request.method == 'POST':
            body = request.get_json()
            if 'searchTerm' in body:
                searchterm = body['searchTerm']
                search_results = Question.query.filter(
                    Question.question.ilike('%' + searchterm + '%')).all()
                formatted_results = [result.format()
                                     for result in search_results]
                return jsonify({
                    'success': True,
                    'questions': formatted_results,
                    'totalQuestions': len(formatted_results)
                })
            else:
                quest = body['question']
                ans = body['answer']
                cat = int(body['category'])
                diff = int(body['difficulty'])
                try:
                    new_question = Question(
                        question=quest, answer=ans, category=cat, difficulty=diff)
                    new_question.insert()
                except SQLAlchemyError as e:
                    print(e)
                    error = True
                    abort(422)
                success = False if error else True
                return jsonify({
                    'success': success
                })
        else:
          page = request.args.get('page', 1, type=int)
          start = (page - 1) * 10
          end = start + 10
          questions = Question.query.all()
          formatted_questions = [question.format() for question in questions]
          categories = Category.query.all()
          categories_dict = {
            category.id: category.type for category in categories}
          return jsonify({
            'success': True,
            'questions': formatted_questions[start:end],
            'total_questions': len(formatted_questions),
            'categories': categories_dict
          })

    @app.route('/categories')
    # return all categories
    def get_categories():
        categories = Category.query.all()
        categories_dict = {
            category.id: category.type for category in categories}
        return jsonify({
            'success': True,
            'categories': categories_dict
        }) 

    @app.route('/questions/<int:question_id>', methods=['GET','PATCH','DELETE'])
    def access_question(question_id):
        error = False
        
        if request.method == 'GET':
            try:
                question = Question.query.filter_by(id=question_id).one_or_none().format()
            except:
                error = True
                abort(422)
            success = False if error else True
            return jsonify({
                'question': question,
                'success': success
            })

        elif request.method == 'PATCH':
            quest = body['question']
            ans = body['answer']
            cat = int(body['category'])
            diff = int(body['difficulty'])
            try:
                question = Question.query.filter_by(id=question_id).one_or_none()
                question.update({
                    question = quest,
                    answer = ans,
                    category = cat,
                    difficulty = diff
                })         
            except SQLAlchemyError as e:
                print(e)
                error = True
                abort(422)
            success = False if error else True
            return jsonify({
                'success': success
            })

        elif request.method == 'DELETE':
            try:
                Question.query.filter_by(id=question_id).one_or_none().delete()
            except:
                error = True
                abort(422)
            success = False if error else True
            return jsonify({
                'success': success
            })

    @app.route('/add')
    def get_form():
        return jsonify({
            'success': True,
        })

    @app.route('/categories/<int:category_id>/questions')
    def get_categorized_questions(category_id):
        categorized_questions = Question.query.filter_by(
            category=category_id).all()
        formatted_questions = [question.format()
                               for question in categorized_questions]
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'totalQuestions': len(formatted_questions),
            'currentCategory': category_id
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        print(body)
        category_id = body['quiz_category']['id']
        if category_id == 0:
            categorized_questions = Question.query.all()
        else:
            categorized_questions = Question.query.filter_by(
                category=category_id).all()
        prev_questions = body['previous_questions']
        formatted_questions = [
            q.format() for q in categorized_questions if q.id not in prev_questions]
        random.shuffle(formatted_questions)
        return jsonify({
            'success': True,
            'question': formatted_questions[0] if formatted_questions else None
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    return app

app = create_app()

if __name__ == '__main__':
    app.run()