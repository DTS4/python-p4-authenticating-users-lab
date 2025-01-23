from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Login(Resource):

    def post(self):
        try:
            username = request.get_json()['username']
        except KeyError:
            return jsonify({'message': 'Missing username in request body'}), 400

        user = User.query.filter_by(username=username).first()

        if user:
            session['user_id'] = user.id
            return jsonify(user.to_dict()) 
        else:
            return jsonify({'message': 'Invalid username'}), 401


class Logout(Resource):
    
    def delete(self):
        session.pop('user_id', None)
        return '', 204  


class CheckSession(Resource):
    def get(self):
        try:
            user_id = session.get('user_id')
            if not user_id:
                return {}, 401   

            user = db.session.get(User, user_id)
            if user:
                return user.to_dict(), 200
            else:
                return {}, 404   
        except Exception as e:
            return {'message': 'Internal Server Error'}, 500



class ClearSession(Resource):

    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return jsonify({})


class IndexArticle(Resource):

    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return jsonify(articles)


class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = session.get('page_views', 0) + 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            if article:
                return jsonify(article.to_dict()) 
            else:
                return jsonify({'message': 'Article not found'}), 404

        return jsonify({'message': 'Maximum pageview limit reached'}), 401


api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)