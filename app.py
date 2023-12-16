from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, session, redirect, url_for, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from collections import defaultdict
from datetime import datetime
from functools import wraps

import os

from dotenv import load_dotenv
load_dotenv()

# TODO: requirements.txt

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URI')
)
db = SQLAlchemy(app)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

ADMIN_EMAILS = os.getenv('ADMIN_EMAILS').split(',')
USER_LEVELS = {
    'logged_out': 0,
    'non_user': 1,
    'visitor': 2,
    'admin': 3
}

posts_cache = None

class BlogPost(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    author = db.Column(db.Boolean, nullable=False)
    _date = db.Column('date', db.Date, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    @validates('rating')
    def validate_rating(self, key, rating):
        assert 0 <= rating <= 30
        return rating
    
    @validates('content')
    def validate_content(self, key, content):
        assert content.strip()
        return content
    
    @validates('_date')
    def validate_date(self, key, date):
        if isinstance(date, str):
            return datetime.strptime(date, '%Y-%m-%d').date()
        return date

    @hybrid_property
    def date(self):
        return self._date.strftime('%Y-%m-%d')

    @date.setter
    def date(self, value):
        self._date = datetime.strptime(value, '%Y-%m-%d').date()

    @hybrid_property
    def formatted_date(self):
        formatted = self._date.strftime(f'%b {self._date.day}, %Y').lower()
        return formatted.replace('jun', 'june').replace('jul', 'july').replace('sep', 'sept')

    @hybrid_property
    def side(self):
        return 'left' if not self.author else 'right'

    @classmethod
    def get_organized_posts(cls):
        posts = cls.query.order_by(cls._date.desc()).all()
        organized_posts = defaultdict(lambda: {'date': None, 'left': None, 'right': None})
        for post in posts:
            date_id = post.date.replace('-', '')
            side = post.side
            if organized_posts[date_id][side] is None:
                organized_posts[date_id]['date'] = post.formatted_date
                organized_posts[date_id][side] = post
        return organized_posts


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(256), unique=True, nullable=False, index=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    authorized0 = db.Column(db.Boolean, nullable=False)
    authorized1 = db.Column(db.Boolean, nullable=False)

    @hybrid_property
    def both_authorized(self):
        return self.authorized0 and self.authorized1

# OAuth 2 client setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
)

def get_user(google_id):
    return User.query.filter_by(google_id=google_id).first()

def create_or_update_user(google_id, user_email, user_name):
    if user_name is None:
        user_name = ''
    user = get_user(google_id)
    if user is None:
        user = User(
            google_id=google_id,
            email=user_email,
            name=user_name,
            authorized0=False,
            authorized1=False
        )
        db.session.add(user)
    else:
        user.email = user_email
        user.name = user_name
    db.session.commit()
    return user

def get_user_level():
    user_id = session.get('user_id')
    if user_id is None:
        return USER_LEVELS['logged_out']
    if user_id in ADMIN_EMAILS:
        return USER_LEVELS['admin']
    user = get_user(user_id)
    if user.both_authorized:
        return USER_LEVELS['visitor']
    else:
        return USER_LEVELS['non_user']

def requires_user_level(level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_level = get_user_level()
            if user_level == USER_LEVELS['logged_out']:
                return redirect('/login')
            if user_level < level:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_organized_posts():
    global posts_cache
    if posts_cache is None:
        posts_cache = BlogPost.get_organized_posts()
    return posts_cache

def clear_posts_cache():
    global posts_cache
    posts_cache = None

def render_blog_posts():
    organized_posts = get_organized_posts()
    admin = get_user_level() >= USER_LEVELS['admin']
    return render_template('blog.html', posts=organized_posts, admin=admin)

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data: http://w3.org/2000/svg;"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.route('/')
def homepage():
    user_level = get_user_level()
    if user_level == USER_LEVELS['logged_out']:
        return render_template('login.html')
    elif user_level == USER_LEVELS['non_user']:
        return render_template('non_user.html')
    elif user_level >= USER_LEVELS['visitor']:
        return render_blog_posts()

@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    # TODO: remove select_account after testing
    return google.authorize_redirect(redirect_uri, prompt='select_account')

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    try:
        token = google.authorize_access_token()
        id_info = id_token.verify_oauth2_token(token['id_token'], requests.Request(), GOOGLE_CLIENT_ID)
        session['user_id'] = create_or_update_user(id_info['sub'], id_info['email'], id_info.get('name')).google_id
    except Exception as e:
        # Log the error and inform the user
        print(f"Authentication error: {e}")
        # something like https://idp.shibboleth.ox.ac.uk/idp/profile/SAML2/Redirect/SSO?execution=e1s1
        return render_template('error/auth_error.html'), 400
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/create-post', methods=['GET', 'POST'])
@requires_user_level(USER_LEVELS['admin'])
def create_post():
    if request.method == 'POST':
        data = request.form
        author = ADMIN_EMAILS.index(session['user_id']) != 0
        try:
            new_post = BlogPost(
                author=author,
                rating=int(data.get('rating')),
                content=data.get('text'),
                _date=data.get('date')
                # why isn't date= working??
            )
            clear_posts_cache()
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            print(f"Error creating post: {e}")
            return redirect('/')
    return render_template('admin/create_post.html')

@app.route('/manage-access')
@requires_user_level(USER_LEVELS['admin'])
def manage_access():
    admin_index = ADMIN_EMAILS.index(session['user_id'])

    search_query = request.args.get('search_email', '')
    users = User.query.filter(User.email.contains(search_query)).all()

    return render_template('admin/manage_access.html', users=users, admin_index=admin_index)

@app.route('/update-authorization', methods=['POST'])
@requires_user_level(USER_LEVELS['admin'])
def update_authorization():
    admin_index = ADMIN_EMAILS.index(session['user_id'])

    data = request.json
    user_id = data['userId']
    new_state = data['newState']

    user = User.query.get(user_id)
    if user:
        auth_field = f'authorized{admin_index}'
        setattr(user, auth_field, new_state)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.errorhandler(404)
def not_found(e):
  # TODO: create error pages
  return "404 not found :(", 404

@app.errorhandler(403)
def forbidden(e):
  return "403 forbidden :(", 403

@app.errorhandler(500)
def internal(e):
    return "500 internal server error :(", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
