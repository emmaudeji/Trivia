import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
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
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
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

    @app.route('/categories')
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
    ten questions per page and pagination at the bottom of the screen for three pages.
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

    TEST: When you click the trash icon next to a question, the question will be removed.
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
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

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

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app
