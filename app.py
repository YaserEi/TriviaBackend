import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r'/*/api/*': {'origins': '*'}})


    @app.after_request
    def after_request(response):
        response.headers.add('Access_Control_Allow_Headers', 'Content-Type, Authorization, True')
        response.headers.add('Access_control_Allow_Methods', "GET, POST, PATCH, DELETE, OPTIONS")

        return response

    @app.route('/categories', methods=['GET'])
    def categories():
        cats=Category.query.all()
        formated_cat = [cat.format() for cat in cats]
        all_categories=[]
        for i in range(len(cats)):
            all_categories.append(formated_cat[i]['type'])
        return jsonify({
          'success': True,
          'categories': all_categories
          })



    @app.route('/questions')
    def questions():
        page = request.args.get('page',1,type=int)
        start = (page-1) *10
        end = start +10
        all_categories=[]
        categories = Category.query.all()
        formated_categories = [category.format() for category in categories]
        questions = Question.query.all()
        formated_questions = [question.format() for question in questions]
        totalQuestions = len(formated_questions)
        for i in range(len(categories)):
            all_categories.append(formated_categories[i]['type'])
        return jsonify({
        'success': True,
        'questions': formated_questions[start:end],
        'totalQuestions': totalQuestions,
        'categories': all_categories,
        # 'currentCategory':
        })



    @app.route('/questions/<id>', methods=['DELETE'])
    def delete(id):
       question = Question.query.filter_by(id = id).first()
       if not question:
           abort(422)
       try:
          db.session.delete(question)
          db.session.commit()
       except:
          db.session.rollback()
       finally:
          db.session.close()
          return jsonify({
          'success': True
          })


    @app.route('/questions', methods = ['POST'])
    def add_question():
        body=request.get_json()
        question = body['question']
        answer = body['answer']
        difficulty = body['difficulty']
        category = body['category']


        add_question = Question(question = question, answer = answer, difficulty = difficulty, category = category)

        try:
            db.session.add(add_question)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
            return jsonify({ "success":True})


    @app.route('/questionSearch', methods=['POST'])
    def search():
        body = request.get_json()
        search_result = Question.query.filter(Question.question.ilike('%'+body['searchTerm']+'%')).all()
        total_questions = Question.query.all()
        formated_result = [result.format() for result in search_result]
        return jsonify({
          'success':True,
          'questions': formated_result,
          'totalQuestions': len(total_questions)
          #'currentCategory': categories
        })

    @app.route('/categories/<int:id>/questions', methods = ['GET'])
    def filter_questions(id):
        id +=1
        questions = Question.query.filter_by(category = id).all()
        print(id)
        print(questions)
        formated_questions = [question.format() for question in questions]
        if not questions:
            abort(404)
        return jsonify({
        'success': True,
        'totalQuestions': len(questions),
        'questions': formated_questions
        })


    @app.route('/quizzes', methods = ['POST'])
    def quizzes():
        body = request.get_json()
        print(body["quiz_category"]['id'])
        questions = Question.query.filter_by(category = body["quiz_category"]["id"]).all()
        for i in range(len(body["previous_questions"])):
            if i in questions:
                del questions[i]
        formated_questions = [question.format() for question in questions]
        print(formated_questions)
        quiz_question = random.choice(formated_questions)
        return jsonify({
            "success": True,
            "question": quiz_question
        })

 
  # Create error handlers for all expected errors
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        "success": False,
        "error": 404,
        "message":"resource not found"
        }) , 404
    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
        "success": False,
        "status": 422,
        "message":"resource not found"
        }), 422



    return app
