#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear', methods=['DELETE'])
def clear_session():
    session['page_views'] = None
    session['user_id'] = None
    return {}, 204

@app.route('/articles', methods=['GET'])
def index_article():
    articles = [article.to_dict() for article in Article.query.all()]
    return jsonify(articles), 200

@app.route('/articles/<int:id>', methods=['GET'])
def show_article(id):
    article = Article.query.filter(Article.id == id).first()
    if not session.get('user_id'):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            return jsonify(article.to_dict()), 200

        return {'message': 'Maximum pageview limit reached'}, 401

    return jsonify(article.to_dict()), 200

@app.route('/login', methods=['POST'])
def login():
    username = request.get_json().get('username')
    user = User.query.filter(User.username == username).first()

    if user:
        session['user_id'] = user.id
        return jsonify(user.to_dict()), 200

    return {}, 401

@app.route('/logout', methods=['DELETE'])
def logout():
    session['user_id'] = None
    return {}, 204

@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        return jsonify(user.to_dict()), 200

    return {}, 401

@app.route('/members_only_articles', methods=['GET'])
def member_only_index():
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'Unauthorized access'}, 401

    articles = [article.to_dict() for article in Article.query.filter(Article.is_member_only == True).all()]
    return jsonify(articles), 200

@app.route('/members_only_articles/<int:id>', methods=['GET'])
def member_only_article(id):
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'Unauthorized access'}, 401

    article = Article.query.filter(Article.id == id, Article.is_member_only == True).first()
    if article:
        return jsonify(article.to_dict()), 200
    else:
        return {'error': 'Article not found'}, 404

if __name__ == '__main__':
    app.run(port=5555, debug=True)

