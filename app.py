from flask import Flask, render_template, session, redirect, url_for, request
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy

from collections import defaultdict
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy(app)

ADMIN_EMAILS = os.getenv('ADMIN_EMAILS').split(',')

class BlogPost(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    author = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.Text, nullable=False)  
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

# Database model for authorized users
class AuthorizedVisitor(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

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

def render_blog_posts(user_type):
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

    return render_template('posts.html', posts=organized_posts)

def is_admin():
    return session.get('user_email') in ADMIN_EMAILS

@app.route('/')
def homepage():
    user_email = session.get('user_email')
    
    # Check if user is logged in
    if user_email:
        # Check if user is admin
        if user_email in ADMIN_EMAILS:
            return render_blog_posts('admin')
        
        # Check if user is in the list of authorized users
        elif AuthorizedVisitor.query.filter_by(email=user_email).first():
            return render_blog_posts('visitor')
        
        # User not authorized
        else:
            return render_template('unauthorized.html')

    # User not logged in
    return render_template('login.html')

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
        return redirect(url_for('auth_error'))

    user_info = google.get('userinfo').json()
    session['user_email'] = user_info.get('email')
    return redirect('/')

@app.route('/auth-error')
def auth_error():
    return render_template('auth_error.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect('/')

@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    if not is_admin():
        return render_template('access_denied.html'), 403

    if request.method == 'POST':
        data = request.form
        author = ADMIN_EMAILS.index(session.get('user_email')) != 0
        new_post = BlogPost(
            author=author,
            rating=int(data.get('rating')),
            content=data.get('text'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        )
        db.session.add(new_post)
        db.session.commit()
        print(new_post)
        return redirect('/')

    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('add_post.html', today=today)

# Route to manage authorized users (for simplicity, shown without authentication)
@app.route('/manage-users')
def manage_users():
    # Fetch all authorized users
    users = AuthorizedVisitor.query.all()
    # Render a page to manage users
    # You'll need to create a template 'manage_users.html' for this
    return render_template('manage_users.html', users=users)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
