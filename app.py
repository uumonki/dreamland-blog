from flask import Flask, render_template, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy(app)

ADMIN_EMAILS = os.getenv('ADMIN_EMAILS').split(',')

# Database model
class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(500))

# Database model for authorized users
class AuthorizedVisitor(db.Model):
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

@app.route('/')
def homepage():
    user_email = session.get('user_email')
    
    # Check if user is logged in
    if user_email:
        # Check if user is admin
        if user_email in ADMIN_EMAILS:
            return render_template('admin.html')
        
        # Check if user is in the list of authorized users
        elif AuthorizedVisitor.query.filter_by(email=user_email).first():
            content = Content.query.all()
            html_content = '<br>'.join([c.data for c in content])
            return render_template('loggedin.html', content=html_content)
        
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

# Route to manage authorized users (for simplicity, shown without authentication)
@app.route('/manage-users')
def manage_users():
    # Fetch all authorized users
    users = AuthorizedVisitor.query.all()
    # Render a page to manage users
    # You'll need to create a template 'manage_users.html' for this
    return render_template('manage_users.html', users=users)

# Initialize database
def init_db(app):
    with app.app_context():
        db.create_all()
        # Optionally, add initial authorized users or content

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True)
