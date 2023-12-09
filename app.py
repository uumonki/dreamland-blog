from flask import Flask, render_template, session, redirect, url_for, request, jsonify, abort
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

from collections import defaultdict
from datetime import datetime
from functools import wraps
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy(app)

ADMIN_EMAILS = os.getenv('ADMIN_EMAILS').split(',')

USER_LEVELS = {
    'logged_out': 0,
    'non_user': 1,
    'visitor': 2,
    'admin': 3
}

class BlogPost(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    author = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.Text, nullable=False)  
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    @validates('rating')
    def validate_rating(self, key, rating):
        assert 0 <= rating <= 50
        return rating
    
    @validates('content')
    def validate_content(self, key, content):
        assert content.strip()
        return content
    
    @validates('date')
    def validate_date(self, key, date):
        assert datetime.strptime(date, '%Y-%m-%d')
        return date

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    authorized0 = db.Column(db.Boolean, nullable=False)
    authorized1 = db.Column(db.Boolean, nullable=False)

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

def get_or_create_user_in_database(user_email):
    user = User.query.filter_by(email=user_email).first()
    if user is None:
        user = User(email=user_email, authorized0=False, authorized1=False)
        db.session.add(user)
        db.session.commit()
    return user

def get_user_level():
    user_email = session.get('user_email')
    if user_email is None:
        return USER_LEVELS['logged_out']
    user = get_or_create_user_in_database(user_email)
    if user_email in ADMIN_EMAILS:
        return USER_LEVELS['admin']
    if user.authorized0 and user.authorized1:
        return USER_LEVELS['visitor']
    else:
        return USER_LEVELS['non_user']

def requires_user_level(level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_level = get_user_level()
            if user_level < level:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@requires_user_level(USER_LEVELS['visitor'])
def render_blog_posts():
    posts = BlogPost.query.order_by(BlogPost.date.desc()).all()
    
    # Group posts by date
    organized_posts = defaultdict(lambda: {'left': None, 'right': None})
    for post in posts:
        # Formatting the date
        date_obj = datetime.strptime(post.date, '%Y-%m-%d')
        formatted_date = date_obj.strftime(f'%b {date_obj.day}, %Y').lower()
        formatted_date = formatted_date.replace('jun', 'june').replace('jul', 'july').replace('sep', 'sept')

        # Organizing posts by formatted date
        side = 'left' if not post.author else 'right'
        if organized_posts[formatted_date][side] is None:
            post.formatted_date = formatted_date
            organized_posts[formatted_date][side] = post

    admin = get_user_level() >= USER_LEVELS['admin']
    return render_template('blog.html', posts=organized_posts, admin=admin)

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
    return google.authorize_redirect(redirect_uri, prompt='select_account')

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    try:
        token = google.authorize_access_token()
    except Exception as e:
        # Log the error and inform the user
        print(f"Authentication error: {e}")
        # something like https://idp.shibboleth.ox.ac.uk/idp/profile/SAML2/Redirect/SSO?execution=e1s1
        return render_template('error/auth_error.html'), 400

    user_info = google.get('userinfo').json()
    session['user_email'] = user_info.get('email')
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect('/')

@app.route('/create-post', methods=['GET', 'POST'])
@requires_user_level(USER_LEVELS['admin'])
def create_post():
    if request.method == 'POST':
        data = request.form
        author = ADMIN_EMAILS.index(session.get('user_email')) != 0
        try:
            new_post = BlogPost(
                author=author,
                rating=int(data.get('rating')),
                content=data.get('text'),
                date=datetime.strptime(data.get('date'), '%Y-%m-%d').date()
            )
        except Exception as e:
            print(f"Error creating post: {e}")
            return redirect('/')
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')

    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('admin/create_post.html', today=today)

@app.route('/manage-access')
@requires_user_level(USER_LEVELS['admin'])
def manage_access():
    admin_index = ADMIN_EMAILS.index(session.get('user_email'))

    search_query = request.args.get('search_email', '')
    users = User.query.filter(User.email.contains(search_query)).all()

    return render_template('admin/manage_access.html', users=users, admin_index=admin_index)

@app.route('/update-authorization', methods=['POST'])
@requires_user_level(USER_LEVELS['admin'])
def update_authorization():
    admin_index = ADMIN_EMAILS.index(session.get('user_email'))

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
def not_found(e):
  return "403 forbidden :(", 403

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
