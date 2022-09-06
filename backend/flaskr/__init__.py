from crypt import methods
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import setup_db, Question, Category

db = SQLAlchemy()

QUESTIONS_PER_PAGE = 10


# paginate questions in a list of 10 per page.
def paginate(request, all_questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in all_questions]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    """

    cors = CORS(app, resource={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Content-Type', 'application/json')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories', methods=['GET'])
    def get_categories():
        '''get all categories'''
        categories = Category.query.all()
        category_dict = {category.id: category.type for category in categories}
        # no categories available, return a 404 error
        if len(category_dict) == 0:
            abort(404)
        # result
        return jsonify({
            'success': True,
            'categories': category_dict
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the
    screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    # Questions end-point
    # returns: all questions
    #          all categories
    @app.route('/questions')
    def get_questions():
        all_questions = Question.query.all()
        # paginate questions in a list of 10 per page.
        formatted_questions = paginate(request, all_questions)
        categories = Category.query.all()
        category_dict = {category.id: category.type for category in categories}

        # no questions are found, abort with a 404 error.
        if len(formatted_questions) == 0:
            abort(404)

        # result
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(all_questions),
            'current_category': "",
            'categories': category_dict
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question
    will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    # Delete end-point
    # returns: deleted question id
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''Delete a question from the database'''
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            # return 404 if question is not available
            if question is None:
                abort(404)

            # result
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            # rollback and close the connection
            db.session.rollback()
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end
    of the last page
    of the questions list in the "List" tab.
    """

    # POST a new question end-point
    # returns: success
    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            # get the new question data from json
            question = Question(
                question=request.get_json()['question'],
                answer=request.get_json()['answer'],
                category=request.get_json()['category'],
                difficulty=request.get_json()['difficulty']
            )
            question.insert()
            db.session.commit()

            return jsonify({
                'success': True,
            })
        except:
            abort(422)
            db.session.rollback()

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    # POST end-point to search for a question in database
    # returns: related search terms
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        '''search for a question in the database'''
        body = request.get_json()
        if not body:
            # posting an envalid json should return a 400 error.
            abort(400)
        if body.get('searchTerm'):
            # searchTerm is available in the request body
            search_term = body.get('searchTerm')
            result_from_search = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            formatted_questions = paginate(request, result_from_search)

            # category_all = Category.query.all()
            # categories = [category.format() for category in category_all]
            # formatted_categories = {
            #     k: v for category in categories for k, v in category.items()}

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'totalQuestions': len(result_from_search),
            'current_category': "",
            # 'categories': formatted_categories
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    # Get the questions based on a category
    @app.route('/categories/<int:category_id>/questions')
    def get_specific_question(category_id):
        # get category by id
        category = Category.query.filter(
            Category.id == category_id).one_or_none()
        # abort with a 404 error if category is unavailable
        if category is None:
            abort(404)
        # get questions in category with id='category_id'
        questions_per_category = Question.query.filter(
            Question.category == category_id).all()
        if len(questions_per_category) == 0:
            abort(404)

        formatted_questions = paginate(request, questions_per_category)

        # format category
        category_dict = {category.id: category.type}

        try:

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(questions_per_category),
                'category': category_id,
                'categoy': category_dict
            })
        except:
            abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    # play quiz game endpoint
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        # load the request body
        body = request.get_json()
        if not body:
            # posting an envalid json should return a 400 error.
            abort(400)
        if (body.get('previous_questions') is None or body.get(
                'quiz_category') is None):
            # if previous_questions or quiz_category are missing,
            # return a 400 error
            abort(400)
        previous_questions = body.get('previous_questions')
        if type(previous_questions) != list:
            # previous_questions should be a list, otherwise return a 400 error
            abort(400)

        category = body.get('quiz_category')
        category_id = int(category['id'])

        # confirm there are questions to be played.
        if category_id == 0:
            # if category id is 0, query the database for a random object
            # of all questions
            selection = Question.query.order_by(func.random())
        else:
            # load a random object of questions from the specified category
            selection = Question.query.filter(
                Question.category == category_id).order_by(func.random())

        if not selection.all():
            # No questions available, abort with a 404 error
            abort(404)
        else:
            # load a random question from our previous query,
            # which is not in the previous_questions list.
            question = selection.filter(Question.id.notin_(
                previous_questions)).first()
        if question is None:
            # all questions were played, returning a success message
            # without a question signifies the end of the game
            return jsonify({
                'success': True
            })

        # Found a question that wasn't played before,
        # let's return it to the user
        return jsonify({
            'success': True,
            'question': question.format()
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    # error handlers

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal error'
        }), 500

    return app
